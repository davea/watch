#!/usr/bin/env python
# coding: utf-8
import sys
import os
import time
from functools import partial
import argparse

from ScriptingBridge import SBApplication

from fsevents import Stream, Observer

FILE_TYPES = ['css', 'scss', 'html', 'htm', 'php', 'rb', 'erb', 'less', 'js', 'py', 'jst', 'md']

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

def reload_chrome(keyword):
    chrome = SBApplication.applicationWithBundleIdentifier_("com.google.Chrome")
    if not chrome:
        print "Chrome doesn't appear to be running!"
        return
    for window in chrome.windows():
        for tab in window.tabs():
            if keyword in tab.URL():
                print "Reloading Chrome: {}".format(tab.URL())
                tab.reload()
browser_reloaders['chrome'] = reload_chrome

def reload_safari(keyword):
    safari = SBApplication.applicationWithBundleIdentifier_("com.apple.Safari")
    if not safari:
        print "Safari doesn't appear to be running!"
        return
    for window in safari.windows():
        for tab in window.tabs():
            if keyword in tab.URL():
                print "Reloading Safari: {}".format(tab.URL())
                tab.setURL_(tab.URL())
browser_reloaders['safari'] = reload_safari
    

def event_callback(event, browsers, keyword):
    if "." not in event.name:
        return
    file_type = event.name.split(".")[-1].lower()
    if file_type in FILE_TYPES and any(event.mask & flag for flag in FLAGS):
        print "Detected change in {}".format(event.name)
        if file_type in FILE_DELAYS:
            time.sleep(FILE_DELAYS[file_type])
        for browser in browsers:
            if browser in browser_reloaders:
                browser_reloaders[browser](keyword)
            else:
                print "Can't refresh unknown browser {}".format(browser)

def main():
    parser = argparse.ArgumentParser(description="Refresh browser tabs when local files change.")
    parser.add_argument("path", help="The directory to watch for changes.")
    parser.add_argument("keyword", help="Tabs with this keyword in their URL will be refreshed.")
    parser.add_argument("-b", "--browser", help="Which browser to refresh.", choices=sorted(browser_reloaders.keys()), default="chrome")
    args = parser.parse_args()
    print "Watching {} for changes...".format(os.path.abspath(args.path))
    event_callback_partial = partial(event_callback, browsers=(args.browser,), keyword=args.keyword)
    observer = Observer()
    stream = Stream(event_callback_partial, sys.argv[1], file_events=True)
    observer.schedule(stream)
    try:
        observer.start()
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        observer.stop()


if __name__ == '__main__':
    main()
