#!/usr/bin/python

import time
from os import path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ProjectEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(event.src_path)

event_handler = ProjectEventHandler()
observer = Observer()
observer.schedule(event_handler, path='.', recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
