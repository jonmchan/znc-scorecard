znc-scorecard
=============

ZNC python module to keep a scorecard of +1's and -1's with friends.


Usage
=============

Usage is simple - to +1 something, simple type:

    nick, +1

To -1 something, type:

    nick, -1

You can +1 or -1 any word. It will pick up anybody's +1 or -1 in any
channel. Each channel will have their own unique list of +1's and -1's.


To display the score of the +1's/-1's, type:

    !score

The score will be displayed in the channel and you will see the score in
\*scorecard.

You can reset the score with the reset command, but only the owner can
send this command.

    !reset_score


Requirements
=============
* znc irc proxy >= 1.0 built with python support


Installation
=============
Download this repo.

Copy mailonmsg.py to your znc plugins directory.


From within your IRC client connected through znc proxy:

   /znc loadmodule modpython

   /znc loadmodule scorecard

