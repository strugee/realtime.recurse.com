# realtime.recurse.com

Find out, in realtime, what people are working on in 455 Broadway.

## Architecture

How does it work? People voluntarily run a small daemon on their computers. The daemon does stuff like watch which files you're editing, and reports every once in a while to the web service. That lets the web service update the interface in realtime via WebSockets.

You can read more about the design of the system in the README.md files of the `client/` and `server/` directories.

## Author

Alex Jordan <alex@strugee.net>

## License

AGPL 3.0+
