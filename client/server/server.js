import { io } from "socket.io-client";

export const socket = io("wss://smeruxa.ru", {
    path: "/pumpbot_api",
    transports: ["websocket"],
    secure: true,
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000
});

export default socket