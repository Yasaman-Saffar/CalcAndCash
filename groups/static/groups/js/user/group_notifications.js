function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value
}

// realtime notification in the notif page
export function groupNotifPage(container_id, header, message, time, notification_id) {

    const container = document.getElementById(container_id);

    if (!container) return;

    const empty = document.getElementById("empty-group-notifications");
    if (empty) empty.remove();

    const id = "notif_" + Date.now();

    const html = `
        <div class="accordion mb-3 shadow-sm rounded-4 overflow-hidden border-0"
             id="accordion_${id}">

            <div class="accordion-item border-0">

                <h2 class="accordion-header">

                    <button class="accordion-button collapsed py-3 px-4 read_message_btn"
                            data-read="0"
                            data-id="${notification_id}"
                            data-csrf="${csrfToken}"
                            type="button"
                            data-bs-toggle="collapse"
                            data-bs-target="#collapse_notif_page${id}">

                        <div class="d-flex align-items-center justify-content-between w-100 me-3">

                            <div class="d-flex align-items-center gap-3">

                                <span class="p-1 bg-danger border border-light rounded-circle"></span>

                                <span class="fw-semibold text-dark">
                                    ${header}
                                </span>

                            </div>

                            <small class="text-muted">
                                ${time}
                            </small>

                        </div>

                    </button>

                </h2>

                <div id="collapse_notif_page${id}"
                     class="accordion-collapse collapse"
                     data-bs-parent="#notification-list-page">

                    <div class="accordion-body bg-light-subtle px-4 py-3 text-secondary">
                        ${message}
                    </div>

                </div>

            </div>

        </div>
    `;

    container.insertAdjacentHTML("afterbegin", html);

    const accordions = listCol.querySelectorAll(":scope > .accordion");
    if (accordions.length > 7) {
        accordions[accordions.length - 1].remove();
    }
}