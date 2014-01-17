#!/usr/bin/env python
# vim: set sw=4 sts=4 tw=0 : #

# scorecard.py

import sys
import re
import traceback
import znc
import time




## decorators borrowed from mailonmsg.py module - thanks Sean Dague <sean@dague.net>
def _is_self(*args):
    """Utility method to make sure only calling on right modules."""
    if len(args) > 1 and type(args[0]) == scorecard:
        return args[0]
    return None

def trace(fn):
    """Useful decorator for debugging."""
    def wrapper(*args, **kwargs):
        s = _is_self(*args)
        if s:
            s.PutModule("TRACE: %s" % (fn.__name__))
        return fn(*args, **kwargs)
    return wrapper

def catchfail(fn):
    """Catch exceptions and get them onto the module channel."""
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            s = _is_self(*args)
            if s:
                s.PutModule("Failed with %s" % (e))
                # then get the whole stack trace out
                lines = traceback.format_exception(exc_type, exc_value,
                                                   exc_traceback)
                for line in lines:
                    s.PutModule(line)
    return wrapper

class scorecard(znc.Module):
    description = "Scorecard - keeps tracks of +1's and -1's for each channel"


    # score is score = { channel : { nick : 5} }
    scores = {}

    # regex search terms
    plusOneRE = re.compile(r"^(\w+), \+1")
    minusOneRE = re.compile(r"^(\w+), -1")

    def OnLoad(self, args,msg):
        saved_scores=self.GetNV('scores')
        #self.PutModule("we loaded. "+saved_scores)
        if saved_scores:
            self.scores=eval(saved_scores)

        return znc.CONTINUE

    @catchfail
    def OnChanMsg(self, nick, channel, msg):
        if (msg.s == "!score"):
            self.PutIRC("PRIVMSG "+channel.GetName()+" :"+self.getScore(channel.GetName()))
            self.PutModule(self.getScore(channel.GetName()))
        else:
            self.processMsgForScore(channel.GetName(),msg.s)

        #self.PutModule("Hey, {0} said {1} on {2}".format(nick.GetNick(), msg.s, channel.GetName()))

        return znc.CONTINUE

    @catchfail
    def OnUserMsg(self, target, msg):
        if msg.s == "!score":
            self.PutIRC("PRIVMSG "+target.s+" :" + msg.s)
            self.PutIRC("PRIVMSG "+target.s+" :"+self.getScore(target.s))
            self.PutModule(self.getScore(target.s))
            return znc.HALTCORE
        elif msg.s == "!reset_score":
            if target.s in self.scores:
                del self.scores[target.s]
            self.SetNV('scores',str(self.scores), True)
        else:
            self.processMsgForScore(target.s,msg.s)
            return znc.CONTINUE

    @catchfail
    def getScore(self, channel):
        ret_string=""
        if channel in self.scores:
            for name,score in self.scores[channel].items():
                ret_string+=name + " = " + str(score) + ", "
            return ret_string.rstrip(', ')
        else:
            return "No score has been set for "+channel+" yet."

    @catchfail
    def processMsgForScore(self,channel,msg):
        m=self.plusOneRE.match(msg)
        if m:
            obj=m.group(1)
            if channel not in self.scores:
                self.scores[channel]= {}

            if obj not in self.scores[channel]:
                self.scores[channel][obj]=0

            self.scores[channel][obj]+=1
            self.SetNV('scores',str(self.scores), True)


        m=self.minusOneRE.match(msg)
        if m:
            obj=m.group(1)
            if channel not in self.scores:
                self.scores[channel]= {}

            if obj not in self.scores[channel]:
                self.scores[channel][obj]=0

            self.scores[channel][obj]-=1
            self.SetNV('scores',str(self.scores),True)
