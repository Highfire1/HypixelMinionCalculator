async function loadMinionData() {
    try {
        const [minionResponse] = await Promise.all([
            fetch('../data/sheep_minion_combinations.json'),
        ]);
        
        const data = await minionResponse.json();
        createTableHeaders();
        displayMinionData(data);
        displayInfo(data);
        addSortingEventListeners();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

function createTableHeaders() {
    const headerRow = document.querySelector('#minionsTable thead tr');
    headerRow.innerHTML = `
        <th data-column="minion">Minion</th>
        <th data-column="level">Level</th>
        <th data-column="fuel">Fuel</th>
        <th data-column="item1">Item 1</th>
        <th data-column="item2">Item 2</th>
        <th data-column="mi" style="width: min-content">MI.</th>
        <th data-column="fw" style="width: min-content">FW.</th>
        <th data-column="secondsPerAction">Seconds/action</th>
        <th data-column="speedModifier">Speed</th>
        <th data-column="storage">Storage</th>
        <th data-column="hoursUntilFull">Hours <br>until full</th>
        <th data-column="hoursUntilNoFuel">Hours until<br>no fuel</th>
        <th data-column="fuelCostPerDay">$Fuel/<br>day</th>
        <th data-column="revPerDayEhopper">$Rev/day<br> (ehopper)</th>
        <th data-column="profitPerDayEhopper">$Profit/day<br> (ehopper)</th>
        <th data-column="totalOutput" style="text-align: left">Breakdown/day</th>
    `;
}

function addSortingEventListeners() {
    const headers = document.querySelectorAll('#minionsTable thead th');
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.getAttribute('data-column');
            const order = header.getAttribute('data-order') === 'asc' ? 'desc' : 'asc';
            header.setAttribute('data-order', order);
            sortTableByColumn(column, order);
        });
    });
}

function sortTableByColumn(column, order) {
    const table = document.querySelector('#minionsTable tbody');
    const rows = Array.from(table.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aText = a.querySelector(`td[data-column="${column}"]`).textContent;
        const bText = b.querySelector(`td[data-column="${column}"]`).textContent;

        // Remove $ and convert to number if value contains $
        const aValue = aText.includes('$') ? Number(aText.replace('$', '')) : aText;
        const bValue = bText.includes('$') ? Number(bText.replace('$', '')) : bText;

        if (!isNaN(aValue) && !isNaN(bValue)) {
            return order === 'asc' ? aValue - bValue : bValue - aValue;
        } else {
            return order === 'asc' ? aText.localeCompare(bText) : bText.localeCompare(aText);
        }
    });

    rows.forEach(row => table.appendChild(row));
}

function displayMinionData(data) {
    const tableBody = document.getElementById('minionData');
    tableBody.innerHTML = '';
    
    data.forEach(minion => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td data-column="minion">${minion.minion}</td>
            <td data-column="level">${minion.minion_level}</td>
            <td data-column="fuel">${minion.fuel === 'None' ? '' : minion.fuel}</td>
            <td data-column="item1">${minion.item_1 === 'None' ? '' : minion.item_1}</td>
            <td data-column="item2">${minion.item_2 === 'None' ? '' : minion.item_2}</td>
            <td data-column="mi" style="width: min-content">${minion.mithril_infusion ? 'Y' : ''}</td>
            <td data-column="fw" style="width: min-content">${minion.free_will ? 'Y' : ''}</td>
            <td data-column="secondsPerAction">${Number(minion.calculated_seconds_per_action).toFixed(2)}</td>
            <td data-column="speedModifier">${minion.percentage_boost_total}</td>
            <td data-column="storage">${minion.storagetype === 'None' ? '' : minion.storagetype}</td>
            <td data-column="hoursUntilFull">${Number(minion.hours_until_inventory_full).toFixed(1)}</td>
            <td data-column="hoursUntilNoFuel">${minion.hours_until_fuel_runs_out ? Number(minion.hours_until_fuel_runs_out) : ""}</td>
            <td data-column="fuelCostPerDay">${minion.fuel_cost_per_day ? "$"+minion.fuel_cost_per_day : ""}</td>
            <td data-column="revPerDayEhopper">${minion.revenue_per_day_ehopper ? "$"+minion.revenue_per_day_ehopper : ""}</td>
            <td data-column="profitPerDayEhopper" style="padding-right: 12px">${minion.profit_per_day_ehopper ? "$"+minion.profit_per_day_ehopper : ""}</td>
            <td data-column="totalOutput" style="text-align: left">DROPS: ${JSON.stringify(minion.total_output_per_day)}  VALUE: ${JSON.stringify(minion.total_money_per_day)}</td>
        `;
        tableBody.appendChild(row);
    });
}


function displayInfo(data) {
    const infoDiv = document.getElementById('info');
    const numberOfCombinations = data.length;
    infoDiv.innerHTML = `
        <p>Number of combinations: ${numberOfCombinations}</p>
    `;
}

document.addEventListener('DOMContentLoaded', loadMinionData);