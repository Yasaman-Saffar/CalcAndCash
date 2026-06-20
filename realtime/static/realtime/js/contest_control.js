import { createSocket } from "./socket_helper.js";

const control_socket_url = `ws://${window.location.hostname}:8000/ws/contest-control/`;

const socket = createSocket(control_socket_url, (data) => {
    if (data.type === "FORCE_REFRESH") {
        socket.close();
        setTimeout(() => window.location.reload(), 300);
    }
});