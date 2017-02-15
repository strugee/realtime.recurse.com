# realtime.recurse.com server component

The files in this directory are responsible for serving the web interface and handling API calls.

It's written in Node.js and uses Express.js. ES6 is preferred.

## Design

The web server is designed to be "mostly stateless". This means that while it's not, strictly speaking, stateless, its design is similar to and influenced by stateless systems in that the state it keeps can be thought of as a cache that can be dropped at any time with minimal functionality impact.

More specifically, upon submission, each incoming update is put in two places: an in-memory JavaScript Map object, and a Redis database. Requests are served from the Map and the Redis database is only used to initialize the Map on startup. The reader will note that, as alluded to above, this provides terrible data persistence guarantees. However, this is completely fine: records are automatically expired every 10 minutes anyway, so in the event that data is lost, the system will be completely consistent with clients again in 10 minutes or less.

Likewise, there is no authentication state. The web UI is unrestricted, and API submissions are accepted based on the IP that they originate from (it's checked against 455 Broadway's address). This isn't the most secure thing ever, but is more than good enough. As a nice side effect, it automatically filters out submissions from people who aren't physically in the space.
