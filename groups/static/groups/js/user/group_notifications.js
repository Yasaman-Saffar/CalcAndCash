function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value
}

// realtime notification in the notif page
export function groupNotifPage(container_id, header, message, time, notification_id){
    const container = document.getElementById(container_id);
    const id = "notif_" + Date.now();
    const empty = document.getElementById("empty-notification-page")
    if(empty){
        empty.remove()
    }

    const html = `
        <div class="accordion" id="accordion_${id}">
            <div class="accordion-item">
                <h2 class="accordion-header">
                <button class="accordion-button collapsed read_message_btn" 
                        data-read="0"
                        data-id="${notification_id}"
                        data-csrf="${getCSRFToken()}"
                        type="button" 
                        data-bs-toggle="collapse" 
                        data-bs-target="#collapse_notif_page${id}"
                        aria-expanded="false" 
                        aria-controls="panelsStayOpen-collapseTwo">
                    <strong>${header}</strong>
                    <small>${time}</small>

                    <span class="position-absolute top-0 start-0 translate-middle p-1 bg-danger border border-light rounded-circle">
                        <span class="visually-hidden">New alerts</span>
                    </span>

                </button>
                </h2>
                <div id="collapse_notif_page${id}" class="accordion-collapse collapse">
                <div class="accordion-body">
                    ${message}
                </div>
                </div>
            </div>
        </div>
    ` ;
    container.insertAdjacentHTML("afterbegin", html);
    while (container.children.length > 7) {
        container.lastElementChild.remove();
    }
}