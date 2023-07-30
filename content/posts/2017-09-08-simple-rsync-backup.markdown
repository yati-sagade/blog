---
date: 2017-09-08

layout: post

title: A simple backup setup using rsync

categories: notes


---

Suppose we have a bunch of files we'd like to have backed up on a remote host
periodically. In this post, I'll describe my setup that uses [rsync][1] with
cron.

## Remote host setup

First we'll need a place to back up to. I also have a Digital Ocean box, whose
IP address is known to me. Any remote box with sufficient disk space would do:
all we need is a way to access it. I have an entry for my remote box in the
`/etc/hosts` file (I call it "dome"):

```bash

# /etc/hosts
...
xx.xx.xx.xx dome

```

On this box, I have a `~/backup/` directory, which will where all the backed
up files from my local box will land.

For security, I an ssh key added to the remote box to let it identify
connections from my local box. To do this, first generate a keypair if you
haven't:

```bash

$ ssh-keygen

```

Now make note of the public key (found in e.g., `~/.ssh/id_rsa.pub`) and
ssh to the remote host (using, say, a password). Then, edit the file
`~/.ssh/authorized_keys` **on the remote host** and paste your full public
key in there. That's it. To test if this worked, try sshing again to the remote
host. This time, it should not ask for a password (of course, if your usernames
on local and remote differ, you'll have to `ssh remote_username@remote_host`).

## Local setup

I maintain the list of files to be backed up in a file, `~/backup.txt`, which
lists a path _relative to my home directory_ per line. The rules are:

- Files are copied normally.
- Symlinks are traversed and their referrents are copied.
- Directories, when listed without a trailing slash, are copied recursively and
end up on the backup server with the toplevel directory intact.
- Directories, when list *with* a trailing slash, have their *contents copied*
out into the remote backup directory.

e.g., 

```
notes.org
Documents
Projects
Bak/

```

will backup `~/notes.org`, `~/Documents` and `~/Projects` (the latter two being
directories) to `~/backup/notes.org`, `~/backup/Documents`, `~/backup/Projects`,
respectively. However, the _contents of_ `~/Bak` are copied directly to
`~/backup`.


## rsync

The `rsync` command is pretty simple:

```bash

$ rsync \
    -avz \                          # copy in [a]rchive mode, [v]erbose, compressed.
    --files-from=~/backup.txt \     # our file list.
    $HOME \                         # this is prefixed to every path in the file.
    ys@dome:~/backup                # remote path

```

## Scheduling backups

I have an hourly cronjob that runs the above command. To set it up, do

```bash

$ crontab -e

```

and then add the following line:

```cron

0 * * * *  rsync -az --files-from=/home/ys/backup.txt /home/ys ys@dome:~/backup

```
and exit. Whenever a new path is added to the backup list, the next run of
our cronjob will copy it over to the remote. For existing files, rsync only
sends the deltas.

[1]: https://rsync.samba.org/
