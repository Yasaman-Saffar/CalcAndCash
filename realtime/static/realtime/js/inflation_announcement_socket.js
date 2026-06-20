import { createSocket } from "./socket_helper.js";
import { changeInflationStatus } from "/static/timer/js/inflation_announcement.js";

const inflation_socket_url = `ws://${window.location.hostname}:8000/ws/inflation-announcement/`;

createSocket(inflation_socket_url, (data) => {
    changeInflationStatus(data.current_inflation)
});