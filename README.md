# realtime.recurse.com

Find out, in realtime, what people are working on in 455 Broadway.

## Architecture

How does it work? People voluntarily run a small daemon on their computers. The daemon does stuff like watch which files you're editing, and reports every once in a while to the web service. That lets the web service update the interface in realtime via WebSockets.

You can read more about the design of the system in the README.md files of the `client/` and `server/` directories.

## Privacy

Some important notes:

1. The client will **never** disclose the project you're working on if that project is not public. This information won't even make it to the server.
2. The client will **never** change its behavior to report more than what you said was okay when you installed.

You're always in control of what you report.

## Author

Alex Jordan <alex@strugee.net>

## License

AGPL 3.0+
