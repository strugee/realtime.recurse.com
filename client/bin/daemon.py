#!/usr/bin/python

import time
import sched
import subprocess
from os import path, chdir, getcwd
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

# 5 minutes
#resubmitTime = 60 * 5
resubmitTime = 5
version = '0.1.0'

lastUrl = None
lastWasPeriodic = False

def submit_data(repo_url, action='edit'):
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': requests.utils.default_user_agent() + ' rcrealtime/' + version
    })

    payload = { 'action': action, 'url': repo_url }
    r = requests.post('http://localhost:8000/api/people/aj', headers=headers, json=payload)
    print('Received {0} {1} from server.'.format(r.status_code, r.reason))

    if r.headers.get('X-Upgrade-Required'):
        print('Response included notification about version ' + r.headers['X-Upgrade-Required'])

class ProjectEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        global lastWasPeriodic
        global lastUrl

        if not isinstance(event, FileModifiedEvent):
            # TODO expand this
            print('Incoming event is not a file modification; ignoring')
            return

        print('Dispatching request.')
        # Find the git root
        # TODO this could be made more efficient with popen
        cwd = getcwd()
        chdir(path.dirname(event.src_path))
        try:
            repo_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], universal_newlines=True)
        except subprocess.CalledProcessError:
            print('Failed to get git repository information; probably this isn\'t a git project.')
            print('Trying hg.')
            try:
                # TODO: probably this can be done natively in Python
                repo_url = subprocess.check_output(['hg', 'path', 'default'], universal_newlines=True)
            except CalledProcessError:
                print('Failed to get hg repository information; probably this isn\'t an hg project.')
                print('No more version control systems to try. Bailing.')
                chdir(cwd)
                return
        chdir(cwd)

        lastUrl = repo_url
        lastWasPeriodic = False
        submit_data(repo_url)

print('realtime.recurse.com client starting up...')

event_handler = ProjectEventHandler()
observer = Observer()
observer.schedule(event_handler, path='.', recursive=True)
observer.start()

print('Listening for filesystem events.')

periodicSubmitter = sched.scheduler(time.time, time.sleep)

def submit_periodic(sc):
    global lastWasPeriodic
    if lastUrl and not lastWasPeriodic:
        print('Submitting a periodic update.')
        lastWasPeriodic = True
        submit_data(lastUrl, action='edit')
    periodicSubmitter.enter(resubmitTime, 1, submit_periodic, (sc,))

periodicSubmitter.enter(resubmitTime, 1, submit_periodic, (periodicSubmitter ,))
periodicSubmitter.run()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
