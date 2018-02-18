#!/usr/bin/env python
"""Wait for Dock to launch."""
import subprocess
import sys
import time


# One million percent stolen almost verbatim from munki
def get_running_processes():
    """Return a list of paths of running processes."""
    proc = subprocess.Popen(['/bin/ps', '-axo' 'comm='],
                            shell=False, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (output, dummy_err) = proc.communicate()
    if proc.returncode == 0:
        return [item for item in output.splitlines()
                if item.startswith('/')]
    return []


def is_app_running(appname):
    """Determine if the application in appname is currently running."""
    proc_list = get_running_processes()
    matching_items = []
    if appname.startswith('/'):
        # search by exact path
        matching_items = [item for item in proc_list
                          if item == appname]
    elif appname.endswith('.app'):
        # search by filename
        matching_items = [item for item in proc_list
                          if '/' + appname + '/Contents/MacOS/' in item]
    else:
        # check executable name
        matching_items = [item for item in proc_list
                          if item.endswith('/' + appname)]
    if not matching_items:
        # try adding '.app' to the name and check again
        matching_items = [item for item in proc_list
                          if '/' + appname + '.app/Contents/MacOS/' in item]

    if matching_items:
        # it's running!
        print 'Matching process list: %s' % matching_items
        print '%s is running!' % appname
        return True

    # if we get here, we have no evidence that appname is running
    return False


def main():
    """Script workflow."""
    # Wait for Dock to start
    while is_app_running('Dock') is False:
        print 'Waiting for Dock'
        time.sleep(1)
    time.sleep(4)
    return 0


if __name__ == "__main__":
    MAIN_RESULT = main()
    sys.exit(MAIN_RESULT)
