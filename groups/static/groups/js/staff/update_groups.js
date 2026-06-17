export function updateTable(data){
    const tableBody = document.getElementById("groups-body");
    if (!tableBody) return;

    data.forEach(acc => {
        const row = tableBody.querySelector(`tr[data-id="${acc.id}"]`);
        if(!row) return;

        row.querySelector(".bank_balance").textContent = acc.bank_balance;
        row.querySelector(".items_amount").textContent = acc.items_amount
        row.querySelector(".total_assets").textContent = acc.score
        row.querySelector(".rank").textContent = acc.rank;
        
    });
}