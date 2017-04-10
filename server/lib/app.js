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
      redis = require('redis'),
      semver = require('semver');

const recommendedVersion = '0.1.0';

// Expiry time is 10 minutes
const expiryTime = 1000 * 60 * 10;

var app = express(),
    db = redis.createClient();

db.on('error', err => { throw err; });

app.set('view engine', 'pug');

app.use(compression());
app.use(bodyParser.json());

app.use(express.static('public'));

// Update information
app.use(function(req, res, next) {
	req.headers['user-agent'].split(' ').map(el => {
		let component = el.split('/');

		if (component[0] === 'rcrealtime'
		    && semver.lt(component[1], recommendedVersion)) {
			res.set('X-Upgrade-Required', recommendedVersion);
		}
	});

	next();
});

// Cache sets automatically propogate to Redis
var cache = new Map();
// TODO

app.get('/', function(req, res, next) {
	// TODO: figure out how to iterate over a Map in Pug
	var objCache = Object.create(null);
	cache.forEach((value, key) => {
		objCache[key] = value;
	});
	res.render('index', {cache: objCache, dataAvailable: cache.size !== 0});
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

app.get('/api/versions/:major', function(req, res, next) {
	if (req.params.major !== '0') {
		next();
		return;
	}

	// TODO make this only offer semver-compatible upgrades
	res.json({
		recommended: {
			version: recommendedVersion,
			download: 'http://localhost:8080/update-bundle.tar.gz',
			signature: 'http://localhost:8080/update-bundle.tar.gz.sig'
		},
		prerelease: null
	});
});

module.exports = app;
