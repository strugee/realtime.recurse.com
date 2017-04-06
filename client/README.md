# realtime.recurse.com client component

The files in this directory are responsible for monitoring the filesystem and updating the server.

The client is written in Python.

## Features

The client is currently very simple. If you touch a file in a git or Mercurial project, it'll automatically assume you're working on that project. In the future this will gain some smarter heuristics.

It also contains an autoupdater.

## Automatic updates

The client is able to update itself. Out of the box the autoupdater will only update to client releases that don't turn on new reporting by default. That means that whatever 

Updates are cryptographically signed by AJ. The client verifies this signature before updating and will abort if it doesn't match.

## Configuration

The client reads configuration from an INI file located at `$XDG_CONFIG_HOME/rcrealtime.ini`. On most systems, this is set to `~/.config/rcrealtime.ini`.

The only required configuration option is your name, so the configuration can be as simple as:

```ini
[main]

name = Alyssa P. Hacker
```

However, you can also specify more advanced options. Everything is optional except for `name`. Here's a complete annotated config file showing the defaults:

```ini
[main]

# The name you're reporting under. Set this to your real name.
name = Alyssa P. Hacker

# Server to submit to
server = https://realtime.recurse.com

[reporters]

# Whether or not to report development activity in *public* repos
editing = on

[editing]

# Comma-separated list of tilde-expanded directories to recursively watch for activity
dirs = ~/Development, ~/dev, ~/Documents/GitHub, ~/code, ~/repos
```
