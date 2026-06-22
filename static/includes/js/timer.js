let timerInterval = null; // For a countdown, every second
let syncInterval = null; //For synchronization, every 5 minutes
let remainingTime = 0;
let isTimerRuning = false;

// Buttons
let startBtn;
let pWrapper;
let rWrapper;
let resetBtn;

const timerDisplays = document.querySelectorAll('.timer-display');

function format(sec){
    let h = Math.floor(sec / 3600);
    let m = Math.floor((sec % 3600) / 60);
    let s = sec % 60;
    return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

function renderTimer(remaining){
    if (!timerDisplays) return;
    timerDisplays.forEach(el => {
        el.innerText = format(remaining);
    });
}


// Ticker management
function stopTicker() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function startTicker() {
    if(isTimerRuning) return;

    stopTicker();

    isTimerRuning = true;
    timerInterval = setInterval(() => {
        remainingTime--;
        
        if (remainingTime <= 0) {
            remainingTime = 0;
            stopTicker();
            renderTimer(remainingTime);
            fetchTimerData();
        } else {
            renderTimer(remainingTime);
        }
    }, 1000);
}

// Syncing every 5 mins
function stopSync() {
    if(syncInterval){
        clearInterval(syncInterval);
        syncInterval = null;
    }
}

function startSync() {
    stopSync();
    syncInterval = setInterval(() => {
        console.log("Syncing timer...");
        fetchTimerData(); 
    }, 300 * 1000); // 5 minutes in milliseconds
}

function fetchTimerData() {
    fetch("/timer/timer-data/")
        .then(r => r.json())
        .then(data => {

            if (data.status === "timer_not_configured") {
                if (timerDisplays) {
                    timerDisplays.forEach(el => {
                        el.innerText = "--:--:--";
                    });
                }

                return;
            }

            const currentTimeRemaining = data.remaining !== null ? Math.max(0, data.remaining) : 0;
            let shouldStartTicker = false;
            remainingTime = currentTimeRemaining;
            renderTimer(remainingTime);
            
            if(window.USER.is_superuser){
                startBtn = document.getElementById("start_btn");
                pWrapper = document.getElementById("pause_wrapper");
                rWrapper = document.getElementById("resume_wrapper");
                resetBtn = document.getElementById("reset_btn")
            }

            if (data.status === "not-started") {
                stopTicker();
                let duration = data.duration;
                if (remainingTime !== null){
                    renderTimer(remainingTime);
                } else {
                    if (!timerDisplays) return;
                    timerDisplays.forEach(el => {
                        el.innerText = "--:--:--";
                    });
                }

                if(window.USER.is_superuser){
                    startBtn.classList.remove("d-none");
                    pWrapper.classList.add("d-none");
                    rWrapper.classList.add("d-none");
                    resetBtn.classList.add("d-none");
                }
                stopSync();
                return;
            }

            else if (data.status === "paused") {
                stopTicker();

                if(window.USER.is_superuser){
                    startBtn.classList.add("d-none");
                    pWrapper.classList.add("d-none");
                    rWrapper.classList.remove("d-none");
                    resetBtn.classList.add("d-none");
                }
                stopSync();
            }

            else if(data.status === "running") {
                if (remainingTime > 0) {
                    startTicker();
                } else {
                    stopTicker(); 
                    renderTimer(0);
                    fetchTimerData();
                }

                if(window.USER.is_superuser){
                    startBtn.classList.add("d-none");
                    pWrapper.classList.remove("d-none");
                    rWrapper.classList.add("d-none");
                    resetBtn.classList.add("d-none");
                }

                startSync();
            }

            else if(data.status === "finished") {
                if(window.USER.is_superuser){
                    startBtn.classList.add("d-none");
                    pWrapper.classList.add("d-none");
                    rWrapper.classList.add("d-none");
                    resetBtn.classList.remove("d-none");
                }
                stopSync();
            }

            renderTimer(remainingTime);
        });
}

if(window.USER.is_superuser){

    document.getElementById("start_btn").addEventListener("click", () => {
        let btn = document.getElementById("start_btn");
        if (!btn) return;

        fetch(btn.dataset.url, {
            method: "POST",
            headers: {
                "X-CSRFToken": btn.dataset.csrf,
            },
        })
        .then(r => r.json())
        .then(data => {
            if (data.status !== "started") {
                if (!timerDisplays) return;
                timerDisplays.forEach(el => {
                    el.innerText = "--:--:--";
                });
                return;
            }
            fetchTimerData();
        });
    })

    async function handleContestAction(button){
        const url = button.dataset.url;
        const csrf = button.dataset.csrf;

        if(!url){
            console.error("url not found.");
        }

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrf,
                    "X-Requested-With": "XMLHttpRequest"
                },
            });

            if (response.ok) {
                const data = await response.json();
                fetchTimerData();
            } else {
                console.error("error");
            }

        } catch (error) {
            console.error("server error:", error);
        }
    }

    const contestButtons = [
        "pause_btn", 
        "resume_btn", 
        "reset_btn", 
        "fFinish_btn_p", 
        "fFinish_btn_r"  
    ];

    contestButtons.forEach(id => {
        const btnElement = document.getElementById(id);
        if (btnElement) {
            btnElement.addEventListener("click", function() {
                handleContestAction(this);
            });
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    fetchTimerData();
});