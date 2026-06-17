import { createSocket } from "./socket_helper.js";
import { updateLeaderboard } from "/static/leaderboard/js/update_leaderboard_look.js";
import { updateTable } from "/static/groups/js/staff/update_groups.js";

const leaderboard_socket_url = "ws://127.0.0.1:8000/ws/leaderboard/";

createSocket(leaderboard_socket_url, (data) => {
    updateLeaderboard(data);
    updateTable(data);
});