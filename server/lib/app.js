/*

Copyright 2016 Alex Jordan <alex@strugee.net>.

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

var fs = require('fs');
var path = require('path');
var express = require('express');
var compression= require('compression');

var app = express();

app.use(compression());

app.get('/api/people', function(req, res, next) {
	
});

app.get('/api/people/:name', function(req, res, next) {
	
});

app.post('/api/submit', function(req, res, next) {
	
});

module.exports = app;
