export function personalNotifPage(container_id, header, message, time, context, notification_id) {

    const container = document.getElementById(container_id);

    if (!container) return;

    const empty = document.getElementById("empty-user-notifications");
    if (empty) empty.remove();

    const id = "notif_" + Date.now();

    let buttons = "";

    if (context === "invitation") {
        buttons = `
        <hr class="my-3">
        <form method="post"
              action="/groups/invitation-response/"
              class="d-flex flex-column flex-sm-row gap-2">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
            <input type="hidden" name="notification_id" value="${notification_id}">

            <button class="btn btn-success rounded-3 px-4" type="submit" name="action" value="accept">
                <i class="bi bi-check2-circle me-1"></i> Accept
            </button>
            <button class="btn btn-outline-danger rounded-3 px-4" type="submit" name="action" value="reject">
                <i class="bi bi-x-circle me-1"></i> Reject
            </button>
        </form>
        `;
    }

    const html = `
    <div class="accordion mb-3 shadow rounded-4 overflow-hidden" id="accordion_${id}">
        <div class="accordion-item border-0">
            <h2 class="accordion-header">
                <button
                    class="accordion-button collapsed read_message_btn py-3 px-4"
                    data-read="0"
                    data-id="${notification_id}"
                    data-csrf="${csrfToken}"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#collapse_notif_personal${id}"
                >
                    <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between w-100 gap-2 pe-3">
                        <div class="d-flex align-items-center gap-3">
                            <span class="p-1 bg-danger border border-light rounded-circle" title="Unread">
                                <span class="visually-hidden">New</span>
                            </span>
                            <span class="fw-semibold text-dark">${header}</span>
                        </div>

                        <small class="text-muted flex-shrink-0">${time}</small>
                    </div>
                </button>
            </h2>

            <div id="collapse_notif_personal${id}" class="accordion-collapse collapse">
                <div class="accordion-body px-4 py-3">
                    <div class="text-secondary">${message}</div>
                    ${buttons}
                </div>
            </div>
        </div>
    </div>`;

    container.insertAdjacentHTML("afterbegin", html);

    const accordions = container.querySelectorAll(":scope > .accordion");
    if (accordions.length > 7) {
        accordions[accordions.length - 1].remove();
    }
}