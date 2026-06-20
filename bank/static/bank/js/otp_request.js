function start_otp_timer(btn, timeout){
    btn.disabled = true;
    btn.innerHTML = timeout

    const countdown = setInterval(() => {
        timeout -= 1;
        btn.innerHTML = timeout;

        if(timeout <= 0){
            clearInterval(countdown);
            btn.innerHTML ="Request OTP";
            btn.disabled = false;
        }
    }, 1000)
}

document.getElementById("otp-btn")?.addEventListener("click", () => {
    let btn = document.getElementById("otp-btn");
    const buyer = document.getElementById("id_buyer").value;

    fetch(btn.dataset.url, {
            method: "POST",
            headers: {
                "X-CSRFToken": btn.dataset.csrf,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                buyer: buyer,
            }),
        })
        .then(response => response.json())
        .then(data => {
            showAlert(data.message, data.type);
            if(data.timeout){
                start_otp_timer(btn, data.timeout)
            }
        })
        .catch(() => {
            showAlert("Failed to request OTP. Please try again.", "danger");
        });
});


// showing the otp remaining time
document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("otp-btn");
    if (otpRemaining > 0){
        start_otp_timer(btn, otpRemaining)
    }
});
