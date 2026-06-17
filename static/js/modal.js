document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("globalConfirmModal");

    modal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;


        const icon = button.getAttribute("data-modal-icon");
        const color = button.getAttribute("data-modal-color")
        const header = button.getAttribute("data-modal-header");
        const message = button.getAttribute("data-modal-message");
        const action = button.getAttribute("data-modal-action");

        const iconEl = document.getElementById("globalModalIcon");
        const headerEl = document.getElementById("globalModalHeader");
        const messageEl = document.getElementById("globalModalMessage");
        const formEl = document.getElementById("globalModalForm");
        const buttonEl = document.getElementById("globalModalSubmit");

        iconEl.className = `${icon} display-4 text-${color}`;
        headerEl.textContent = header;
        messageEl.innerHTML = message;
        formEl.action = action;
        buttonEl.className = `btn btn-${color} w-100`;
    });
});

