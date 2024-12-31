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


PLAYSTYLES = [
    "enchanted_hopper", # you will check the minion less than once a month
    "idle", # you will idle on your island to activate the crystal and 
    "idle_non_minion_spawning", # you afk on your island and you 
    "non_minion_harvest", # you farm the minion output yourself (why would you do this?...)
    
    "non_minion_spawning", "non_minion_harvest"]

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
    
    outputs_per_cycle: dict[str, float]
    outputs_per_day: dict[str, float]
    total_output_per_day: dict[str, float]
    total_money_per_day: dict[str, float]
    compaction_level: int
    
    hours_until_fuel_runs_out: None | int
    hours_until_inventory_full: int
    
    fuel_cost_per_day: float
    
    revenue_per_day_npc: float # DOES NOT INCLUDE FUEL COST
    revenue_per_day_bz: float # DOES NOT INCLUDE FUEL COST
    
    revenue_per_day_ehopper: float = 0 # DOES NOT INCLUDE FUEL COST
    profit_per_day_ehopper: float = 0 # includes fuel cost

    def clean_clamp(self):
        self.revenue_per_day_ehopper = int(self.revenue_per_day_ehopper)
        self.profit_per_day_ehopper = int(self.profit_per_day_ehopper)



combinations:list[MinionOutputs] = []

# get data of skyblock items
skyblock_items = SkyblockItems()


"""
TBD: confirm that catalyst affects minion outputs, but not diamond spreadings outputs
"""
def calculate_minion_outputs(minion:MinionBase, minion_level: int, playstyle:str, fuel:MinionFuelType, item_1:MinionItemType, item_2:MinionItemType, storage:MinionStorageType, mithril_infusion:bool, free_will:bool) -> MinionOutputs:
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
    if playstyle == "passive" or True:
        seconds_per_harvest *= 2 # because every minion has a spawning / harvesting action
    
    
    total_output_per_day = outputs_per_day.copy()
    for output in outputs_per_cycle:
        if output not in total_output_per_day:
            total_output_per_day[output] = 0
        total_output_per_day[output] += outputs_per_cycle[output] * (86400 / seconds_per_harvest)
    
    total_money_per_day = {}
    for output in total_output_per_day:
        item = skyblock_items.search_by_name(output)
        assert item
        total_money_per_day[output] = f"${int(item.npc_sell_price * total_output_per_day[output])}"
        
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

    id = f"{minion.name}_{minion_level}_{playstyle}_{fuel.name}_{item_1.name}_{item_2.name}_{storage.name}_{mithril_infusion}_{free_will}"

    # calculate expenses and costs:
    fuel_cost_per_day = None
    if fuel.duration_hours:
        fuel_cost_per_day = skyblock_items.search_by_name(fuel.name).bz_buy_price * (24 / fuel.duration_hours)
    
    revenue_per_day_npc: float = 0 # DOES NOT INCLUDE FUEL COST
    revenue_per_day_bz: float = 0 # DOES NOT INCLUDE FUEL COST
    
    # for output in outputs_per_day:
    #     item = skyblock_items.search_by_name(output)
    #     if item:
    #         revenue_per_day_npc += item.npc_price * outputs_per_day[output]
    #         revenue_per_day_bz += item.bazaar_sell_order_price * outputs_per_day[output
    
    
    revenue_per_day_ehopper: float = 0
    
    for output in total_output_per_day:
        item = skyblock_items.search_by_name(output)
        assert item
        revenue_per_day_ehopper += item.npc_sell_price * total_output_per_day[output]
    
    revenue_per_day_ehopper *= 0.90 # enchanted hopper has 90% efficiency
    
    profit_per_day_ehopper = revenue_per_day_ehopper
    if fuel_cost_per_day:
        profit_per_day_ehopper -= fuel_cost_per_day

    return MinionOutputs(
        id=id,
        playstyle=playstyle, 
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
        total_money_per_day=total_money_per_day,
        compaction_level=0,
        hours_until_fuel_runs_out=hours_until_fuel_runs_out,
        hours_until_inventory_full=hours_until_inventory_full,
        fuel_cost_per_day=fuel_cost_per_day,
        
        revenue_per_day_npc=revenue_per_day_npc,
        revenue_per_day_bz=revenue_per_day_bz,
        
        revenue_per_day_ehopper=revenue_per_day_ehopper,
        profit_per_day_ehopper=profit_per_day_ehopper
    )






for minion in MINIONS:
    
    for playstyle in PLAYSTYLES: 
        
        # only go to the loop if the playstyle is valid for the minion
        if playstyle == "passive":
            pass
        elif playstyle == "non_minion_spawning" and minion.non_minion_spawning_exists:
            pass
        elif playstyle == "non_minion_harvest" and minion.non_minion_harvest_exists:
            pass
        else:
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