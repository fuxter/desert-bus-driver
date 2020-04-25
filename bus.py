#! /usr/bin/env python
"""
* get window dimensions by name (xprop & xwininfo)
* grab screen with dimensions (mss)
* get to the line
    * (debug) paint pixel green (PIL)
    * (debug) show grab (PIL)
* if color yellow send keystroke to window (xdotool)
"""

import sys
import subprocess
import time
from mss import mss
from PIL import Image


YELLOW = (239, 207, 66)


def main():
    name = sys.argv[1]
    m = mss()
    info = subprocess.Popen(["xwininfo", "-name", name], stdout=subprocess.PIPE).communicate()[0].splitlines()
    x = int(info[3].split()[-1])
    y = int(info[4].split()[-1])
    w = int(info[7].split()[-1])
    h = int(info[8].split()[-1])
    wid = subprocess.Popen(["xdotool", "search", "--name", name], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
    xdotool = subprocess.Popen(["xdotool", "-"], stdin=subprocess.PIPE)

    # focus, unpause, press a
    xdotool.stdin.write(f'search --name "{name}"\n'.encode())
    xdotool.stdin.write(b"windowfocus\n")
    xdotool.stdin.write(b"key p\n")
    xdotool.stdin.flush()
    while True:
        left = False
        focused = wid == subprocess.Popen(["xdotool", "getwindowfocus"], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
        if not focused:
            xdotool.stdin.write(b"keyup a\n")
            time.sleep(1)
            continue

        # grab data
        grab = m.grab({'left': x, 'top': y, 'width': w, 'height': h})
        middle = int(w / 100 * 38)  # point to keep the road line on
        center = int(h / 100 * 58)
        for xx in range(grab.width):
            for yy in range(grab.height):
                if yy == center:
                    if grab.pixel(xx, yy) == YELLOW:
                        if xx < middle:
                            left = True
                        continue

        if left:
            print('turn left')
            xdotool.stdin.write(b"keydown Left\n")
        xdotool.stdin.write(b"keydown a\n")
        xdotool.stdin.flush()
        time.sleep(.1)
        xdotool.stdin.write(b"keyup Left\n")
        xdotool.stdin.flush()
        time.sleep(.1)

    return

    img = Image.new("RGB", grab.size)
    #pixels = zip(grab.raw[2::4], grab.raw[1::4], grab.raw[0::4])
    #img.putdata(list(pixels))
    pixels = img.load()
    for x in range(grab.width):
        for y in range(grab.height):
            if y == center:
                pixels[x, y] = (150, 150, 150)
                if grab.pixel(x, y) == YELLOW:
                    if x > middle:
                        # GO LEFT
                        pass
                    continue
                if x < middle:
                    print(grab.pixel(x, y))
            elif x == middle:
                pixels[x, y] = (250, 250, 250)
            else:
                pixels[x, y] = grab.pixel(x, y)
    img.show()

if __name__ == "__main__":
    main()
