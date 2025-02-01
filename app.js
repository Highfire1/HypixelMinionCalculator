function controlFromInput(fromSlider, fromInput, toInput, controlSlider) {
    const [from, to] = getParsed(fromInput, toInput);
    fillSlider(fromInput, toInput, '#C6C6C6', '#25daa5', controlSlider);
    if (from > to) {
        fromSlider.value = to;
        fromInput.value = to;
    } else {
        fromSlider.value = from;
    }
}
    
function controlToInput(toSlider, fromInput, toInput, controlSlider) {
    const [from, to] = getParsed(fromInput, toInput);
    fillSlider(fromInput, toInput, '#C6C6C6', '#25daa5', controlSlider);
    setToggleAccessible(toInput);
    if (from <= to) {
        toSlider.value = to;
        toInput.value = to;
    } else {
        toInput.value = from;
    }
}

function controlFromSlider(fromSlider, toSlider, fromInput) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
  if (from > to) {
    fromSlider.value = to;
    fromInput.value = to;
  } else {
    fromInput.value = from;
  }
}

function controlToSlider(fromSlider, toSlider, toInput) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
  setToggleAccessible(toSlider);
  if (from <= to) {
    toSlider.value = to;
    toInput.value = to;
  } else {
    toInput.value = from;
    toSlider.value = from;
  }
}

function getParsed(currentFrom, currentTo) {
  const from = parseInt(currentFrom.value, 10);
  const to = parseInt(currentTo.value, 10);
  return [from, to];
}

function fillSlider(from, to, sliderColor, rangeColor, controlSlider) {
    const rangeDistance = to.max-to.min;
    const fromPosition = from.value - to.min;
    const toPosition = to.value - to.min;
    controlSlider.style.background = `linear-gradient(
      to right,
      ${sliderColor} 0%,
      ${sliderColor} ${(fromPosition)/(rangeDistance)*100}%,
      ${rangeColor} ${((fromPosition)/(rangeDistance))*100}%,
      ${rangeColor} ${(toPosition)/(rangeDistance)*100}%, 
      ${sliderColor} ${(toPosition)/(rangeDistance)*100}%, 
      ${sliderColor} 100%)`;
}

function setToggleAccessible(currentTarget) {
  const toSlider = document.querySelector('#toSlider');
  if (Number(currentTarget.value) <= 0 ) {
    toSlider.style.zIndex = 2;
  } else {
    toSlider.style.zIndex = 0;
  }
}

const fromSlider = document.querySelector('#fromSlider');
const toSlider = document.querySelector('#toSlider');
const fromInput = document.querySelector('#fromInput');
const toInput = document.querySelector('#toInput');
fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
setToggleAccessible(toSlider);

fromSlider.oninput = () => controlFromSlider(fromSlider, toSlider, fromInput);
toSlider.oninput = () => controlToSlider(fromSlider, toSlider, toInput);
fromInput.oninput = () => controlFromInput(fromSlider, fromInput, toInput, toSlider);
toInput.oninput = () => controlToInput(toSlider, fromInput, toInput, toSlider);


document.addEventListener("DOMContentLoaded", async () => {
    const db = await initDatabase();
    const pageSize = 50; // Number of rows per page
    let currentPage = 1;

    
    const fromSlider = document.getElementById("fromSlider");
    const toSlider = document.getElementById("toSlider");
    const fromInput = document.getElementById("fromInput");
    const toInput = document.getElementById("toInput");

    fromSlider.oninput = () => controlFromSlider(fromSlider, toSlider, fromInput);
    toSlider.oninput = () => controlToSlider(fromSlider, toSlider, toInput);
    fromInput.oninput = () => controlFromInput(fromSlider, fromInput, toInput, toSlider);
    toInput.oninput = () => controlToInput(toSlider, fromInput, toInput, toSlider);

    document.getElementById("apply-filters").addEventListener("click", () => {
        const filters = getFilters();
        currentPage = 1; // Reset to the first page
        updateTable(db, filters, currentPage, pageSize);
    });


    // Set initial state for calculations checkbox
    const showCalculations = document.getElementById("show-calculations");
    showCalculations.checked = false; // or true depending on desired default

    // Trigger initial state
    const event = new Event('change');
    showCalculations.dispatchEvent(event);

    const showOtherProfits = document.getElementById("show-profits");
    showOtherProfits.checked = false;

    // Trigger initial state
    const event2 = new Event('change');
    showOtherProfits.dispatchEvent(event2);


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

    // Add to document.addEventListener("DOMContentLoaded", async () => {
    // Run once with current checkbox state
    const e = { target: document.getElementById("show-calculations") };
    const calculationColumns = document.querySelectorAll('th.calculation-column, td.calculation-column');
    calculationColumns.forEach(col => {
        if (e.target.checked) {
            col.classList.remove('hidden');
        } else {
            col.classList.add('hidden');
        }
    });

    const e2 = { target: document.getElementById("show-profits") };
    const profitColumns = document.querySelectorAll('th.profit-column, td.profit-column');
    profitColumns.forEach(col => {
        if (e2.target.checked) {
            col.classList.remove('hidden');
        } else {
            col.classList.add('hidden');
        }
    });

// Initial table load
updateTable(db, getFilters(), currentPage, pageSize);
});

const allItems = [
    { id: "item-minion-expander", name: "Minion Expander" },
    { id: "item-flycatcher", name: "Flycatcher" },
    { id: "item-diamond-spreading", name: "Diamond Spreading" },
    { id: "item-corrupt-soil", name: "Corrupt Soil" },
    { id: "item-berberis-fuel-injector", name: "Berberis Fuel Injector" },
    { id: "item-super-compactor", name: "Super Compactor 3000" },
  ];

function getFilters() {
    const minionFilter = document.getElementById("minion").value;

    const sortColumn = document.getElementById("sort-column").value;
    const sortOrder = document.getElementById("sort-order").value;

    const minCost = fromSlider.value * 1000000;
    const maxCost = toSlider.value * 1000000;

    const ts1 = document.querySelector("#seconds-300").checked || false;
    const ts2 = document.querySelector("#seconds-86400").checked || false;
    const ts3 = document.querySelector("#seconds-172800").checked || false;
    const ts4 = document.querySelector("#seconds-604800").checked || false;
    const ts5 = document.querySelector("#seconds-1209600").checked || false;
    const ts6 = document.querySelector("#seconds-10713600").checked || false;
    
    const timescales = [
        0, // Always include 0 seconds so if empty, it will return nothing
        ts1 ? 300 : null,
        ts2 ? 86400 : null,
        ts3 ? 172800 : null,
        ts4 ? 604800 : null,
        ts5 ? 1209600 : null,
        ts6 ? 10713600 : null,
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
        'Crystal': 'crystal',
    };

    let upgrades = Object.entries(upgradeMappings)
        .map(([upgradeName, upgradeId]) =>
            document.querySelector(`#upgrade-${upgradeId}`).checked ? upgradeName : null
        )
        .filter(u => u !== null);
    if (upgrades.length === 0) {
        upgrades = [0]
    }

    const selectedItems = [];
    const unselectedItems = [];
    allItems.forEach((item) => {
        const checkbox = document.getElementById(item.id);
        if (checkbox && checkbox.checked) {
        selectedItems.push(item.name);
        } else {
        unselectedItems.push(item.name);
        }
    });

    return {
        minion: minionFilter,
        sort: { column: sortColumn, order: sortOrder },
        timescales: timescales,
        upgrades: upgrades,
        unselectedItems: unselectedItems,
        fuels: fuels,
        minCost: minCost,
        maxCost: maxCost
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

    filters.unselectedItems.forEach((item) => {
        query += ` AND item_1 != '${item}' AND item_2 != '${item}'`;
      });

    if (!filters.upgrades.includes("Mithril Infusion")) { query += ` AND mithril_infusion = 0`; }
    if (!filters.upgrades.includes("Free Will")) { query += ` AND free_will = 0`; }
    if (!filters.upgrades.includes("Postcard")) { query += ` AND postcard = 0`; }
    if (!filters.upgrades.includes("Beacon")) { query += ` AND beacon_boost_percent = 0`; }
    if (!filters.upgrades.includes("Pet Bonus")) { query += ` AND pet_bonus_percent = 0`; }
    if (!filters.upgrades.includes("Crystal")) { query += ` AND crystal_bonus_percent = 0` };

    
    if (filters.minCost !== undefined && filters.maxCost !== undefined) {
        query += ` AND minion_cost_total BETWEEN ${filters.minCost} AND ${filters.maxCost}`;
    }

    

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
    const e = { target: document.getElementById("show-calculations") };
    const calculationColumns = document.querySelectorAll('th.calculation-column, td.calculation-column');
    calculationColumns.forEach(col => {
        if (e.target.checked) {
            col.classList.remove('hidden');
        } else {
            col.classList.add('hidden');
        }
    });

    const e2 = { target: document.getElementById("show-profits") };
    const profitColumns = document.querySelectorAll('th.profit-column, td.profit-column');
    profitColumns.forEach(col => {
        if (e2.target.checked) {
            col.classList.remove('hidden');
        } else {
            col.classList.add('hidden');
        }
    });
    
    const tbody = document.querySelector("#results-table tbody");
    tbody.innerHTML = ""; // Clear existing rows
    tbody.style.fontSize = '0.8em';

    if (!result) return;

    result.values.forEach(row => {
        const tr = document.createElement("tr");
        let i = 0;
        const showCalculations = document.getElementById("show-calculations").checked;
        const calculationIndexes = [16, 17, 18, 19, 20, 21, 22, 23, 24];

        const showOtherProfits = document.getElementById("show-profits").checked;
        const profitIndexes = [25, 27, 28]

        row.forEach((cell, index) => {
            const td = document.createElement("td");
            if (calculationIndexes.includes(index)) {
                td.classList.add('calculation-column');
                if (!showCalculations) {
                    td.classList.add('hidden');
                }
            }

            if (profitIndexes.includes(index)) {
                td.classList.add('profit-column');
                if (!showOtherProfits) {
                    td.classList.add('hidden');
                }
            }

            if (i == 0) {
                // td.style.fontSize = '0.8em';
                td.textContent = cell;
            } else if (i > 7 && i < 11 || i == 32 || i == 33) {
                td.textContent = cell === 0 ? "" : "T"
            } else if (i == 11 || i == 12 || i == 13 || i == 15) {
                td.textContent = cell == 0 ? "" : cell + "%"
            } else if (i >= 34) {
                td.textContent = fmtMoney(cell);
            } else if (i == 16 || i == 17 || i == 18) {
                td.style.fontSize = '0.75em';
                td.textContent = cell;
            } else if (i == 14) {
                td.textContent = fmtSeconds(cell);

            } else if (i > 18 && i < 25 ) {
                td.textContent = fmtMoney(cell);

            } else if (i >= 25 && i < 30) {
                // const apr = ((cell*365) / row[32]) * 100;
                // td.innerHTML = `${fmtMoney(cell)}<br>(${apr.toFixed(0)}% APR)`;
                td.textContent = fmtMoney(cell);
            } else if (i == 30 || i == 31) {
                td.textContent = `${cell}%`;
            } else {
                td.textContent = cell;
            }

            if (i == 26 || i == 29) {
                td.style.backgroundColor = '#90EE90';
            }

            if (i == 34) {
                td.style.backgroundColor = '#ffcccd';
            }
            
            if (i != 0 || false) {
                tr.appendChild(td);
            }
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
