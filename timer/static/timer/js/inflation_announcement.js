export function changeInflationStatus(current_inflation){
    const inflation_box = document.getElementById("inflation-value");

    inflation_box.innerHTML = `
        Current Inflation: <strong>${current_inflation.rate}%</strong>
    `;
}