#!/usr/bin/env python
# coding: utf-8
import sys
import os
import time
from functools import partial

from ScriptingBridge import SBApplication

from fsevents import Stream, Observer

FILE_TYPES = ['css', 'html', 'htm', 'php', 'rb', 'erb', 'less', 'js', 'py']

# Some files need a delay before refresh for the changes to become apparent.
# e.g. Django's runserver takes a few moments to notice and reload the new code.
# This is slightly hacky, but does work...
FILE_DELAYS = {
    'py': 3.5
}

# File event flags that will cause a refresh. Correspond to those defined in FSEvents.h.
FLAGS = (
    0x100,  # kFSEventStreamEventFlagItemCreated
    0x200,  # kFSEventStreamEventFlagItemRemoved
    0x1000, # kFSEventStreamEventFlagItemModified
    0x2,    # kFSEventStreamEventFlagUserDropped - seems to be needed too
)

# The various functions that refresh specific browsers are registered in this dict and called when
# a watched file changes.
browser_reloaders = {}

def reload_chrome():
    chrome = SBApplication.applicationWithBundleIdentifier_("com.google.Chrome")
    if not chrome:
        print "Chrome doesn't appear to be running!"
        return
    for window in chrome.windows():
        for tab in window.tabs():
            if sys.argv[2] in tab.URL():
                print "Reloading Chrome: {}".format(tab.URL())
                tab.reload()
browser_reloaders['chrome'] = reload_chrome

def reload_safari():
    safari = SBApplication.applicationWithBundleIdentifier_("com.apple.Safari")
    if not safari:
        print "Safari doesn't appear to be running!"
        return
    for window in safari.windows():
        for tab in window.tabs():
            if sys.argv[2] in tab.URL():
                print "Reloading Safari: {}".format(tab.URL())
                tab.setURL_(tab.URL())
browser_reloaders['safari'] = reload_safari
    

def event_callback(event, browsers):
    if "." not in event.name:
        return
    file_type = event.name.split(".")[-1].lower()
    if file_type in FILE_TYPES and any(event.mask & flag for flag in FLAGS):
        print "Detected change in {}".format(event.name)
        if file_type in FILE_DELAYS:
            time.sleep(FILE_DELAYS[file_type])
        for browser in browsers:
            if browser in browser_reloaders:
                browser_reloaders[browser]()
            else:
                print "Can't refresh unknown browser {}".format(browser)

def main():
    if len(sys.argv) != 3:
        print "Usage: {} <path> <keyword>".format(sys.argv[0])
        sys.exit(1)
    print "Watching {} for changes...".format(os.path.abspath(sys.argv[1]))
    event_callback_partial = partial(event_callback, browsers=("chrome",))
    observer = Observer()
    stream = Stream(event_callback_partial, sys.argv[1], file_events=True)
    observer.schedule(stream)
    observer.run()

if __name__ == '__main__':
    main()
