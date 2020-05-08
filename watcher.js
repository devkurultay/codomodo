var fs = require('fs')
var http = require('http');
var { spawn } = require("child_process");
var chokidar = require('chokidar');
var WebSocketServer = require('websocket').server;

var server = http.createServer();
server.listen(9898);

var wsServer = new WebSocketServer({
  httpServer: server
});

var connection

wsServer.on('request', function(request) {
  connection = request.accept(null, request.origin);
  connection.on('message', function(message) {
    console.log('Received Message:', message.utf8Data);
    connection.sendUTF('Hi this is WebSocket server!');
  });
  connection.on('close', function(reasonCode, description) {
    console.log('Client has disconnected.');
  });
});

// Set folder here
var testFolder = './frontend/src'
var watcher = chokidar.watch(testFolder, {
  ignoreInitial: true
})

// Watch the files
watcher
  .on('change', changed)
  .on('add', changed)
  .on('unlink', changed)

function changed (file, stats) {
  console.log('Changed', file)
  var dev = spawn('./node_modules/.bin/webpack', ['--mode', 'development'])

  dev.stdout.on("data", data => {
    console.log(`stdout: ${data}`);
    // Send reload command
    if(connection) {
      connection.sendUTF('RELOAD')
    }
  });

  dev.stderr.on("data", data => {
    console.log(`stderr: ${data}`);
  });

  dev.on('error', (error) => {
    console.log(`error: ${error.message}`);
  });

  dev.on("close", code => {
    console.log(`child process exited with code ${code}`);
  });
}
