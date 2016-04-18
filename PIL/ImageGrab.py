#
# The Python Imaging Library
# $Id$
#
# screen grabber (OS X and Windows only)
#
# History:
# 2001-04-26 fl  created
# 2001-09-17 fl  use builtin driver, if present
# 2002-11-19 fl  added grabclipboard support
#
# Copyright (c) 2001-2002 by Secret Labs AB
# Copyright (c) 2001-2002 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

from PIL import Image

import sys
if sys.platform not in ["win32", "darwin"]:
    raise ImportError("ImageGrab is OS X and Windows only")

if sys.platform == "win32":
    grabber = Image.core.grabscreen
elif sys.platform == "darwin":
    import os
    import tempfile
    import subprocess


def grab(bbox=None):
    if sys.platform == "darwin":
        f, file = tempfile.mkstemp('.png')
        os.close(f)
        subprocess.call(['screencapture', '-x', file])
        im = Image.open(file)
        im.load()
        os.unlink(file)
    else:
        size, data = grabber()
        im = Image.frombytes(
            "RGB", size, data,
            # RGB, 32-bit line padding, origo in lower left corner
            "raw", "BGR", (size[0]*3 + 3) & -4, -1
            )
    if bbox:
        im = im.crop(bbox)
    return im


def grabclipboard():
    if sys.platform == "darwin":
        f, file = tempfile.mkstemp('.jpg')
        os.close(f)
        commands = [
            "set theFile to (open for access POSIX file \""+file+"\" with write permission)",
            "try",
                "write (the clipboard as JPEG picture) to theFile",
            "end try",
            "close access theFile"
        ]
        script = ["osascript"]
        for command in commands:
            script += ["-e", command]
        subprocess.call(script)

        im = None
        if os.stat(file).st_size != 0:
            im = Image.open(file)
            im.load()
        os.unlink(file)
        return im
    else:
        debug = 0  # temporary interface
        data = Image.core.grabclipboard(debug)
        if isinstance(data, bytes):
            from PIL import BmpImagePlugin
            import io
            return BmpImagePlugin.DibImageFile(io.BytesIO(data))
        return data
