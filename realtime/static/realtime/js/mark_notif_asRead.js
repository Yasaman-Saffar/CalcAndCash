document.addEventListener("click", function (e) {

    const btn = e.target.closest(".read_message_btn");
    if(!btn) return;

    if(btn.dataset.read === "1"){
        return;
    }

    fetch("/realtime/mark-notif-asRead/", {
        method: "POST",
        headers: {
            "X-CSRFToken": btn.dataset.csrf,
        },
        body: new URLSearchParams({
            "notif_id": btn.dataset.id,
        }),
    })
    .then(res => res.json()) 
    .then(data => {
        if (data.success === true) {
            console.log("marked as read");

            const badge = btn.querySelector(".bg-danger");
            if (badge) badge.remove();

            btn.dataset.read = "1";
        } else {
            console.error("server error");
        }
    })
    .catch(err => {
        console.error("network error:", err);
    });

});
