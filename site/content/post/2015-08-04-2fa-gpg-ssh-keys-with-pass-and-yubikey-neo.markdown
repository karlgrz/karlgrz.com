+++
author = "karlgrz"
comments = true
date = "2015-08-04T09:00:00"
slug = "2fa-gpg-ssh-keys-with-pass-and-yubikey-neo"
title = "2 Factor Authentication GPG & SSH keys with pass and Yubikey NEO"
categories = ["Coding"]
tags = ["2015", "gpg", "ssh", "encryption", "yubikey", "2fa", "pass", "password-management"]
+++

## In the beginning...

For the past few years I've used [KeePass](http://keepass.info/) as my password management solution, both for personal and work related credentials. It's a great product. When I moved from PC to OS X and eventually Linux I used [KeepassX](https://www.keepassx.org/) and the Android client, [KeePassDroid](http://www.keepassdroid.com/), with great success. I stored my .kdbx database in DropBox for easy syncing between my many machines and devices. I felt comfortable with the security and usability at the time.

## Bombshell

After reading through [this thread](https://news.ycombinator.com/item?id=9727297) a little over a month ago I grew a bit skeptical and started to look at alternatives.

## Meditate on this...

This led me to what I will affectionately call a "deep dive into the wormhole" that is [PGP encryption](https://en.wikipedia.org/wiki/Pretty_Good_Privacy) and, also, [GNU Privacy Guard, or GPG](https://en.wikipedia.org/wiki/GNU_Privacy_Guard). Having used it extensively in practice but not really diving deep before, I was excited to give myself a good reason to research the topic. When I actually tried to generate my own key pair following best practices I realized that there were a lot of things I was not familiar with. I attribute this both to not practicing these techniques as often as other programming paradigms and also my ignorance in the area.

After my research I knew that I wanted a few things from my next solution. I wanted a tool that would leverage an existing GPG keychain. I didn't want to rely on something else generating keys for me, as I wanted to create my own and manage them myself so I could reasonably confirm that the keys were generated in a sound manner. I wanted authentication, encryption, and signing subkeys for daily use on all my devices while my private master key pair could be stored offline in an airgapped USB key. I also really wanted some kind of 2 Factor Authentication.

In the end, I found a solution that fits all my criteria and I have been very happy with it thus far.

## pass

When I read that HN thread I was introduced to a little tool called [pass](http://passwordstore.org/), which is a password management tool following the [Unix philosophy](http://en.wikipedia.org/wiki/Unix_philosophy). Behind the scenes it is essentially a wrapper around gpg (or gpg2) and git, and it works very well. After a little research I was sold. It has a functional Android client ([Password Store](https://github.com/zeapo/Android-Password-Store) which also relies on [OpenKeychain](http://www.openkeychain.org)), and a functional native client ([QtPass](https://github.com/IJHack/qtpass)) for most OS's, so if I did decide I needed to use this in a VM or a different platform in the future I should be covered.

## GPG
I won't regurgitate the key generation process here, as I feel others have already done this exceptionally well. I will just link to the resources I used to generate my key pair:

- [https://alexcabal.com/creating-the-perfect-gpg-keypair/](https://alexcabal.com/creating-the-perfect-gpg-keypair/) (this is the one I followed very closely)
- [https://www.esev.com/blog/post/2015-01-pgp-ssh-key-on-yubikey-neo/](https://www.esev.com/blog/post/2015-01-pgp-ssh-key-on-yubikey-neo/)
- [https://drupalwatchdog.com/blog/2015/6/yubikey-neo-and-better-password-manager-pass](https://drupalwatchdog.com/blog/2015/6/yubikey-neo-and-better-password-manager-pass)
- [http://blog.josefsson.org/2014/06/23/offline-gnupg-master-key-and-subkeys-on-yubikey-neo-smartcard/](http://blog.josefsson.org/2014/06/23/offline-gnupg-master-key-and-subkeys-on-yubikey-neo-smartcard/)

For the most part, I had a smooth time generating my key pair. I did everything very, very slowly so I understood every step of the way, so ultimately it took an incredibly long time. There is _so_ much information online about this stuff buried in forum posts and github issues. These 4 posts captured nearly everything I needed to know about creating a nice key pair that I feel is reasonably private and secure.

## Enter the Yubikey

You'll notice some of those posts reference [Yubikey NEO](https://www.yubico.com/products/yubikey-hardware/yubikey-neo/), which I started seeing a lot in my research. I ended up purchasing one and am pleased with the results. Essentially, a Yubikey is a hardware token for strong 2 factor authentication. It operates much like a smartcard, but has a few other interesting features that ended up fitting in perfectly with how I wanted my workflow to be.

The [Yubikey NEO](https://www.yubico.com/products/yubikey-hardware/yubikey-neo/) offers both contact (USB) and contactless (NFC) communications, so I can use one single device with both my laptop and my phone. Beautiful.

## Oops

Those posts above cover almost everything you need to get started, but I ran into a couple of issues, probably due to my own ignorance more than anything, but I feel like they might trip up someone else so I wanted to document them somewhere.

When working with the Yubikey NEO, [this forum post](http://forum.yubico.com/viewtopic.php?f=26&t=1171) answered all the questions I had regarding getting my subkeys on to the NEO itself.

One thing that didn't work well was setting GNUPGHOME directly to the USB drive housing my airgapped private key pair in the VM I was using to export to the NEO. I had to copy the folder to the VM (which I questioned at first but in the end, it's an airgapped VM and I conceded that it was reasonably secure for me, but use your own discretion). I tried setting the permissions differently on the key, but the only thing that worked properly was copying directly to the VM. After that I was able to export the keys to the NEO no problem and shred the VM.

## 4096 v. 2048

When I first generated my key pair I made the subkeys all 4096 bit, thinking that "moar datas" has to be better. Practically speaking, that is the truth. However, Yubikey NEO only supports subkeys up to 2048 bit, which, [after](https://www.yubico.com/2015/02/big-debate-2048-4096-yubicos-stand/) [some](http://danielpocock.com/rsa-key-sizes-2048-or-4096-bits) [research](http://security.stackexchange.com/questions/65174/4096-bit-rsa-encryption-keys-vs-2048), isn't a huge deal depending on who you ask, and 2048 bit seems to be sufficient for me. Considering my private master key pair is 4096 bit, when a Yubikey _does_ support 4096 bit subkeys, I should be set without having to generate a new master private key pair.

## gnome-keyring

Another thing that was annoying was gnome-keyring was interfering with the interaction between Yubikey NEO pin caching on pass CLI and QtPass. gnome-keyring is enabled by default on Ubuntu 15.04.

After a bit of research, I [opened an issue](https://github.com/IJHack/qtpass/issues/73) thinking it was a bug. I'd like to take a moment now to give a shout out to [Anne Jan Brouwer](https://twitter.com/annejanbrouwer) and his responsiveness to issues and pull requests (he is active maintainer of QtPass). Every interaction I had with him gave me further confidence that this was the right solution for me. Thank you, good sir!

In the end, my problem was solved by a couple simple steps. First, I had to add a gpg-agent.conf to my ~/.gnupg folder with the following contents:

```
enable-ssh-support
write-env-file
use-standard-socket
default-cache-ttl 600
max-cache-ttl 7200
```

Also, I had to turn off gnome-keyring and add this to my .bashrc:

``` bash
# OpenPGP applet support for YubiKey NEO
if [ ! -f /tmp/gpg-agent.env ]; then
    killall gpg-agent;
        eval $(gpg-agent --daemon --enable-ssh-support > /tmp/gpg-agent.env);
fi
. /tmp/gpg-agent.env
```

This seems to be a bit more straight forward on OS X. "Linux UX is rough?" Pfft :-)

## Re-encrypt

The last thing that was not very clear is when you generate new subkeys you need to re-init your pass repo with the new encryption subkey. For example, let's assume the master private key pair has been stored away and we are on our development laptop. Let's say this is the output of `gpg --list-secret-keys`:

```
karl@deathstar:~$ gpg --list-secret-keys
/home/karl/.gnupg/secring.gpg
-----------------------------
sec#  4096R/ABCDEFGH 2015-01-01
uid                  Karl Grzeszczak <karl@karlgrz.com>
ssb   4096R/01234567 2015-01-01
ssb   4096R/76543210 2015-01-01
ssb>  2048R/00000000 2015-05-01
ssb>  2048R/11111111 2015-05-01
ssb>  2048R/22222222 2015-05-01
```

This shows that my private master key pair (generated on 2015-01-01) is __NOT__ on my laptop (sec# means your secret key is not on the current keychain, since I left it on the airgapped USB drive). This means if my laptop was stolen, I could revoke all those subkeys, generate new ones with my master private key pair, and then re-publish the new keys to key servers.

It also shows that I had 2, 4096 bit subkeys generated on 2015-01-01, and 3, 2048 bit subkeys generated on 2015-05-01 that are stubs (the actual private key resides on a smartcard, in this case the Yubikey NEO).

What this doesn't show is that the 2, 4096 bit subkeys were revoked and they were the keys used to originally create my pass entries. At first I was trying to whip up a quick script to re-encrypt my entries, but pass already has an easy mechanism to do this, like so:

```
pass init <new-gpg-id>
```

In this example, my encryption subkey is 11111111, and I would run this:

```
pass init 11111111
```

This iterates every entry and re-encrypts it with your new subkey. Awesome!

## ssh

Lastly, something I never realized before all this is that you can use a GPG authentication subkey as an SSH key for servers or source control or wherever an SSH key would be used. This has a fantastic side effect of bestowing hardware 2 factor authentication upon my SSH key. It is simple to do once you have all your keys exported to the Yubikey NEO. To get the public key for your GPG authentication subkey you run the following command:

```
gpgkey2ssh <id-of-authentication-subkey>
```

So in my case, my authentication subkey in the previous example was 22222222, so I'd run:

```
gpgkey2ssh 22222222
```

The output is the public SSH key, which you can paste into github, bitbucket, or the authorized_keys file on your server. Having to type my Yubikey NEO PIN one time every time it is inserted for SSH is a mighty fine compromise for the hardware two factor authentication.

## Commentary

There exists services like [keybase.io](https://keybase.io) which is a great thing. They are trying to take a very complex set of operations and make it more accessible, which I think is fantastic. This stuff needs to be __MUCH__ simpler in order to gain a wider adoption. Right now, the state of world is clear: it's just not ready for mainstream consumption.

I am not a member of a government agency, or a security professional, or someone dealing with health care numbers on a day to day basis. I'm just a software engineer, but I do work with lots of things that for one reason or another should be private. It is nice to see an entire community of people that have the same goals and ideals behind encryption and keeping data private that I do. Having followed these procedures, you should be reasonably confident that you have done a good job in protecting your encryption keys and the data you are encrypting with them. It's a shame there are so many agencies, governments, and private companies trying to put backdoors into the very same encryption tools  that protect them as well. One day these techniques will be outdated and, possibly, easily hacked or brute forced. Hopefully, by then, we will have better options for protecting our data. But we need something _right now_, and this feels like the best way currently.

Here's the opinion I formed for myself after this exercise. We need a new approach. There has to be a better way to do this. I don't know what that is, but I want something better. The tools we have right now leave a lot to be desired. They're functional, but they are not "usable." I think if we (the community) spent a bit more resources on smoothing out the rough edges then there would be wider adoption of these tools.

In order to be a standard, people have to use it. In order to get people to use it, there has to be a standard. In order to be a standard...

I read a great quote by [Moxie Marlinspike](http://www.thoughtcrime.org/blog/gpg-and-me/) about GPG:

> In the 1990s, I was excited about the future, and I dreamed of a world where everyone would install GPG. Now I’m still excited about the future, but I dream of a world where I can uninstall it.

I like GPG, but I also want something better.

I'd love to hear your own ideas about this stuff, as well as how I can improve the techniques I have described here. This has been a fascinating learning exercise, and I feel like I've only scratched the surface.