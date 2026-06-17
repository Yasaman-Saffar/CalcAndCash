function debounce(func, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

function renderDefaultState(container) {
    container.innerHTML = `
        <li class="list-group-item text-center text-muted py-5 bg-transparent border-0">
            Start typing to search for users
        </li>
    `;
}

function renderLoadingState(container) {
    container.innerHTML = `
        <li class="list-group-item text-center text-muted py-5 bg-transparent border-0">
            <div class="spinner-border spinner-border-sm text-primary me-2"></div>
            Searching...
        </li>
    `;
}

function renderEmptyState(container) {
    container.innerHTML = `
        <li class="list-group-item text-center text-muted py-5 bg-transparent border-0">
            <i class="bi bi-person-x fs-4 d-block mb-2"></i>
            No users found
        </li>
    `;
}

function renderErrorState(container) {
    container.innerHTML = `
        <li class="list-group-item text-center text-danger py-5 bg-transparent border-0">
            Something went wrong. Please try again.
        </li>
    `;
}

function search_user(input) {
    const container = document.getElementById("results");
    const query = input.value.trim();
    const url = input.dataset.url;

    if (query === "") {
        renderDefaultState(container);
        return;
    }

    renderLoadingState(container);

    fetch(url + "?q=" + encodeURIComponent(query))
        .then(res => res.json())
        .then(data => {
            container.innerHTML = "";

            if (!data.results.length) {
                renderEmptyState(container);
                return;
            }

            data.results.forEach(user => {
                const li = document.createElement("li");
                li.className = "list-group-item d-flex justify-content-between align-items-center py-3";

                let actionBtn = "";

                if (user.has_group) {
                    actionBtn = `
                        <span class="badge bg-secondary-subtle text-secondary px-3 py-2">
                            Already in a group
                        </span>
                    `;
                } else if (user.has_invited) {
                    actionBtn = `
                        <span class="badge bg-info-subtle text-info px-3 py-2">
                            Invitation sent
                        </span>
                    `;
                } else {
                    actionBtn = `
                        <button class="btn btn-sm btn-primary"
                                onclick="invite(this, ${user.id})">
                            <i class="bi bi-send"></i> Invite
                        </button>
                    `;
                }

                li.innerHTML = `
                    <div class="d-flex align-items-center gap-3">
                        <div class="bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center"
                             style="width: 40px; height: 40px;">
                            <i class="bi bi-person"></i>
                        </div>
                        <div class="fw-semibold">${user.username}</div>
                    </div>
                    ${actionBtn}
                `;

                container.appendChild(li);
            });
        })
        .catch(() => {
            renderErrorState(container);
        });
}

const debouncedSearch = debounce(search_user, 500);

function invite(button, userId) {
    const inviteInput = document.getElementById("inviteUrl");
    const inviteUrl = inviteInput.dataset.inviteUrl;
    const csrf = inviteInput.dataset.csrf;

    button.disabled = true;
    button.innerHTML = `<span class="spinner-border spinner-border-sm"></span>`;

    fetch(inviteUrl, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrf,
        },
        body: new URLSearchParams({
            user_id: userId,
        }),
    })
        .then(res => res.json())
        .then(data => {
            showAlert(data.message, data.type);

            if (data.type === "success") {
                button.outerHTML = `
                    <span class="badge bg-success-subtle text-success px-3 py-2">
                        Invitation sent
                    </span>
                `;
            } else {
                button.disabled = false;
                button.innerHTML = `<i class="bi bi-send"></i> Invite`;
            }
        })
        .catch(() => {
            button.disabled = false;
            button.innerHTML = `<i class="bi bi-send"></i> Invite`;
        });
}
