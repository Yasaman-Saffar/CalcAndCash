import { createSocket } from "./socket_helper.js";
import { addToastNotif } from "/static/js/toasts.js";
import { groupNotifPage} from "/static/groups/js/user/group_notifications.js";
import { personalNotifPage } from "/static/dashboard/js/personal_notifications.js";

const notification_socket_url = "ws://127.0.0.1:8000/ws/notifications/";

createSocket(notification_socket_url, (data) => {
    addToastNotif(data.header, data.message, data.time);

    if (data.type == "group" || data.type == "contest"){
        groupNotifPage("notification-list-page", data.header, data.message, data.time, data.notif_id);
    }
    else if (data.type == "personal"){
        personalNotifPage("pnotification-list-page", data.header, data.message, data.time, data.context, data.notif_id);
    }
});
