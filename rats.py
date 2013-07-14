#!/usr/bin/env python
# encoding: utf-8
"""
    Hello Julia,

    this program helps you to record what the rats did at which time.


    __________________________
    _________#######__________
    ________#___#___#_________
    _______#____#____#________
    _______#_________#________
    ________#########_________
    _________#######__________
    _________#_____#__________
    _________#_____#__________
    _________#_____#__________
    _________#_____#__________
    ______####_____####_______
    _____##___________##______
    _____#_____________#______
    _____##___________##______
    ______####_____####_______

Created by RUNTHROUTHEJUNGLE on 2012-01-27.
Copyright (c) 2012. All rights reserved.
"""

import os
import telnetlib
import Tkinter as tk
import tkFileDialog as diag

interval = 2        # in seconds
activities = {"1": "swimming", "2": "floating", "3": "drowning"}


class App():
    def __init__(self, interval, activities):
        self.interval = interval
        self.out = []
        self.activities = activities
        self.chars = "".join(self.activities.keys())
        self.root = tk.Tk()
        self.init_vlc_connection()
        self.init_gui()
        self.root.mainloop()

    def init_gui(self):
        """initialize the GUI elements"""
        self.root.title("Sad Rats")
        self.file_button = tk.Button(text="choose video", command=self.load_video_into_vlc)
        self.file_button.pack()
        self.label = tk.Label(text="choose a video to work on")
        self.label.pack()

    def init_vlc_connection(self):
        """open telnet connection to running VLC player"""
        self.vlc = VLCClient("::1")
        self.vlc.connect()

    def load_video_into_vlc(self):
        """load video into vlc player"""
        self.fname = diag.askopenfilename(parent=self.root, title='Choose video')
        if self.fname is not None:
            self.out = []
            self.vlc.clear()
            self.vlc.add(self.fname)
            self.vlc.stop()
            self.video_length = self.vlc.get_length()
            self.label.configure(text="press enter to start annotating the video")
            self.root.bind('<Return>', self.start)
            self.file_button.configure(state=tk.DISABLED)
        else:
            self.label.configure(text="no file selected")

    def start(self, event):
        """docstring for start"""
        self.vlc.play()
        self.root.unbind('<Return>')
        self.root.after(self.interval * 1000, self.repeated_loop)

    def repeated_loop(self):
        """stop video and ask for input"""
        self.vlc.pause()
        info = "select behavior [1, 2 or 3]\n"
        info += str(self.activities.items())
        self.label.configure(text=info)
        self.root.bind('<Key>', self.on_keypress)

    def on_keypress(self, event):
        """wait for user input"""
        # read and record key
        self.root.unbind('<Key>')
        if event.char in self.chars:
            self.out.append(event.char)

        # if the rest of the video is a full interval
        if self.vlc.get_time() + self.interval < self.video_length:
            self.root.after(self.interval * 1000, self.repeated_loop)
            self.vlc.play()
        else:
            self.stop()

    def stop(self):
        """docstring for stop"""
        fname_out = os.path.splitext(self.fname)[0] + '.csv'
        print self.activities
        print self.out
        with open(fname_out, "w") as f:
            f.write("time, activity\n")
            for i, activity in enumerate(self.out):
                time = (i + 1) * self.interval
                f.write("%d, %s, %s\n" % (time, activity, self.activities[str(activity)]))
        self.label.configure(text="yeah, done. output saved to: {0}".format(fname_out))
        self.file_button.configure(state=tk.ACTIVE)


class VLCClient(object):
    """Connection to a running VLC instance."""
    def __init__(self, server, port=4212, password="admin", timeout=5):
        self.server = server
        self.port = port
        self.password = password
        self.timeout = timeout

        self.telnet = None
        self.server_version = None

    def connect(self):
        """Connect to VLC and login"""
        assert self.telnet is None, "connect() called twice"
        self.telnet = telnetlib.Telnet()
        self.telnet.open(self.server, self.port, self.timeout)

        # Parse version
        result = self.telnet.expect([
            "VLC media player ([\d.]+)",
        ])
        self.server_version = result[1].group(1)
        self.server_version_tuple = self.server_version.split('.')

        # Login
        self.telnet.read_until("Password: ")
        self.telnet.write(self.password)
        self.telnet.write("\n")

        # Password correct?
        result = self.telnet.expect([
            "Password: ",
            ">"
        ])
        if "Password" in result[2]:
            raise WrongPasswordError()

    def disconnect(self):
        """Disconnect and close connection"""
        self.telnet.close()
        self.telnet = None

    def _send_command(self, line):
        """Sends a command to VLC and returns the text reply.
        This command may block."""
        self.telnet.write(line + "\n")
        return self.telnet.read_until(">")[1:-3]

    def _require_version(self, command, version):
        if isinstance(version, basestring):
            version = version.split('.')
        if version > self.server_version_tuple:
            raise OldServerVersion("Command '{0} requires at least VLC {1}".format(
                command, ".".join(version)
            ))

    #
    # item information
    #
    def get_length(self):
        return int(self._send_command("get_length"))

    def get_time(self):
        return int(self._send_command("get_time"))

    #
    # Playlist
    #
    def add(self, filename):
        """Add a file to the playlist and play it.
        This command always succeeds."""
        return self._send_command("add {0}".format(filename))

    def play(self):
        """Start/Continue the current stream"""
        return self._send_command("play")

    def pause(self):
        """Pause playing"""
        return self._send_command("pause")

    def stop(self):
        """Stop stream"""
        return self._send_command("stop")

    def clear(self):
        """Clear all items in playlist"""
        return self._send_command("clear")


class WrongPasswordError(Exception):
    pass


class OldServerVersion(Exception):
    pass


if __name__ == '__main__':
    app = App(interval, activities)
