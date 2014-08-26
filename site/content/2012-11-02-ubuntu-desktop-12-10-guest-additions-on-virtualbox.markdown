author: karlgrz 
comments: true
date: 2012-11-02 23:30:24
slug: ubuntu-desktop-12-10-guest-additions-on-virtualbox
title: Ubuntu Desktop 12.10 Guest Additions on Virtualbox
category: Coding
tags: ubuntu, virtualbox

I had the unfortunate annoyance of trying to get Ubuntu Desktop 12.10 Guest Additions working on VirtualBox 4.24, which have a strong desire to NOT install linux kernel headers. Here's the steps. Don't be annoyed. I hope this finds you quickly.

I'm like you. I like my VM to scale when I change dimensions of the window, I like to copy/paste between the host/guest, and I expect that to work. Out of the box, it doesn't. I assume this will be fixed shortly, but in the meantime, do this and you'll be good to go.

For what it's worth, I'm on Windows 7 64-bit Ultimate host, with the newest Ubuntu Desktop 12.10 .iso from ubuntu.com installed onto VirtualBox 4.24.r81684.

- DO NOT INSTALL GUEST ADDITIONS UNTIL THE END. You can do it now, if you want, but it's just going to be pointless and cause you pain. If you have already installed them, uninstall them either from VBoxLinuxAdditions.run and uninstall from the mounted disc or if you installed from apt-get, just run the 

```
sudo apt-get remove virtualbox-guest-additions 
``` 

from terminal and be done with it.

This command makes your Guest Additions install so happy it actually succeeds:

```
sudo apt-get install linux-headers-generic
``` 

Run that in a terminal. That's it.

Now, shut down the VM and restart it. When it boots back up, in the VirtualBox guest window click on Devices -> Install Guest Additions and follow the prompts. This should succeed. 

Shut down the VM and restart, and your VirtualBox VM should resize dynamically like you're used to, and be able to copy/paste between host and guest and vice versa.

Something funky is going on with xserver and the way the dependencies are resolving during Ubuntu 12.10 installation. I'm sure this will get smoothed out (it is pretty recent release) but still annoying.

Enjoy.
