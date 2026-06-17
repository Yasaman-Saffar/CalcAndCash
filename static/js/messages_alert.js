document.querySelectorAll('#messages-container .alert').forEach(alert => {
    setTimeout(() => alert.remove(), 3000);
});

window.showAlert = function(message, type="success") {

    const container = document.getElementById("messages-container");

    const div = document.createElement("div");
    div.className = `alert alert-${type} mt-2`;
    div.setAttribute("role","alert");
    div.innerText = message;

    container.prepend(div);

    setTimeout(() => div.remove(), 3000);
}