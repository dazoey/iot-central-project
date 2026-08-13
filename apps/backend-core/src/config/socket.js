const { Server } = require('socket.io');

let io = null;

const initSocket = (server) => {
    io = new Server(server, {
        cors: {
            origin: '*',
            methods: ['GET', 'POST']
        }
    });

    io.on('connection', (socket) => {
        console.log(`[INFO] Socket.IO Client Connected: ${socket.id}`);

        socket.on('disconnect', () => {
            console.log(`[INFO] Socket.IO Client Disconnected: ${socket.id}`);
        });
    });

    return io;
};

const getIO = () => {
    if (!io) {
        throw new Error('Socket.IO belum diinisialisasi!');
    }
    return io;
};

module.exports = { initSocket, getIO };
