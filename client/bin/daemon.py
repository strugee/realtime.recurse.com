#!/usr/bin/python

import time
import subprocess
from os import path, chdir, getcwd
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ProjectEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print('Dispatching request.')
        # Find the git root
        # TODO this could be made more efficient with popen
        cwd = getcwd()
        chdir(path.dirname(event.src_path))
        repo_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], universal_newlines=True)
        repo_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], universal_newlines=True)
        chdir(cwd)

        payload = { 'action': 'edit', 'url': repo_url }
        r = requests.post('http://localhost:8000/api/people/aj', json=payload)
        print(r.status_code, r.reason)

print('realtime.recurse.com client starting up...')

event_handler = ProjectEventHandler()
observer = Observer()
observer.schedule(event_handler, path='.', recursive=True)
observer.start()

print('Listening for filesystem events.')

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
