watch
=====

Refreshes your browser when source files change during local development.

By default will refresh Chrome, but can refresh Safari too.

##Usage

    usage: watch.py [-b {chrome,safari}] path keyword

    Refresh browser tabs when local files change.

    positional arguments:
      path                  The directory to watch for changes.
      keyword               Tabs with this keyword in their URL will be refreshed.

    optional arguments:
      -b {chrome,safari}, --browser {chrome,safari}
                            Which browser to refresh.

e.g. to refresh any browser tabs with `localhost` in the URL when a source file in the current directory changes:

    watch.py . localhost

##Requirements
 * OS X
 
###Installation in a virtualenv with homebrewed Python
If you're using a homebrew-installed Python instead of the OS X-provided version, the `ScriptingBridge` module is probably not available.

To get around this, use the OS X Python when creating the virtualenv (you'll also need to enable access to system packages so `ScriptingBridge` is found):

    mkvirtualenv --system-site-packages --python=/System/Library/Frameworks/Python.framework/Versions/Current/bin/python watch
