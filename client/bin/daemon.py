#!/usr/bin/python3

from configparser import SafeConfigParser, NoSectionError
import xdg
import time
import sched
import subprocess
import tempfile
import gnupg
from os import path, chdir, getcwd
import requests
import urllib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

# 5 minutes
resubmitTime = 60 * 5
version = '0.1.0'
# TODO make this report the Python version
userAgent = requests.utils.default_user_agent() + ' rcrealtime/' + version

lastUrl = None
lastWasPeriodic = False

# Parse configs before we do anything else

settings = SafeConfigParser()
settings.read(path.normpath(path.join(path.dirname(__file__), '..', 'lib', 'defaults.ini')))
settings.read(path.join(xdg.XDG_CONFIG_HOME, 'rcrealtime.ini'))

if not ('main' in settings and 'name' in settings['main']):
    print('I can\'t do anything without a name in the configuration.')
    exit(1)

editingDirs = map((lambda s: path.expanduser(s.strip())), settings['editing']['dirs'].split(','))

def perform_upgrade(url, signature_url):
    print('Performing upgrade.')
    tmpdir = tempfile.TemporaryDirectory(prefix='rcrealtime')
    pkgfile = path.join(tmpdir.name, 'package.tar.xz')
    sigfile = path.join(tmpdir.name, 'package.tar.xz.sig')
    # TODO make this respect the user agent
    # TODO URLopener is deprecated
    package = urllib.request.URLopener()
    package.retrieve(url, pkgfile)
    signature = urllib.request.URLopener()
    signature.retrieve(signature_url, sigfile)

    # TODO ship the keyring in the package
    gpg = gnupg.GPG(gnupghome=path.join(tmpdir.name, 'gpg_home'))
    key_import = gpg.recv_keys('hkp://pool.sks-keyservers.net', 'C46D8E7A3F13AD1C8EC6784843BF769C4ACA8B96')
    sigfile_obj = open(sigfile, 'rb')
    verification = gpg.verify_file(sigfile_obj, pkgfile)

    if verification.trust_level is None:
        print('Aborted update due to mismatched signature.')
        # TODO notify user

    print('Downloaded and verified update bundle.')
    # TODO unpack and stuff
    print('Upgrade complete.')

def submit_data(repo_url, action='edit'):
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': userAgent
    })

    payload = { 'action': action, 'url': repo_url }
    r = requests.post('{0}/api/people/{1}'.format(settings['main']['server'], settings['main']['name']), headers=headers, json=payload)
    print('Received {0} {1} from server.'.format(r.status_code, r.reason))

    if r.headers.get('X-Upgrade-Required'):
        print('Response included notification about version ' + r.headers['X-Upgrade-Required'] + '; requesting upgrade information.')
        upgrade_r = requests.get('{0]/api/versions/0'.format(settings['main']['server']), headers=headers)
        upgrade = upgrade_r.json()
        perform_upgrade(upgrade['recommended']['download'], upgrade['recommended']['signature'])

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

if settings.getboolean('reporters', 'editing'):
    event_handler = ProjectEventHandler()
    observer = Observer()
    for i in [i for i in editingDirs if path.exists(i)]:
        print('Registering filesystem watcher for {0}; this may take a while...'.format(i))
        observer.schedule(event_handler, path=i, recursive=True)
        print('Registered filesystem watcher for {0}.'.format(i))
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
