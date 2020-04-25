/**
 * Module dependencies.
 */
var express = require('express');
var path = require('path');
var httpProxy = require('http-proxy');
var bodyParser = require('body-parser');
var devConfig = require('./localConfig.json')['development'];
// Node express server setup.
var server = express();
var appRouter = express.Router();

var apiForwardingUrl = devConfig.microServiceURL;

var proxyOptions = {
    changeOrigin: true,
    target: {
        https: true
    }
};

var allowCrossDomain = function (req, res, next) {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
    res.header('Access-Control-Allow-Headers', 'content-type, Authorization, Content-Length, X-Requested-With, Origin, Accept');

    if ('OPTIONS' === req.method) {
        res.send(200);
    } else {
        next();
    }
};

// var headers = {
//     'Content-Length': contentLength,
//     'Content-Type': 'application/x-www-form-urlencoded'
//   }

httpProxy.prototype.onError = function (err) {
    console.log(err);
};

var apiProxy = httpProxy.createProxyServer(proxyOptions);

console.log('Forwarding API requests to ' + apiForwardingUrl);


server.set('port', process.env.VCAP_APP_PORT || 5000);
server.use(express.static(path.join(__dirname, '../dist')));
server.use(allowCrossDomain);

//server.use(bodyParser.json());
server.use(bodyParser.urlencoded({
    extended: true
}));

// server.use('/', function(req, res) {
//   console.log('inside // api');
//   //express.static(path.join(__dirname, '../dist/index.html'));
// });

server.get("/apis/*", function(req, res) {
    req.headers['X-Access-Token'] = req.headers.token;
    req.url = req.url.replace('/apis/','');
    apiProxy.web(req, res, {target: apiForwardingUrl});
});

server.post("/apipost/*", function(req, res) {
    // console.log(req);
    req.headers['X-Access-Token'] = req.headers.token;
    req.url = req.url.replace('/apipost/','');
    // console.log(req.url);
    apiProxy.web(req, res, {target: apiForwardingUrl});
});

// server.get('/flux/*', (req, res, next) => {
//     server.use(express.static(path.join(__dirname, '../dist')));
//     res.sendFile(path.join(__dirname, '../dist/index.html'));
// });

server.get('/favicon.ico', function (req, res) {
  res.send('favicon.ico');
});

// Start Server.
server.listen(server.get('port'), function() {
    console.log('Express server listening on port ' + server.get('port'));
});

