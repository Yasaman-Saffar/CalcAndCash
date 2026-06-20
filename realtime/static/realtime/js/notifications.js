import { createSocket } from "./socket_helper.js";
import { addToastNotif } from "/static/js/toasts.js";
import { groupNotifPage} from "/static/groups/js/user/group_notifications.js";
import { personalNotifPage } from "/static/dashboard/js/personal_notifications.js";

const notification_socket_url = `ws://${window.location.hostname}:8000/ws/notifications/`;

createSocket(notification_socket_url, (data) => {
    addToastNotif(data.header, data.message, data.time);

    if (data.type == "group" || data.type == "contest"){
        groupNotifPage("g-notifications-list", data.header, data.message, data.time, data.notif_id);
    }
    else if (data.type == "personal"){
        personalNotifPage("notifications-list", data.header, data.message, data.time, data.context, data.notif_id);
    }
});
