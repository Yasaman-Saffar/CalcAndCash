import { createSocket } from "./socket_helper.js";

const control_socket_url = "ws://127.0.0.1:8000/ws/contest-control/";

createSocket(control_socket_url, (data) => {
    if (data.type === "FORCE_REFRESH"){
        location.reload();
    }
});