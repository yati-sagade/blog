---
title: Killing a process group with a timeout in bash
layout: post
date: 2017-07-01
tags: ["linux", "bash"]

---

On Linux, most programs that daemonize write their process number to a file,
which can be used to send signals to the daemon. To automate deployment (in case
you already do not have upstart or systemd integration with the program in
question), here's one approach to stop a daemon with potentially many child
processes:

- Send `SIGTERM` to the parent process id (known via, say, a file written to by
  the program while daemonizing).
- Wait for some time so the process can handle the signal (e.g., by cleaning up
  its children and any other resources), while checking if the process has
  exited.
- If the process exited before timeout, all good, otherwise, send `SIGKILL` to
  the parent process' process group. `SIGKILL` might be a bit extreme, and maybe
  you want to try `SIGINT` first, but for this post, we'll just send `SIGKILL`.

Here's the implementation in bash:

```bash
#!/bin/sh

TIMEOUT=30 # seconds
TARGET_PID=$1

if ! kill -0 $TARGET_PID 2>/dev/null; then
    echo "Process $TARGET_PID either does not exist,\
          or you are not allowed to send signals to it"
    exit 1
fi

kill $TARGET_PID 2>/dev/null

STARTED_AT=$(date +"%s") # current UNIX timestamp
# $((...)) means evaluation in arithmetic context
TO_END_AT=$(($STARTED_AT + $TIMEOUT))

while true; do

    # See below, "sending" a 0 does not actually send anything, but performs
    # error-checking, and allows us to know if the process is still alive.
    kill -0 $TARGET_PID 2>/dev/null

    if ! kill -0 $TARGET_PID 2>/dev/null; then
        echo "Process exited"
        break
    fi

    sleep 1

    if [ $(date +"%s") -gt $TO_END_AT ]; then
        echo "Timeout reached"
        break
    fi

done

if kill -0 $TARGET_PID 2>/dev/null; then
    PGID=$(ps --no-header -o '%r' $TARGET_PID)
    echo "Killing pgid $PGID"
    # To kill the entire pgroup, we must send the _negation_ of the process
    # group id to kill(1)
    kill -9 $((-$PGID)) 
fi
```

`kill(1)` allows us to check the status of a process by sending it the 0 signal,
which doesn't actually send anything to the target process, but does all the
error checking a `kill` invocation normally would. This includes checking if we
are allowed to send signals to the process in question, and the process is
running at all.

