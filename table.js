async function initDatabase() {
    const SQL = await initSqlJs({ locateFile: file => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.6.2/${file}` });
    let db_path = "";
    if (window.location.pathname == "/table.html") { // localhost
        db_path = "/data/sheep_minion_combinations.db"
    } else { // server
        db_path = window.location.pathname + "/../data/sheep_minion_combinations.db"
    }
    const response = await fetch(db_path);
    const buffer = await response.arrayBuffer();
    return new SQL.Database(new Uint8Array(buffer));
}

document.addEventListener("DOMContentLoaded", async () => {
    const db = await initDatabase();

    document.getElementById("apply-filters").addEventListener("click", () => {
        const minionTypeElements = document.querySelectorAll("#minion-type input:checked");
        const minionTypes = Array.from(minionTypeElements).map(el => el.value);

        const budgets = [2, 5, 10, 25, 50, 500].map(m => m * 1000000); // Convert to $M
        const frequencies = [86400, 172800, 604800, 1209600, 10713600]; // Hardcoded timescales

        budgets.forEach(budget => {
            frequencies.forEach(frequency => {
                const filters = {
                    minionTypes,
                    budget,
                    frequency
                };

                updateTable(db, filters, budget, frequency);
            });
        });
    });

    // Initial table load
    const budgets = [2, 5, 10, 25, 50, 500].map(m => m * 1000000); // Convert to $M
    const frequencies = [86400, 172800, 604800, 1209600, 10713600]; // Hardcoded timescales

    budgets.forEach(budget => {
        frequencies.forEach(frequency => {
            const filters = {
                minionTypes: ["all"],
                budget,
                frequency
            };

            updateTable(db, filters, budget, frequency);
        });
    });
});

function updateTable(db, filters, budget, frequency) {
    let query = "SELECT * FROM MinionSimulationResult WHERE 1=1";

    if (filters.minionTypes.length > 0 && !filters.minionTypes.includes("all")) {
        const minionTypesCondition = filters.minionTypes.map(type => {
            if (type.includes('-t')) {
                const [minionName, tier] = type.split('-t');
                return `(minion = '${minionName}' AND minion_level = ${tier})`;
            }
            return `minion = '${type}'`;
        }).join(" OR ");
        query += ` AND (${minionTypesCondition})`;
    }

    query += ` AND minion_cost_total <= ${filters.budget}`;
    query += ` AND seconds = ${filters.frequency}`;
    query += ` ORDER BY CASE WHEN profit_24h_if_inventory_instant_sold_to_bz > profit_24h_only_hopper THEN profit_24h_if_inventory_instant_sold_to_bz ELSE profit_24h_only_hopper END DESC`;
    query += ` LIMIT 1`;

    const results = db.exec(query);
    console.log(query)
    renderTable(results[0], budget, frequency);
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

function renderTable(result, budget, frequency) {
    const frequencyMap = {
        86400: '1d',
        172800: '2d',
        604800: '7d',
        1209600: '14d',
        10713600: '124d'
    };

    const minionTypeColors = {
        "Sheep": "#f0e68c", // Light Khaki
        "Slime": "#bdffbd", // Pale Green
        "Tarantula": "#dda0dd", // Plum
        "Clay": "#d3d3d3", // Light Gray
        "Oak": "#deb887", // Burly Wood
        "Magma Cube": "#ffc5c2" 
    };

    // Check if the frequency is valid
    if (!frequencyMap[frequency]) {
        console.error(`Invalid frequency: ${frequency}`);
        return;
    }

    const cellId = `${budget / 1000000}m-${frequencyMap[frequency]}`;
    const cell = document.getElementById(cellId);
    if (!cell) {
        console.error(`Cell with ID ${cellId} not found`);
        return;
    }
    cell.innerHTML = ""; // Clear existing content

    if (!result || result.values.length === 0) {
        return; // No result found, cell remains cleared
    }

    const bestCombination = result.values[0];

    console.log(bestCombination)

    const minionType = "T" + bestCombination[2] + " " + bestCombination[1] + " Minion";
    
    const upgrades = [
        bestCombination[7] && `${bestCombination[7]} storage`,
        bestCombination[8] && "infused",
        bestCombination[9] && "free will",
        bestCombination[10] && "postcard",
        bestCombination[11] && `beacon: ${bestCombination[11]}%`
    ].filter(Boolean).join(", ");

    const fuel = bestCombination[3]

    const items = bestCombination.slice(5, 7).filter(item => item).join(", ");
    
    
    const instantSellProfit = bestCombination[26];
    const ehopperProfit = bestCombination[29];
    let optimalPerDay;
    let payoff_days;

    if (instantSellProfit > (ehopperProfit * 1.11)) {
        optimalPerDay = `${fmtMoney(instantSellProfit)}/day (sell to bz)`;
        payoff_days = bestCombination[34] / instantSellProfit
    } else {
        optimalPerDay = `${fmtMoney(ehopperProfit)}/day (ehopper)`;
        payoff_days = bestCombination[34] / ehopperProfit
    }
    console.log(instantSellProfit, (ehopperProfit * 1.11))

    payoff_days = payoff_days.toFixed(0)
    
    
    const setupCost = fmtMoney(bestCombination[34]);

    // Set the background color based on the minion type
    const minionBaseType = bestCombination[1];
    const backgroundColor = minionTypeColors[minionBaseType] || "#ffffff"; // Default to white if not found
    cell.style.backgroundColor = backgroundColor;

    cell.innerHTML = `
        <span>
            <strong>${optimalPerDay}</strong><br>
            ${minionType}<br>
            
            ${fuel && `<span style="font-size: 0.9em">${fuel}</span><br>`}
            ${items && `<span style="font-size: 0.9em">${items}</span><br>`}
            ${upgrades && `<span style="font-size: 0.9em">${upgrades}</span><br>`}
            <span style="font-size: 0.9em">Cost/minion: ${setupCost} (${payoff_days}d payback)</span>
        </span>
    `;
}