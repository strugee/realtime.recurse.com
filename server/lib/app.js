/*

Copyright 2017 Alex Jordan <alex@strugee.net>.

This file is part of realtime.recurse.com.

realtime.recurse.com is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

realtime.recurse.com is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with realtime.recurse.com. If not, see
<https://www.gnu.org/licenses/>.

*/

'use strict';

const fs = require('fs'),
      path = require('path'),
      express = require('express'),
      compression= require('compression'),
      bodyParser = require('body-parser'),
      redis = require('redis');

// Expiry time is 10 minutes
const expiryTime = 1000 * 60 * 10;

var app = express(),
    db = redis.createClient();

db.on('error', err => { throw err; });

app.use(compression());
app.use(bodyParser.json());

// Cache sets automatically propogate to Redis
var cache = new Proxy(new Map(), {
	apply: function(target, thisArg, argumentsList) {
		// Do the default behavior but kick off a Redis command
		debugger;
	}
});

app.get('/api/people', function(req, res, next) {
	res.write('[');

	let count = 0, target = cache.size - 1;
	for (const key of cache.keys()) {
		res.write(`"${key}"`);
		if (count !== target) res.write(',');
		count++;
	}

	res.end(']');
});

app.get('/api/people/:name', function(req, res, next) {
	res.json(cache.get(req.params.name));
});

app.post('/api/people/:name', function(req, res, next) {
	if (!req.body.action) {
		res.status(400);
		res.end('Missing `action` parameter');
		return;
	}

	cache.set(req.params.name, req.body);

	setTimeout(() => {
		cache.delete(req.params.name);
	}, expiryTime);

	res.status(204);
	res.end();
});

module.exports = app;
