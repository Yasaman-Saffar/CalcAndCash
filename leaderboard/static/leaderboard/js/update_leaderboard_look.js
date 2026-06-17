export function updateLeaderboard(data) {
    const tbody = document.getElementById("leaderboard-body");
    if (!tbody) return;

    const oldRows = [...tbody.querySelectorAll("tr")];

    const firstPositions = new Map();

    oldRows.forEach(row => {
        firstPositions.set(row.dataset.id, row.getBoundingClientRect().top);
    });

    const rowMap = new Map();
    oldRows.forEach(row => {
        rowMap.set(row.dataset.id, row);
    });

    data.forEach(item => {
        const id = String(item.id);
        let row = rowMap.get(id);

        if (!row) {
            row = document.createElement("tr");
            row.dataset.id = id;
        }

        row.innerHTML = `
            <td class="table-warning">${item.rank}</td>
            <td class="table-warning">${item.name}</td>
            <td class="table-warning">${Number(item.score).toFixed(2)}</td>
        `;

        tbody.appendChild(row);
    });

    const newRows = [...tbody.querySelectorAll("tr")];

    newRows.forEach(row => {
        const id = row.dataset.id;
        const firstTop = firstPositions.get(id);
        const lastTop = row.getBoundingClientRect().top;

        if (firstTop === undefined) return;

        const delta = firstTop - lastTop;

        if (Math.abs(delta) > 5) {
            row.style.transition = "none";
            row.style.transform = `translateY(${delta}px)`;

            row.getBoundingClientRect();

            requestAnimationFrame(() => {
                row.style.transition = "transform 1s ease";
                row.style.transform = "translateY(0)";
            });
        }
    });
}