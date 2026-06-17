import { createSocket } from "./socket_helper.js";
import { changeInflationStatus } from "/static/timer/js/inflation_announcement.js";

const inflation_socket_url = "ws://127.0.0.1:8000/ws/inflation-announcement/";

createSocket(inflation_socket_url, (data) => {
    changeInflationStatus(data.current_inflation)
});