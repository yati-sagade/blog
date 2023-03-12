---
date: 2022-03-12
layout: post
title: Remapping delete to escape on Arch Linux
---

This will work for X based installations, and not just for the Del key.
KDE/Gnome usually have tools to remap a fixed set of keys to escape (e.g., Caps
Lock), but I could not find a setting in KDE for Del -> Esc.

First, use `xev` to figure out what the hex keySym is for your Del key. In my
case it showed `0xffff`, but turned out that was not it. I did:

```
$ xmodmap -pk |grep -i delete
91         0xff9f (KP_Delete)      0xffae (KP_Decimal)     0xff9f (KP_Delete)      0xffae (KP_Decimal)
```

And used `0xff9f` as the keySym code. The remapping is easy:

```
$ xmodmap -e "keysym 0xff9f = Escape"
```

After testing it works, best to stick it in your `~/.profile`.

If you use VS Code, if [a bug with remapped keys on Code running on
X](https://github.com/microsoft/vscode/issues/23991) hasn't been resolved yet,
you will want to add:

```
"keyboard.dispatch": "keyCode"
```

to your settings.json.


