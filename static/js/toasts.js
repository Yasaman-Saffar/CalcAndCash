export function addToastNotif(header, message, time){
    const container = document.getElementById("notif-toast");

    const html = `
        <div class="toast" data-bs-autohide="true">
            <div class="toast-header">
                <strong class="me-auto">${header}</strong>
                <small>${time}</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

    container.insertAdjacentHTML("beforeend", html);

    const toastEl = container.lastElementChild;
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}