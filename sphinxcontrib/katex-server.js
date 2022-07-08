const net = require("net");
const process = require("process");

let value = null;
let katex_options = {};
let socket = null;
let port = null;
// this is the downloaded katex javascript library.
// need to keep it updated
// path to the downloaded katex javascript library `katex.min.js`.
let katex_path = "./katex.min";
process.argv.forEach(function(arg) {
    if (value == "katex_path") {
        katex_path = arg;
        value = null;
    } else if (value == "socket_path") {
        socket = arg;
        value = null;
    } else if (value == "socket_port") {
        port = arg;
        value = null;
    } else {
        if (arg == "--katex") {
            value = "katex_path";
        } else if (arg == "--socket") {
            value = "socket_path";
        } else if (arg == "--port") {
            value = "socket_port";
        } else {
            // Ignore unknown/unexpected arguments, for example the path to this
            // script
        }
    }
});

const katex = require(katex_path);

let listen_options = {};
if (socket !== null) {
    listen_options["path"] = socket;
} else if (port !== null) {
    listen_options["port"] = port;
    // Do not expose the rendering server on the network
    listen_options["host"] = "127.0.0.1";
}

// Start the network server for processing our sphinx's latex's math equations
const server = net.createServer();
server.on("connection", setupClient);
server.listen(listen_options);

function setupClient(client) {
    // Split the input stream into individual rendering requests
    // How many bytes are still left in the current request
    let bytesLeft = null;
    // List of chunks belonging to the current request
    let buffer = [];
    // Any undecoded bytes from the previous chunk, for example we were expecting
    // a 4-byte integer but only received 2 bytes
    let undecodedBytes = null;
    client.on("data", function(chunk) {
        // If there are any undecoded bytes left from the previous chunk, prepend
        // them to the current one
        if (undecodedBytes !== null) {
            chunk = Buffer.concat([undecodedBytes, chunk]);
            undecodedBytes = null;
        }

        let start = 0;
        while (start < chunk.length) {
            let remainingBytes = chunk.length - start;
            if (bytesLeft === null) {
                if (remainingBytes >= 4) {
                    bytesLeft = chunk.readInt32LE(start);
                    start += 4;
                } else {
                    undecodedBytes = chunk.slice(start);
                    break;
                }
            } else {
                if (remainingBytes >= bytesLeft) {
                    let end = start + bytesLeft;
                    buffer.push(chunk.slice(start, end));

                    var all = Buffer.concat(buffer);
                    handleRequest(client, all.toString());

                    bytesLeft = null;
                    buffer = [];
                    start = end;
                } else {
                    buffer.push(chunk.slice(start));

                    bytesLeft -= remainingBytes;
                    break;
                }
            }
        }
    });

    client.on("end", function() {
        buffer = [];
    });
}

function handleRequest(client, serialized) {
    try {
        var request = JSON.parse(serialized);
    } catch (e) {
        let response = { "error": `Could not deserialize ${serialized}: ${e.message}` };
        sendMessage(client, JSON.stringify(response));

        return;
    }

    try {
        let latex = request["latex"];
        let options = request["katex_options"] || {};
        // this is where math latex equation is processed
        let html = katex.renderToString(latex, options);

        let response = { "html": html };
        sendMessage(client, JSON.stringify(response));
    } catch (e) {
        let response = { "error": e.message };
        sendMessage(client, JSON.stringify(response));
    }
}

function sendMessage(client, message) {
    // Encode the message string into bytes
    let msgBuffer = Buffer.from(message, "utf-8");

    // Tell the client how many bytes we are going to send
    let lengthBuffer = Buffer.alloc(4);
    lengthBuffer.writeInt32LE(msgBuffer.length, 0);
    client.write(lengthBuffer);

    // Send the actual message
    client.write(msgBuffer);
}

