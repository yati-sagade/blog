---
title: Writing video captured using OpenCV to a file
layout: post
date: 2016-11-06
tags: ["opencv"]

---
This approach requires [ffmpeg][1] (forked to [avconv][2] on Debian), and is not
really limited to OpenCV. If you can write raw video frames to stdout, you can
use this method. OpenCV video frames are represented as numpy arrays in Python,
and the `.tostring()` method will give the raw frame data that can be piped to
ffmpeg. Here is a small program that captures the first video stream and pipes
it to ffmpeg to make a video output file called `ouput.avi`.

```python
from __future__ import print_function
import os
import sys
import cv2
import subprocess as sp
import numpy as np
import atexit


show_preview = True


preview_wnd = "preview"


FFMPEG = "/usr/bin/ffmpeg" # change to avconv on Debian


command = [
    FFMPEG,
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-s", "640x480", 
    "-r", "30",         # 30 fps
    "-i", "-",          # Read from piped stdin
    "-an",              # No audio
    "-f", "avi",        # output format
    "-r", "30",         # output fps
    "output.avi",
]


def close_proc(proc):
    print("cleanly exiting {}".format(FFMPEG))
    proc.stdin.close()
    if proc.stderr is not None:
        proc.stderr.close()
    proc.wait()


if __name__ == "__main__":
    print("Control-C to exit.")
    proc = sp.Popen(command, stdin=sp.PIPE)
    atexit.register(lambda: close_proc(proc))

    cap = cv2.VideoCapture(0)

    if show_preview:
        cv2.namedWindow(preview_wnd, cv2.WINDOW_NORMAL)

    while True:
        flag, frame = cap.read()
        if not flag or frame is None:
            break

        if show_preview:
            cv2.imshow(preview_wnd, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        proc.stdin.write(frame.tostring())
```

Note that this ffmpeg incantation will quit if the output file already exists.
If overwriting is desired behaviour, include the `-y` option.


[1]:https://www.ffmpeg.org/
[2]:https://libav.org/avconv.html
