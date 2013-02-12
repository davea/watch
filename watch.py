#!/usr/bin/env python
# coding: utf-8
import sys
import os
import time
from fsevents import Stream, Observer
from ScriptingBridge import SBApplication

FILE_TYPES = ['css', 'html', 'htm', 'php', 'rb', 'erb', 'less', 'js', 'pyc']

FILE_DELAYS = {
    'pyc': 1.5
}

def reload_chrome():
    chrome = SBApplication.applicationWithBundleIdentifier_("com.google.Chrome")
    if not chrome:
        print "Chrome doesn't appear to be running!"
        return
    for window in chrome.windows():
        for tab in window.tabs():
            if sys.argv[2] in tab.URL():
                print "Reloading {0}".format(tab.URL())
                tab.reload()

def reload_safari():
    safari = SBApplication.applicationWithBundleIdentifier_("com.apple.Safari")
    if not safari:
        print "Safari doesn't appear to be running!"
        return
    for window in safari.windows():
        for tab in window.tabs():
            if sys.argv[2] in tab.URL():
                print "Reloading {0}".format(tab.URL())
                tab.reload()
    

def event_callback(event):
    if "." not in event.name:
        return
    file_type = event.name.split(".")[-1].lower()
    if file_type in FILE_TYPES and (event.mask & 0x100 or event.mask & 0x2 or event.mask & 0x1000 or event.mask & 0x200):
        print "Detected change in {0}".format(event.name)
        if file_type in FILE_DELAYS:
            time.sleep(FILE_DELAYS[file_type])
        reload_chrome()

def main():
    if len(sys.argv) != 3:
        print "Usage: {0} <path> <keyword>".format(sys.argv[0])
        sys.exit(1)
    print "Watching {0} for changes...".format(os.path.abspath(sys.argv[1]))
    observer = Observer()
    stream = Stream(event_callback, sys.argv[1], file_events=True)
    observer.schedule(stream)
    observer.run()

if __name__ == '__main__':
    main()
