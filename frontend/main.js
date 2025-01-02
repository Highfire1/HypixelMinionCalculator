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
    
    // Base columns
    let headers = `
        <th data-column="minion">Minion</th>
        <th data-column="level">Level</th>
        <th data-column="fuel">Fuel</th>
        <th data-column="hopper">Hopper</th>
        <th data-column="item1">Item 1</th>
        <th data-column="item2">Item 2</th>
        <th data-column="storage">Storage</th>
        <th data-column="mi">MI</th>
        <th data-column="fw">FW</th>
        <th data-column="postcard">PC</th>
        <th data-column="beaconBoost">Beacon %</th>
        <th data-column="speedModifier">Speed %</th>`;

    // Add columns for each time period
    const timePeriods = ["1m", "30m", "1h", "12h", "24h", "48h", "7d", "14d", "120d", "365d"];
    timePeriods.forEach((period, index) => {
        headers += `
            <th data-column="hopper_${index}">Hopper $ (${period})</th>
            <th data-column="npc_${index}">NPC $ (${period})</th>
            <th data-column="fuel_${index}">Fuel Cost<br>(${period})</th>
            <th data-column="total_${index}">Total $ (${period})</th>`;
    });

    headerRow.innerHTML = headers;
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
        
        // Base minion data
        let html = `
            <td data-column="minion">${minion.minion}</td>
            <td data-column="level">${minion.minion_level}</td>
            <td data-column="fuel">${minion.fuel || ''}</td>
            <td data-column="hopper">${minion.hopper || ''}</td>
            <td data-column="item1">${minion.item_1 || ''}</td>
            <td data-column="item2">${minion.item_2 || ''}</td>
            <td data-column="storage">${minion.storagetype || ''}</td>
            <td data-column="mi">${minion.mithril_infusion ? 'Y' : ''}</td>
            <td data-column="fw">${minion.free_will ? 'Y' : ''}</td>
            <td data-column="postcard">${minion.postcard ? 'Y' : ''}</td>
            <td data-column="beaconBoost">${minion.beacon_percent_boost}</td>
            <td data-column="speedModifier">${minion.time_combinations[0].percentage_boost}</td>`;

        // Add data for each time period
        minion.time_combinations.forEach((combo, index) => {
            html += `
                <td data-column="hopper_${index}">$${combo.hopper_coins}</td>
                <td data-column="npc_${index}">$${combo.coins_if_inventory_sold_to_npc}</td>
                <td data-column="fuel_${index}">$${combo.cost_of_fuel}</td>
                <td data-column="total_${index}">$${combo.hopper_coins+combo.coins_if_inventory_sold_to_npc-combo.cost_of_fuel}</td>`;
        });

        row.innerHTML = html;
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