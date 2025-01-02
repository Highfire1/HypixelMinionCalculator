"""
FAQ:

 Q: Where are Farming Crystal and Pet Boosts
 A: THEY ARE NOW INCLUDED IN AFK CALCULATIONS? 
 THERE IS NO LONGER A NEED to AFK on your island for these bonuses to apply.
 However, you must make sure that your pet is equipped.
 (this also includes postcard)

 q: where inferno minion?
 It's too complicated for this interface, use the page on the wiki: https://hypixel-skyblock.fandom.com/wiki/User:Voball/Sandbox-Inferno_Minions


"""

from dataclasses import dataclass
import json
from typing import List
import requests

from bazaar import SkyblockItems


from minion_data import (
    MinionBase,
    MinionFuelType,
    MinionItemType,
    MinionStorageType,
    MINIONS,
    FUEL_TYPES,
    ITEMS,
    STORAGES,
)

from item_data import (
    # SMELT_MAP,
    # COMPACTOR_MAP,
    # SUPER_COMPACTOR_MAP,
    is_smeltable,
    convert_to_smelted,
    is_compactable,
    convert_to_compacted,
    is_super_compactable, 
    convert_to_super_compacted,
)


@dataclass
class Playstyle:
    short_name: str
    name: str
    eligible_minions: list[str]
    one_cycle: bool = False

# ["EH", "SA-CA", "SA-CC", "SA-FL", "ID-SS", "ID-SH", "AC-SH"]

PLAYSTYLES:list[Playstyle] = [
    # you will not check or load your minions. Profits will only be calculated using the enchanted hopper.
    # IT IS POSSIBLE THAT CRYSTAL AND PET BONUS CAN BE CALCULATED AFK NOW
    Playstyle("EH", "not active (enchanted hopper only)", ["all"]),
    # applies to all combinations

    # you will login before the third compaction level is reached
    # if 3 levels exist e.g. iron, enchanted iron, enchanted iron block
    # then we will create a combination that avoids ench iron block, and a setup that avoids enchanted iron
    # to find the best coin/time compaction level item to sell to the bazaar
    Playstyle("SA-CA", "semi-active (compactor avoid compaction)", ["all"]),
    # applies only when compactor in items
    
    # similar to the above, but
    # this case is specifically for compactor + corrupted soil
    # because compacted items have priority over compacted items
    # so it is possible to keep the compacted items, while corrupted soil outputs get sold by enchanted hopper
    # to sell the second compaction level items to the bazaar
    Playstyle("SA-CC", "semi-active (compactor avoid compaction and ehopper corrupted soil)", ["all"]),
    # applies only when compactor/variants + corrupted soil in items
    
    # you will login before min(inventory_full, fuel_runs_out) 
    # to sell the items to the bazaar
    Playstyle("SA-FL", "semi-active (avoid full inventory/empty fuel)", ["all"]),
    # applies to all combinations
    
    # you will idle on your island to activate the crystal and pet bonus if they exist for that minion
    # skyblock should calculate this properly now
    # Playstyle("idle (24/7)", ["all"]),
    
    
    # you idle on your island and automate spawning (this doubles drops)
    # this works for Melon, Pumpkin, Cobblestone, Ice, Mycelium, and Flowers
    Playstyle("ID-SS", "idle (non-minion spawning)", ["Melon", "Pumpkin", "Cobblestone", "Ice", "Mycelium"], True),
    # these can be safely ignored because these minions are dogwater regardless
    
    
    # you idle on your island and automate harvesting (this doubles drops)
    # to my knowledge, 
    # this only works for flower minions
    # (minions don't take drop damage, witherborn patched, etc)
    Playstyle("ID-SH", "idle (non-minion harvest)", ["Flowers"], True),
    
    
    # you harvest the minion output yourself (why would you do this?...)
    # this is more nostalgia for the potato war days than out of any optimization opportunity
    # combat: you would have to be in some sort of super niche situation
    # farming: no farming fortune... and there is garden now
    # farming: maybe helpful for some farming spawned minions??
    # fishing: no, clay would barely work, fishing is not automable
    # mining: absolutely not
    # slayer: maybe? i doubt it
    # foraging: no, bone meal farms exist
    # Playstyle("AC-SH", "active (non-minion harvest)", ["clay"], True),
    # unimplemented for now because its complicated and not useful for MVP
]

# DATA VALIDATION:
for fuel in FUEL_TYPES:
    if fuel.name == "None":
        pass
    elif fuel.special_case:
        assert not fuel.percentage_boost
    else:
        assert fuel.percentage_boost

# TODO: validate assumptions for other types to ensure there are no mistakes in data entry



@dataclass
class MinionOutputs:
    # base info about the minion
    id: str
    playstyle: str
    minion: str
    minion_level: int
    
    fuel: str
    item_1: str
    item_2: str
    
    storagetype: str
    inventory_slots: int
    
    mithril_infusion: bool
    free_will: bool
    
    seconds_per_action: int
    calculated_seconds_per_action: float
    percentage_boost_total: int
    
    # base minion outputs
    outputs_per_cycle: dict[str, float]
    outputs_per_day: dict[str, float]
    
    total_output_per_day: dict[str, float]
    
    total_money_per_day_npc: dict[str, float]
    total_money_per_day_bz: dict[str, float]
    total_money_per_day_optimal: dict[str, float]
    
    # some calculated helpers
    hours_until_fuel_runs_out: None | int
    hours_until_inventory_full: int
    
    fuel_cost_per_day: None | float
    
    
    
    # playstyle specific values
    EH_revenue_per_day_ehopper: None | float = None # DOES NOT INCLUDE FUEL COST
    
    SA_CA_compaction_level: None | int = None
    SA_CA_hours_before_unwanted_compaction: None | float = None
    
    SA_CC_compaction_level: None | int = None
    SA_CC_hours_before_unwanted_compaction: None | float = None
    SA_CC_hours_before_non_fragsulphur_inventory_full: None | float = None
    
    SA_FL_hours_before_inventory_full: None | float = None
    
    # generated from playstyle:
    total_output_per_day_compacted: dict[str, float] = {}
    total_output_per_day_non_compacted: dict[str, float] = {}
    
    # depending on the playstyle, we will populate these differently
    # EH sends all items to sold_to_ehopper
    # semi-active compact avoid compaction 
    sold_to_npc: dict[str, float] = {}
    sold_to_bz_sell_order: dict[str, float] = {}
    sold_to_bz_instant_sell: dict[str, float] = {}
    sold_to_enchanted_hopper: dict[str, float] = {}
    
    # if island is loaded
    # very quick (no compactor)
    # before first compaction level is reached (e.g. enchanted iron)
    # before second compaction level is reached (e.g. enchanted iron block)
    # before fuel runs out
    # before inventory is full
    
    # if island is not loaded
    
    
    # collection_frequency:
    # very quick (no compactor)
    # 
    # never (enchanted hopper)
    
    # values across playstyles
    global_hours_until_non_optimal_output: None | float = None
    global_revenue_per_day_optimal: None | float = None # DOES NOT INCLUDE FUEL COST
    
    
    
    
    # playstyle("EH", "not active (enchanted hopper only)", ["all"]),
    # applies to all combinations

    # you will login before the third compaction level is reached
    # if 3 levels exist e.g. iron, enchanted iron, enchanted iron block
    # then we will create a combination that avoids ench iron block, and a setup that avoids enchanted iron
    # to find the best coin/time compaction level item to sell to the bazaar
    # Playstyle("SA-CA", "semi-active (compactor avoid compaction)", ["all"]),
    # applies only when compactor in items
    
    # similar to the above, but
    # this case is specifically for compactor + corrupted soil
    # because compacted items have priority over compacted items
    # so it is possible to keep the compacted items, while corrupted soil outputs get sold by enchanted hopper
    # to sell the second compaction level items to the bazaar
    # this will also create a unique combination for each compaction level
    # Playstyle("SA-CC", "semi-active (compactor avoid compaction and ehopper corrupted soil)", ["all"]),
    # applies only when compactor/variants + corrupted soil in items
    
    # you will login before min(inventory_full, fuel_runs_out) 
    # to sell the items to the bazaar
    # Playstyle("SA-FL", "semi-active (avoid full inventory/empty fuel)", ["all"]),
    # applies to all combinations
    
    
    # you idle on your island and automate spawning (this doubles drops)
    # this works for Melon, Pumpkin, Cobblestone, Ice, Mycelium, and Flowers
    # Playstyle("ID-SS", "idle (non-minion spawning)", ["Melon", "Pumpkin", "Cobblestone", "Ice", "Mycelium", "Flowers"], True),
    
    
    # you idle on your island and automate harvesting (this doubles drops)
    # to my knowledge, 
    # this only works for flower minions
    # (minions don't take drop damage, witherborn patched, etc)
    # Playstyle("ID
    
    
    
    # min(fuel_runs_out, hours_until_compactor condition is no longer true)
    SA_compaction_level: None | int = None
    SA_hours_before_non_optimal_output: None | float = None
    SA_revenue_per_day_optimal: None | float = None # DOES NOT INCLUDE FUEL COST
    
    ID_revenue_per_day_optimal: None | float = None # DOES NOT INCLUDE FUEL COST
    
    minion_cost: int = 0

    def clean_clamp(self):
        if self.EH_revenue_per_day_ehopper:
            self.EH_revenue_per_day_ehopper = int(self.EH_revenue_per_day_ehopper)



combinations:list[MinionOutputs] = []

# get data of skyblock items
skyblock_items = SkyblockItems()


"""
TBD: confirm that catalyst affects minion outputs, but not diamond spreadings outputs
"""
def calculate_minion_outputs(minion:MinionBase, minion_level: int, playstyle:Playstyle, fuel:MinionFuelType, item_1:MinionItemType, item_2:MinionItemType, storage:MinionStorageType, mithril_infusion:bool, free_will:bool) -> MinionOutputs:
    hours_until_fuel_runs_out = -999999999999
    hours_until_inventory_full = -999999999999
    inventory_slots_required_for_crafting = 0
    
    outputs_per_cycle:dict[str, float] = {}
    outputs_per_day:dict[str, float] = {}
    minion_speed_percentage = 100
    inventory_slots = minion.levels[minion_level-1].inventory_slots + storage.inventory_slots
    
    
    for action in minion.actions:
        if action.drops:
            for drop in action.drops:
                if drop.item not in outputs_per_cycle:
                    outputs_per_cycle[drop.item] = 0
                outputs_per_cycle[drop.item] += drop.amount * (drop.percentage/100)
    
    # handle minion upgrades
    if mithril_infusion:
        minion_speed_percentage += 10
    if free_will:
        minion_speed_percentage += 10
    
    
    # handle fuel
    if not fuel.special_case:
        minion_speed_percentage += fuel.percentage_boost
        
    elif fuel.name == "Everburning Flame":
        minion_speed_percentage += 35
        if minion.skill_type == "combat":
            minion_speed_percentage += 5
    
    elif fuel.name == "Tasty Cheese":
        for item in outputs_per_cycle:
            outputs_per_cycle[item] *= 2
    
    elif fuel.name == "Catalyst":
        for item in outputs_per_cycle:
            outputs_per_cycle[item] *= 3
            
    elif fuel.name == "Hyper Catalyst":
        for item in outputs_per_cycle:
            outputs_per_cycle[item] *= 4
    
    
    
    # handle items    
    for item in [item_1, item_2]:
        
        if not item.special_case:
            if item.percentage_boost:
                minion_speed_percentage += item.percentage_boost
        
        elif item.name == "Diamond Spreading":
            # one diamond is generated for every 10 items (on average)
            # TODO: verify double diamond spreading calculation
            if item_1 == item_2: # if there are two diamond spreadings
                outputs_per_cycle["Diamond"] = ( sum(outputs_per_cycle.values()) / 10 ) * 2
            else:
                outputs_per_cycle["Diamond"] = sum(outputs_per_cycle.values()) / 10
        
        # TODO: check if lesser soulflow and souflow engine can stack
    
        elif item.name == "Lesser Soulflow Engine":
            minion_speed_percentage = minion_speed_percentage*0.5 # IS THIS CORRECT???
            # one soulflow is generated every 3 minutes (180 seconds)
            outputs_per_day["soulflow"] = 86400/180 # (480 soulflow/day)
        
        elif item.name == "Soulflow Engine":
            minion_speed_percentage = minion_speed_percentage*0.5 # IS THIS CORRECT???
            # one soulflow is generated every 1.5 minutes (90 seconds)
            outputs_per_day["Soulflow"] = 86400/90 # (960 soulflow/day)
            if minion.name == "Voidling":
                minion_speed_percentage += (3 * minion_level)
        
        # turns mobs into their corrupted forms
        # only works on mob-spawning minions
        elif item.name == "Corrupt Soil":
            if "Corrupted Fragment" not in outputs_per_cycle:
                outputs_per_cycle["Corrupted Fragment"] = 0
            if "Sulphur" not in outputs_per_cycle:
                outputs_per_cycle["Sulphur"] = 0
            
            for action in minion.actions:
                if action.drops:
                    # apparently slimes get to be special
                    if minion.name == "Slime":
                        for drop in action.drops:
                            outputs_per_cycle["Corrupted Fragment"] += 1 * (drop.percentage / 100)
                            outputs_per_cycle["Sulphur"] += 1 * (drop.percentage / 100)
                    # and everyone else gets 1
                    else:
                        outputs_per_cycle["Corrupted Fragment"] = 1
                        outputs_per_cycle["Sulphur"] = 1
                        
        elif item.name == "Berberis Fuel Injector":
            # one berberis is generated every 5 minutes (300 seconds)
            minion_speed_percentage += 15
            outputs_per_day["Lush Berberis"] = 86400/300
            
            
        # TODO: enchanted shears, enchanted egg, flint shovel
        
        # auto smelter, compactor, super compactor 3000, super dwarven compactor
        elif item.name == "Auto Smelter":
            for item in outputs_per_cycle:
                if is_smeltable(item):
                    outputs_per_cycle[convert_to_smelted(item)] = outputs_per_cycle[item]
                    del outputs_per_cycle[item]
        
        elif item.name == "Compactor":
            for item in list(outputs_per_cycle.keys()):
                if is_compactable(item):
                    # if we create 1 clay per action, and it takes 4 clay to make a clay block
                    # then we produce 0.25 (1/4) clay blocks per action
                    converted_item = convert_to_compacted(item)
                    outputs_per_cycle[converted_item.output_item] = outputs_per_cycle[item] / converted_item.input_count
                    del outputs_per_cycle[item]
                    inventory_slots_required_for_crafting += 1
        
        # note: this only applies super compaction once
        elif item.name == "Super Compactor 3000":
            for item in list(outputs_per_cycle.keys()):
                if is_super_compactable(item):
                    converted_item = convert_to_super_compacted(item)
                    outputs_per_cycle[converted_item.output_item] = outputs_per_cycle[item] / converted_item.input_count
                    del outputs_per_cycle[item]
                    inventory_slots_required_for_crafting += 1
        
        
    # calculate outputs per day and hours until inventory full
    # note that we show the time when the minion gets an item, and doesn't have a slot for it.
    # a minion may continue limited harvesting other items at this point
    
    # Calculate time reduction based on percentage boost
    # 10s per action and 150% speed -> 10 / (150/100) -> 10 / 1.5 -> 6.666666666666667
    # 10s per action and 200% speed -> 10 / (200/100) -> 10 / 2 -> 5
    # currently, the greatest possible percentage boost is somewhere around 220%
        
    multiplier = (minion_speed_percentage) / 100
    seconds_per_action = minion.levels[minion_level-1].seconds_per_action / multiplier
    
    seconds_per_harvest = seconds_per_action
    if not playstyle.one_cycle:
        seconds_per_harvest *= 2 # because every minion has a spawning / harvesting action
    
    
    total_output_per_day = outputs_per_day.copy()
    for output in outputs_per_cycle:
        if output not in total_output_per_day:
            total_output_per_day[output] = 0
        total_output_per_day[output] += outputs_per_cycle[output] * (86400 / seconds_per_harvest)
    
    total_money_per_day_npc = {}
    for output in total_output_per_day:
        item = skyblock_items.search_by_name(output)
        assert item
        total_money_per_day_npc[output] = int(item.npc_sell_price * total_output_per_day[output])
    
    total_money_per_day_bz = {}
    for output in total_output_per_day:
        item = skyblock_items.search_by_name(output)
        assert item
        total_money_per_day_bz[output] = int(item.bz_buy_price * total_output_per_day[output])
    
    total_money_per_day_optimal = {}
    for output in total_output_per_day:
        item = skyblock_items.search_by_name(output)
        assert item
        total_money_per_day_optimal[output] = max(int(item.bz_buy_price * total_output_per_day[output]), int(item.npc_sell_price * total_output_per_day[output]))
    
    
    if fuel.duration_hours:
        hours_until_fuel_runs_out = fuel.duration_hours * 64
    else:
        hours_until_fuel_runs_out = None
    
    # calculate how long until the inventory is full
    # calculate total items per day
    total_items_per_day = sum(total_output_per_day.values())
    # calculate hours until inventory full
    # inventory slots available for items = total slots - slots needed for crafting
    available_slots = inventory_slots - inventory_slots_required_for_crafting
    if available_slots > 0:
        # one slot holds 64 items
        total_capacity = available_slots * 64
        
        # hours until full = (capacity / items per day) * 24
        hours_until_inventory_full = (total_capacity / total_items_per_day) * 24 if total_items_per_day > 0 else float('inf')
    else:
        hours_until_inventory_full = 0

    id = f"{minion.name}_{minion_level}_{playstyle.short_name}_{fuel.name}_{item_1.name}_{item_2.name}_{storage.name}_{mithril_infusion}_{free_will}"

    # calculate expenses and costs:
    fuel_cost_per_day = None
    if fuel.duration_hours:
        fuel_cost_per_day = skyblock_items.search_by_name(fuel.name).bz_buy_price * (24 / fuel.duration_hours)
    
    
    # for output in outputs_per_day:
    #     item = skyblock_items.search_by_name(output)
    #     if item:
    #         revenue_per_day_npc += item.npc_price * outputs_per_day[output]
    #         revenue_per_day_bz += item.bazaar_sell_order_price * outputs_per_day[output
    
    SA_hours_before_non_optimal_output = None
    SA_revenue_per_day_optimal = None
    if playstyle.short_name == "SA-FL":
        # you will login before min(inventory_full, fuel_runs_out) 
        # to sell the items to the bazaar
        if hours_until_fuel_runs_out is None:
            SA_hours_before_non_optimal_output = hours_until_inventory_full
        else:
            SA_hours_before_non_optimal_output = min(hours_until_inventory_full, hours_until_fuel_runs_out)
        SA_revenue_per_day_optimal = 0
        for output in total_output_per_day:
            item = skyblock_items.search_by_name(output)
            SA_revenue_per_day_optimal += item.npc_sell_price * total_output_per_day[output]
    
    EH_revenue_per_day_ehopper= None
    if playstyle.short_name == "EH":
        EH_revenue_per_day_ehopper = 0
        
        for output in total_output_per_day:
            item = skyblock_items.search_by_name(output)
            EH_revenue_per_day_ehopper += item.npc_sell_price * total_output_per_day[output]
        
        EH_revenue_per_day_ehopper *= 0.90 # enchanted hopper has 90% efficiency
    
    # profit_per_day_ehopper = revenue_per_day_ehopper
    # if fuel_cost_per_day:
    #     profit_per_day_ehopper -= fuel_cost_per_day

    return MinionOutputs(
        id=id,
        playstyle=playstyle.short_name, 
        minion=minion.name, 
        minion_level=level,
        fuel=fuel.name, 
        item_1=item_1.name, 
        item_2=item_2.name, 
        storagetype=storage.name, 
        mithril_infusion=mithril_infusion,
        free_will=free_will,
        inventory_slots=inventory_slots, 
        seconds_per_action=minion.levels[minion_level-1].seconds_per_action,
        calculated_seconds_per_action=seconds_per_action, 
        percentage_boost_total=minion_speed_percentage, 
        outputs_per_cycle=outputs_per_cycle,
        outputs_per_day=outputs_per_day,
        total_output_per_day=total_output_per_day,
        total_money_per_day_npc=total_money_per_day_npc,
        total_money_per_day_bz=total_money_per_day_bz,
        total_money_per_day_optimal=total_money_per_day_optimal,
        SA_compaction_level=None,
        hours_until_fuel_runs_out=hours_until_fuel_runs_out,
        hours_until_inventory_full=hours_until_inventory_full,
        
        # hours_until_player_action_required=0,
        
        fuel_cost_per_day=fuel_cost_per_day,
        
        # revenue_per_day_npc=revenue_per_day_npc,
        # revenue_per_day_bz=revenue_per_day_bz,
        SA_hours_before_non_optimal_output=SA_hours_before_non_optimal_output,
        SA_revenue_per_day_optimal=SA_revenue_per_day_optimal,
        
        EH_revenue_per_day_ehopper=EH_revenue_per_day_ehopper,
    )






for minion in MINIONS:
    
    for playstyle in PLAYSTYLES: 
        
        # only go to the loop if the playstyle is valid for the minion
        if playstyle.eligible_minions != ["all"]:
            if minion.name not in playstyle.eligible_minions:
                continue
        
        
        for fuel in FUEL_TYPES:
            
            
            for item_1_index, item_1 in enumerate(ITEMS):
                for item_2_index, item_2 in enumerate(ITEMS):
                    # Skip inverse combinations
                    if item_1_index > item_2_index:
                        continue
                    
                    # don't stack non-stacking items
                    if item_1 == item_2:
                        if not item_1.can_stack:
                            continue
                    
                    # only send item to be calculated if the item can be used in the minion
                    if item_1.eligible_minions != ["all"]:
                        if minion.name not in item_1.eligible_minions:
                            continue
                    if item_2.eligible_minions != ["all"]:
                        if minion.name not in item_2.eligible_minions:
                            continue
                    
                    # TODO: confirm this is true
                    # you can't use dwarven super compactor + super compactor 3000
                    # if item_1.name == "Super Compactor 3000" and item_2.name == "Dwarven Super Compactor" or item_1.name == "Dwarven Super Compactor" and item_2.name == "Super Compactor 3000":
                    #     continue
                    
                    # the compactor playstyles are only valid with certain items
                    # you will login before the third compaction level is reached
                    
                    if playstyle.short_name in ["SA-CA", "SA-CC", "SA-FL"]:
                        if (not ("Compactor" in item_1.name)) and (not ("Compactor" in item_2.name)):
                            continue
                        
                        if playstyle.short_name == "SA-CC":
                            # there must be corrupted soil in the other item
                            if not ("Corrupt Soil" in item_1.name) and not ("Corrupt Soil" in item_2.name):
                                continue
                    
   
                    
                    
                    for storage in STORAGES:
                        
                        levels = [len(minion.levels)]
                        # if the final level is complicated then we should also show the t11 version
                        if minion.levels[-1].npc_required:
                            levels = [len(minion.levels)-1, len(minion.levels)]
                        
                        for level in levels:
                            
                            for mithril_infusion in [False, True]:
                                for free_will in [False, True]:
                                    out = calculate_minion_outputs(minion, level, playstyle, fuel, item_2, item_1, storage, mithril_infusion, free_will)
                                    combinations.append(out)
                        

print(len(combinations))


# GET INFO FROM BAZAAR


# bazaar_data = get_bazaar_data()

for c in combinations:
    c.clean_clamp()


def write_data(combinations):
    # Convert float values to 2 decimal places before writing
    processed_combinations = []
    for c in combinations:
        c_dict = vars(c)
        for key, value in c_dict.items():
            if isinstance(value, float):
                c_dict[key] = round(value, 2)
            elif isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, float):
                        value[k] = round(v, 2)
        processed_combinations.append(c_dict)
    
    # class SetEncoder(json.JSONEncoder):
    #     def default(self, obj):
    #         if isinstance(obj, set):
    #             return list(obj)
    #         return json.JSONEncoder.default(self, obj)
    
    with open('data/sheep_minion_combinations.json', 'w') as f:
        json.dump(processed_combinations, f, indent=4)


# def read_data():
#     with open('data.json', 'r') as f:
#         data = json.load(f)
#         return [MinionOutputs(**item) for item in data]

write_data(combinations)

# write_data(read_data())


# for i in range(0, min(100, len(combinations))):
#     print(combinations[i])