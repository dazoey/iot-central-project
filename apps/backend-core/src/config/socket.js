const { Server } = require('socket.io');

let io = null;

const initSocket = (server) => {
    io = new Server(server, {
        cors: {
            origin: '*',
            methods: ['GET', 'POST']
        },
        pingTimeout: 60000,
        pingInterval: 25000
    });

    io.on('connection', (socket) => {
        console.log(`[INFO] Socket.IO Client Connected: ${socket.id}`);

        // Room Joining untuk Perangkat Spesifik (Misal frontend memilih fokus ke 1 device saja)
        socket.on('join-device-room', (deviceId) => {
            const roomName = `device_${deviceId}`;
            socket.join(roomName);
            console.log(`[INFO] Client ${socket.id} bergabung ke room: ${roomName}`);
        });

        // Leaving Room
        socket.on('leave-device-room', (deviceId) => {
            const roomName = `device_${deviceId}`;
            socket.leave(roomName);
            console.log(`[INFO] Client ${socket.id} meninggalkan room: ${roomName}`);
        });

        socket.on('disconnect', (reason) => {
            console.log(`[INFO] Socket.IO Client Disconnected: ${socket.id} (Reason: ${reason})`);
        });
    });

    return io;
};

const getIO = () => {
    if (!io) {
        throw new Error('[ERROR] Socket.IO belum diinisialisasi!');
    }
    return io;
};

module.exports = { initSocket, getIO };
