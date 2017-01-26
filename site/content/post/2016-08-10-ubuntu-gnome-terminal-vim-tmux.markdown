+++
author = "karlgrz"
comments = true
date = "2016-08-10T08:00:00"
slug = "ubuntu-gnome-terminal-vim-tmux"
title = "Ubuntu gnome-terminal vim / tmux settings to preserve colors and shortcuts"
categories = ["Coding"]
tags = ["2016", "ubuntu", "vim", "tmux"]
+++

Recently, I've been using vim within tmux for a lot of my development. It's been a very good experience on Ubuntu 16.04 in gnome-terminal. However, the colors were not identical within tmux as they are in standalone vim. Obviously, this really bothers you after a while. Well, not a while. Pretty much immediately, haha. But I put up with it to forego shaving that yak in order to actually get shit done™.

Finally got the shears out and DID shave that yak :-) These settings added to the appropriate files listed give me identical colors both inside and outside of tmux sessions in vim, and my eyes can go back to not twitching as I hit that escape key.

This is all that's in my `~/.tmux.conf`, this is necessary to preserve Ctrl+<arrow> and Shift+<arrow> navigation shortcuts of vim within tmux session:

```
set-option -g xterm-keys on
```

I had to add this to my `~/.bashrc` (note the lack of " surrounding the value. I originally had `"xterm-256color"` but that was part of my initial problems. tmux did not like that):

```
export TERM=xterm-256color
```

Finally, these lines all were added to the top of my `~/.vimrc`:

```
set t_Co=256
set t_ut=
set background=dark
```

Now everything looks good again!