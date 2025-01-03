document.addEventListener("DOMContentLoaded", async () => {
    const db = await initDatabase();
    const pageSize = 50; // Number of rows per page
    let currentPage = 1;

    document.getElementById("apply-filters").addEventListener("click", () => {
        const filters = getFilters();
        currentPage = 1; // Reset to the first page
        updateTable(db, filters, currentPage, pageSize);
    });

    document.getElementById("prev-page").addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            const filters = getFilters();
            updateTable(db, filters, currentPage, pageSize);
        }
    });

    document.getElementById("next-page").addEventListener("click", () => {
        currentPage++;
        const filters = getFilters();
        updateTable(db, filters, currentPage, pageSize);
    });

    // Initial table load
    updateTable(db, getFilters(), currentPage, pageSize);
});

function getFilters() {
    const minionFilter = document.getElementById("minion").value;

    const sortColumn = document.getElementById("sort-column").value;
    const sortOrder = document.getElementById("sort-order").value;

    const ts1 = document.querySelector("#seconds-300").checked || false;
    const ts2 = document.querySelector("#seconds-3600").checked || false;
    const ts3 = document.querySelector("#seconds-21600").checked || false;
    const ts4 = document.querySelector("#seconds-43200").checked || false;
    const ts5 = document.querySelector("#seconds-86400").checked || false;
    const ts6 = document.querySelector("#seconds-172800").checked || false;
    const ts7 = document.querySelector("#seconds-604800").checked || false;
    const ts8 = document.querySelector("#seconds-1209600").checked || false;
    const ts9 = document.querySelector("#seconds-31536000").checked || false;

    const timescales = [
        0, // Always include 0 seconds so if empty, it will return nothing
        ts1 ? 300 : null,
        ts2 ? 3600 : null,
        ts3 ? 21600 : null,
        ts4 ? 43200 : null,
        ts5 ? 86400 : null,
        ts6 ? 172800 : null,
        ts7 ? 604800 : null,
        ts8 ? 1209600 : null,
        ts9 ? 31536000 : null
    ].filter(x => x !== null);

    const fuelMappings = {
        'Enchanted Lava Bucket': 'enchanted-lava-bucket',
        'Magma Bucket': 'magma-bucket',
        'Plasma Bucket': 'plasma-bucket',
        'Hamster Wheel': 'hamster-wheel',
        'Foul Flesh': 'foul-flesh',
        'Everburning Flame': 'everburning-flame',
        'Tasty Cheese': 'tasty-cheese',
        'Catalyst': 'catalyst',
        'Hyper Catalyst': 'hyper-catalyst'
    };

    let fuels = Object.entries(fuelMappings)
        .map(([fuelName, fuelId]) =>
            document.querySelector(`#fuel-${fuelId}`).checked ? fuelName : null
        )
        .filter(f => f !== null);
    if (fuels.length === 0) {
        fuels = [0]
    }

    const upgradeMappings = {
        'Mithril Infusion': 'mithril-infusion',
        'Free Will': 'free-will',
        'Postcard': 'postcard',
        'Beacon': 'beacon',
        'Pet Bonus': 'pet',
        'Crystal' : 'crystal',
    };

    let upgrades = Object.entries(upgradeMappings)
        .map(([upgradeName, upgradeId]) =>
            document.querySelector(`#upgrade-${upgradeId}`).checked ? upgradeName : null
        )
        .filter(u => u !== null);
    if (upgrades.length === 0) {
        upgrades = [0]
    }

    return {
        minion: minionFilter,
        sort: { column: sortColumn, order: sortOrder },
        timescales: timescales,
        upgrades: upgrades,
        fuels: fuels
    };
}

async function initDatabase() {
    const SQL = await initSqlJs({ locateFile: file => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.6.2/${file}` });
    let db_path = "";
    if (window.location.pathname == "/") { // localhost
        db_path = "/data/sheep_minion_combinations.db"
    } else { // server
        db_path = window.location.pathname + "/data/sheep_minion_combinations.db"
    }
    const response = await fetch(db_path);
    const buffer = await response.arrayBuffer();
    return new SQL.Database(new Uint8Array(buffer));
}

function updateTable(db, filters, page, pageSize) {
    const offset = (page - 1) * pageSize;
    let query = "SELECT * FROM MinionSimulationResult WHERE 1=1";

    if (filters.minion && filters.minion != "All") {
        query += ` AND minion LIKE '%${filters.minion}%'`;
    }

    if (filters.timescales && filters.timescales.length > 0) {
        query += ` AND seconds IN (${filters.timescales.join(',')})`;
    }

    if (filters.fuels && filters.fuels.length > 0) {
        query += ` AND fuel IN ('${filters.fuels.join("','")}')`;
    }

    if (!filters.upgrades.includes("Mithril Infusion")) { query += ` AND mithril_infusion = 0`; }
    if (!filters.upgrades.includes("Free Will")) { query += ` AND free_will = 0`; }
    if (!filters.upgrades.includes("Postcard")) { query += ` AND postcard = 0`; }
    if (!filters.upgrades.includes("Beacon")) { query += ` AND beacon_boost_percent = 0`; }
    if (!filters.upgrades.includes("Pet Bonus")) { query += ` AND pet_bonus = 0`; }
    if (!filters.upgrades.includes("Crystal")) { query += ` AND crystal = 0`};


    if (filters.sort) {
        query += ` ORDER BY ${filters.sort.column} ${filters.sort.order}`;
    }

    query += ` LIMIT ${pageSize} OFFSET ${offset}`;
    console.log(query);

    const results = db.exec(query);
    renderTable(results[0]);
}



function fmtMoney(number) {
    // 100 -> $100
    // 1000 -> $1.0k
    // 2500 -> 2.5k
    // 1000000 -> $1.0m
    // 1000000000 -> $1.0b
    if (number < 1000) {
        return `$${number}`;
    } else if (number < 1000000) {
        return `$${(number / 1000).toFixed(1)}K`;
    } else if (number < 1000000000) {
        return `$${(number / 1000000).toFixed(1)}M`;
    } else {
        return `$${(number / 1000000000).toFixed(1)}B`;
    }
}

function fmtSeconds(seconds) {
    if (seconds < 60) {
        return `${seconds}s`;
    } else if (seconds < 3600) {
        return `${seconds / 60}m`;
    } else if (seconds < 86400) {
        return `${seconds / 3600}h`;
    } else {
        return `${seconds / 86400}d`;
    } //else if (seconds < 31536000) {
    //     return `${seconds / 604800}w`;
    // } else {
    //     return `${seconds / 31536000}y`;
    // }
}

function renderTable(result) {
    const tbody = document.querySelector("#results-table tbody");
    tbody.innerHTML = ""; // Clear existing rows

    if (!result) return;

    result.values.forEach(row => {
        const tr = document.createElement("tr");
        let i = 0;
        row.forEach(cell => {
            const td = document.createElement("td");
            if (i == 0) {
                // td.style.fontSize = '0.8em';
                td.textContent = cell;
            } else if (i > 7 && i < 11 || i == 30 || i == 31) {
                td.textContent = cell === 0 ? "" : "T"
            } else if (i == 11 || i==12 || i==13 || i == 15) {
                td.textContent = cell == 0 ? "" : cell + "%"
            } else if (i > 18 && i < 30 || i == 32) {
                td.textContent = fmtMoney(cell);
            } else if (i == 16 || i == 17 || i == 18) {
                td.style.fontSize = '0.50em';
                td.textContent = cell;
            } else if (i == 14) {
                td.textContent = fmtSeconds(cell);
            } else {
                td.textContent = cell;
            }

            if (i == 26 || i == 29) {
            td.style.backgroundColor = '#90EE90';
            }

            tr.appendChild(td);
            i++;
        });
        tbody.appendChild(tr);
    });
}

function updatePaginationControls(db, filters, page, pageSize) {
    const totalRowsQuery = "SELECT COUNT(*) FROM MinionSimulationResult WHERE 1=1";

    let whereClause = "";
    if (filters.minion) {
        whereClause += ` AND minion LIKE '%${filters.minion}%'`;
    }

    const totalRowsResult = db.exec(totalRowsQuery + whereClause);
    const totalRows = totalRowsResult[0]?.values[0][0] || 0;
    const totalPages = Math.ceil(totalRows / pageSize);

    document.getElementById("current-page").textContent = `Page ${page} of ${totalPages}`;
    document.getElementById("prev-page").disabled = page <= 1;
    document.getElementById("next-page").disabled = page >= totalPages;
}
