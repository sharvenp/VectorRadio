const express = require("express");
const socketio = require("socket.io");

const app = express();

const server = app.listen(8001);

const io = socketio(server);

io.on("connection", (socket) => {});
