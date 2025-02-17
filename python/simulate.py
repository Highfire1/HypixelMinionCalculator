"""
FAQ:

 q: where inferno minion?
 It's too complicated for this interface, use the page on the wiki: https://hypixel-skyblock.fandom.com/wiki/User:Voball/Sandbox-Inferno_Minions


"""

import copy
from dataclasses import dataclass
import json
from math import floor
from typing import List, Optional

from sqlmodel import Field, SQLModel, Session, create_engine
from bazaar import SkyblockItems
import os


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
class MinionHopperType:
    name: str
    sell_percentage: int
    
HOPPERS: list[None |  MinionHopperType] = [
    # None,
    # MinionHopperType("Budget Hopper", 50),
    MinionHopperType("Enchanted Hopper", 90),
]

@dataclass
class MinionInventorySlot:
    item: str
    amount: int
    
    def __repr__(self):
        if self.amount == 0:
            return ""
        return f"{self.amount} {self.item}"

class MinionInventory:
    def __init__(self, slots:int, storage: None | MinionStorageType = None):
        self.slots: int = slots
        self.items: list[MinionInventorySlot] = [MinionInventorySlot(item="", amount=0) for i in range(slots)]
        if storage:
            self.storage_slots: int = storage.inventory_slots
            self.storage_items: list[MinionInventorySlot] = [MinionInventorySlot(item="", amount=0) for i in range(storage.inventory_slots)]
        else:
            self.storage_slots = 0
            self.storage_items = []

    # tries to put item in inventory one stack at a time
    # each stack can only have 64 items
    # if inventory is full try to place in storage
    # if both are full return tuple with (item, amount)
    # if success return true
    def put_items_in_inventory(self, items:list[list[str, int]]) -> bool | dict[str, int]:
        # Don't modify input array
        items = copy.deepcopy(items)
        
        # Count empty slots
        empty_main_slots = sum(1 for slot in self.items if slot.amount == 0)
        empty_storage_slots = sum(1 for slot in self.storage_items if slot.amount == 0)
        total_empty_slots = empty_main_slots + empty_storage_slots

        # First fill existing slots with matching items
        for item in items:
            # Try main inventory
            for slot in self.items:
                if slot.item == item[0] and slot.amount < 64:
                    add = min(64 - slot.amount, item[1])
                    slot.amount += add
                    item[1] -= add
                    
            # Try storage
            for slot in self.storage_items:
                if slot.item == item[0] and slot.amount < 64:
                    add = min(64 - slot.amount, item[1])
                    slot.amount += add
                    item[1] -= add

        # Remove fully allocated items
        items = [item for item in items if item[1] > 0]
        
        if not items:
            return True

        # If we have enough slots, ensure one slot per item type
        if total_empty_slots >= len(items):
            # Initial allocation pass
            for item in items:
                allocated = False
                
                # Try main inventory first
                for i, slot in enumerate(self.items):
                    if slot.amount == 0 and not allocated:
                        amount = min(64, item[1])
                        self.items[i] = MinionInventorySlot(item[0], amount) 
                        item[1] -= amount
                        allocated = True
                        break
                        
                # Try storage if needed
                if not allocated:
                    for i, slot in enumerate(self.storage_items):
                        if slot.amount == 0 and not allocated:
                            amount = min(64, item[1])
                            self.storage_items[i] = MinionInventorySlot(item[0], amount)
                            item[1] -= amount
                            break

        # Calculate remaining slots and items
        empty_slots_remaining = sum(1 for slot in self.items if slot.amount == 0) + sum(1 for slot in self.storage_items if slot.amount == 0)
        total_items_remaining = sum(item[1] for item in items)

        # Distribute remaining items proportionally 
        # TODO: something is wrong with this algorithm
        # it doesn't distribute items equally
        if total_items_remaining > 0:
            for item in items:
                if item[1] == 0:
                    continue
                    
                slots_for_item = round((item[1] / total_items_remaining) * empty_slots_remaining)
                
                # Fill main inventory
                slots_used = 0
                for i, slot in enumerate(self.items):
                    if slot.amount == 0 and slots_used < slots_for_item:
                        amount = min(64, item[1])
                        self.items[i] = MinionInventorySlot(item[0], amount)
                        item[1] -= amount
                        slots_used += 1
                        
                # Fill storage
                for i, slot in enumerate(self.storage_items):
                    if slot.amount == 0 and slots_used < slots_for_item:
                        amount = min(64, item[1])
                        self.storage_items[i] = MinionInventorySlot(item[0], amount)
                        item[1] -= amount
                        slots_used += 1

        # Return remaining items or success
        remaining = {item[0]: item[1] for item in items if item[1] > 0}
        return remaining if remaining else True
    
    def get_inventory_items(self) -> dict[str, int]:
        items = {}
        for slot in self.items:
            if slot.amount != 0:
                if slot.item not in items:
                    items[slot.item] = 0
                items[slot.item] += slot.amount
        for slot in self.storage_items:
            if slot.amount != 0:
                if slot.item not in items:
                    items[slot.item] = 0
                items[slot.item] += slot.amount
        
        return items

    def __repr__(self):
        if self.storage_slots != 0:
            return f"{self.items} & {self.storage_items}"
        return f"{self.items}"



@dataclass
class MinionSimulationOutput:
    seconds: int
    percentage_boost: int
    raw_item_drops: dict[str, int]
    in_inventory: dict[str, int]
    sold_to_hopper: dict[str, int]
    
    hopper_coins: int
    coins_if_inventory_sell_order_to_bz: int
    coins_if_inventory_instant_sold_to_bz: int
    coins_if_inventory_sold_to_npc: int
    coins_if_inventory_sold_optimally: int
    
    profit_24h_if_inventory_sell_order_to_bz: int
    profit_24h_if_inventory_instant_sold_to_bz: int
    profit_24h_if_inventory_sold_to_npc: int
    profit_24h_if_inventory_sold_optimally: int
    profit_24h_only_hopper: int
    
    APR_if_inventory_sell_order_to_bz: int
    APR_only_hopper: int
    # total_coins_if_sell_order_to_bz: int
    # total_coins_if_instant_sold_to_bz: int
    # total_coins_if_sold_optimally: int
    
    cost_of_fuel: int
    inventory_full: bool
    fuel_empty: bool
    
    minion_cost_non_recoverable: int
    minion_cost_recoverable: int
    minion_cost_total: int
    # coins_per_day: int
    
class MinionSimulationResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    minion: str
    minion_level: int
    
    fuel: Optional[str]
    hopper: Optional[str]
    item_1: Optional[str]
    item_2: Optional[str]
    storagetype: Optional[str]
    
    mithril_infusion: bool
    free_will: bool
    postcard: bool 
    beacon_boost_percent: int
    pet_bonus_percent: int
    crystal_bonus_percent: int
    
    seconds: int
    percentage_boost: int
    raw_item_drops: str # dict[str, int] # so we can store dict into sqlite as string
    
    in_inventory: str #dict[str, int]
    sold_to_hopper: str #dict[str, int]
    hopper_coins: int
    cost_of_fuel: int
    
    coins_if_inventory_sell_order_to_bz: int 
    coins_if_inventory_instant_sold_to_bz: int
    coins_if_inventory_sold_to_npc: int
    coins_if_inventory_sold_optimally: int
    
    profit_24h_if_inventory_sell_order_to_bz: int
    profit_24h_if_inventory_instant_sold_to_bz: int
    profit_24h_if_inventory_sold_to_npc: int
    profit_24h_if_inventory_sold_optimally: int
    profit_24h_only_hopper: int
    
    APR_if_inventory_sell_order_to_bz: int
    APR_only_hopper: int
    
    inventory_full: bool
    fuel_empty: bool
    
    minion_cost_total: int
    minion_cost_recoverable: int
    minion_cost_non_recoverable: int
    

skyblock_items = SkyblockItems(only_bazaar=False)

MINIONS.reverse()

# NOTE: this calculation is only valid while the island is UNLOADED
# two main reason for this is corrupted soil
# there are some weird interactions
# A: catalyst works on corrupt soil/sulphur/frag BUT only when the island is unloaded (why????? if loaded you only get 1 each per kill)
# B: compacted items get placed in inventory BEFORE corrupted fragments
def simulate_unloaded_minion_output(minion: MinionBase, minion_level: int, fuel: None | MinionFuelType, hopper: None | MinionHopperType, item_1:None | MinionItemType, item_2:None | MinionItemType, storage: None | MinionStorageType, mithril_infusion: bool, free_will: bool, postcard:bool, beacon_percent_boost: int, pet_bonus_percent: int, crystal_bonus_percent: int, seconds: int, minionInventory=None) -> MinionSimulationOutput:
    
    outputs_per_cycle:dict[str, float] = {}
    outputs_per_cycle_not_multiplied:dict[str, float] = {}
    outputs_per_day:dict[str, float] = {}
    minion_speed_percentage = 100
    
    # parse minion drops
    for action in minion.actions:
        if action.drops:
            for drop in action.drops:
                if drop.item not in outputs_per_cycle:
                    outputs_per_cycle[drop.item] = 0
                outputs_per_cycle[drop.item] += drop.amount * (drop.percentage/100)
    
    
    # handle minion upgrades
    if mithril_infusion: minion_speed_percentage += 10
    if free_will: minion_speed_percentage += 10
    if postcard: minion_speed_percentage += 5
    assert beacon_percent_boost in [0, 10, 11] # idc about lower level beacons
    if beacon_percent_boost: minion_speed_percentage += beacon_percent_boost
    if pet_bonus_percent: minion_speed_percentage += pet_bonus_percent
    if crystal_bonus_percent: minion_speed_percentage += crystal_bonus_percent
    
    # handle fuel
    # ASSUMPTION: you will put in 64 fuel at a time
    if fuel == None:
        pass
    
    elif not fuel.special_case:
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
        
        if item == None:
            pass
        
        elif not item.special_case:
            if item.percentage_boost:
                minion_speed_percentage += item.percentage_boost
        
        elif item.name == "Diamond Spreading":
            # one diamond is generated for every 10 items (on average) (only 1 per minion)
            # TODO: verify double diamond spreading calculation
            # drops are not affected by cheese/catalyst/hypercatalyst
            outputs_per_cycle_not_multiplied["Diamond"] = sum(outputs_per_cycle.values()) / 10
        
        # TODO: check if lesser soulflow and soulflow engine can stack
    
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
                    
                    # SPECIAL CASE: slimes have a special calculation (do other minions?)
                    # PENDING MORE TESTING...
                    if minion.name == "Slime" and False:
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
        elif item.name == "Auto Smelter" or item.name == "Dwarven Super Compactor":
            for item in outputs_per_cycle:
                if is_smeltable(item):
                    outputs_per_cycle[convert_to_smelted(item)] = outputs_per_cycle[item]
                    del outputs_per_cycle[item]
        
        elif item.name == "Compactor":
            pass # handle later
            # for item in list(outputs_per_cycle.keys()):
            #     if is_compactable(item):
            #         # if we create 1 clay per action, and it takes 4 clay to make a clay block
            #         # then we produce 0.25 (1/4) clay blocks per action
            #         converted_item = convert_to_compacted(item)
            #         outputs_per_cycle[converted_item.output_item] = outputs_per_cycle[item] / converted_item.input_count
            #         del outputs_per_cycle[item]
            #         inventory_slots_required_for_crafting += 1
        
        # note: this only applies super compaction once
        elif item.name == "Super Compactor 3000":
            pass # handle later
            # for item in list(outputs_per_cycle.keys()):
            #     if is_super_compactable(item):
            #         converted_item = convert_to_super_compacted(item)
            #         outputs_per_cycle[converted_item.output_item] = outputs_per_cycle[item] / converted_item.input_count
            #         del outputs_per_cycle[item]
            #         inventory_slots_required_for_crafting += 1
    # some fuel calculation
    fuel_runs_out = False
    if fuel == None:
        fuel_runs_out = True
    elif fuel.duration_hours == None:
        fuel_runs_out = False
    else:
        # ASSUMPTION: assume you always put in 64 fuel at a time
        if seconds > ((fuel.duration_hours * 60*60) * 64):
            fuel_runs_out = True
    # calculate outputs for the time period
    item_drops = {}
    
    seconds_per_cycle = (minion.levels[minion_level-1].seconds_per_action) * 2
    
    if not fuel_runs_out:
        # the happy path
        for item in outputs_per_cycle:
            items_generated = outputs_per_cycle[item] * (seconds / (seconds_per_cycle / (minion_speed_percentage/100)))
            item_drops[item] = floor(items_generated) 
        for item in outputs_per_cycle_not_multiplied:
            items_generated = outputs_per_cycle_not_multiplied[item] * (seconds / ((seconds_per_cycle / (minion_speed_percentage/100))))
            item_drops[item] = floor(items_generated)

        # if minion.name == "Slime": input(item_drops)
    else:
        # the not happy path
        # (we run out of fuel)
        
        time_1 = (fuel.duration_hours * 60*60) * 64
        for item in outputs_per_cycle:
            items_generated = outputs_per_cycle[item] * (time_1 / (seconds_per_cycle / (minion_speed_percentage/100)))
            item_drops[item] = floor(items_generated) 
        for item in outputs_per_cycle_not_multiplied:
            items_generated = outputs_per_cycle_not_multiplied[item] * (time_1 / ((seconds_per_cycle / (minion_speed_percentage/100))))
            item_drops[item] = floor(items_generated)
        
        # remove fuel
        if fuel == None:
            pass
            
        elif not fuel.special_case:
            minion_speed_percentage -= fuel.percentage_boost
            
        elif fuel.name == "Everburning Flame":
            minion_speed_percentage -= 35
            if minion.skill_type == "combat":
                minion_speed_percentage -= 5
        
        elif fuel.name == "Tasty Cheese":
            for item in outputs_per_cycle:
                outputs_per_cycle[item] /= 2
        
        elif fuel.name == "Catalyst":
            for item in outputs_per_cycle:
                outputs_per_cycle[item] /= 3
                
        elif fuel.name == "Hyper Catalyst":
            for item in outputs_per_cycle:
                outputs_per_cycle[item] /= 4
        
        time_2 = seconds - time_1
        for item in outputs_per_cycle:
            items_generated = outputs_per_cycle[item] * (time_2 / (seconds_per_cycle / (minion_speed_percentage/100)))
            item_drops[item] = floor(items_generated) 
        for item in outputs_per_cycle_not_multiplied:
            items_generated = outputs_per_cycle_not_multiplied[item] * (time_2 / ((seconds_per_cycle / (minion_speed_percentage/100))))
            item_drops[item] = floor(items_generated)
        
    
    for item in outputs_per_day:
        # 86400 seconds in a day
        # if 86400 seconds and 1 item/day, then 86400/86400 = 1 item
        # if 43200 seconds and 1 item/day, then 43200/86400 = 0.5 item
        items_generated = outputs_per_day[item] * (seconds / 86400)
        item_drops[item] = floor(items_generated)
    
    # generate compacted drops
    compacted_item_drops:dict[str, int] = {}
    raw_item_drops:dict[str, int] = copy.deepcopy(item_drops)
    
    # the VERY IMPORTANT INFORMATION here is that compacted items
    # get inserted into the inventory BEFORE all other drops
    # when using an offline calculation
    # allegedly
    
    # compactor applies first
    if item_1.name == "Compactor" or item_2.name == "Compactor":
        for item in item_drops:
            if is_compactable(item):
                compacted = convert_to_compacted(item)
                amt_made = floor(item_drops[item] / compacted.input_count)
                compacted_item_drops[compacted.output_item] = amt_made
                item_drops[item] = item_drops[item] % compacted.input_count
                
    if item_1.name == "Super Compactor 3000" or item_1.name == "Dwarven Super Compactor 3000" or item_2.name == "Super Compactor 3000" or item_2.name == "Dwarven Super Compactor 3000":
        for item in item_drops:
            if is_super_compactable(item):
                
                super_compacted = convert_to_super_compacted(item)
                amt_made = floor(item_drops[item] / super_compacted.input_count)
                compacted_item_drops[super_compacted.output_item] = amt_made
                item_drops[item] = item_drops[item] % super_compacted.input_count
            
                # enchanted iron -> enchanted iron blocks
                compact_2 = super_compacted.output_item
                if is_super_compactable(compact_2) and amt_made > 0:
                    super_compacted_2 = convert_to_super_compacted(compact_2)
                    amt_made = floor(compacted_item_drops[compact_2] / super_compacted_2.input_count)
                    compacted_item_drops[super_compacted_2.output_item] = amt_made
                    compacted_item_drops[compact_2] = compacted_item_drops[compact_2] % super_compacted_2.input_count
                # i don't think that there is a 4th compaction level (?)
                
            
    
    # put items into inventory
    if minionInventory is None:
        minionInventory = MinionInventory(
            slots=minion.levels[minion_level-1].inventory_slots, 
            storage=storage, )
    
    hopper_money = 0
    
    compacted_item_drops_list = [[item, amount] for item, amount in compacted_item_drops.items()]
    not_put_in_inventory_1 = minionInventory.put_items_in_inventory(compacted_item_drops_list)
    
    item_drops_list = [[item, amount] for item, amount in item_drops.items()]
    not_put_in_inventory_2 = minionInventory.put_items_in_inventory(item_drops_list)
    
    # performance implications?
    not_put_in_inventory:dict[str, int] = {}
    if not_put_in_inventory_1 == True and not_put_in_inventory_2 == True:
        pass
    elif not_put_in_inventory_1 == True:
        not_put_in_inventory = not_put_in_inventory_2
    elif not_put_in_inventory_2 == True:
        not_put_in_inventory = not_put_in_inventory_1
        
    
    lost_items = {}
    hopper_items = {}
        
    # if there are items that couldn't fit in the inventory
    # then we need to see if they would be sold by hopper
    if not_put_in_inventory != {}:
        hopper_value = 0

        for item, amount in not_put_in_inventory.items():
            sb_item = skyblock_items.search_by_name(item)
            hopper_value += sb_item.npc_sell_price * amount

        if hopper != None:
            hopper_money = hopper_value * (hopper.sell_percentage / 100)
            hopper_items = not_put_in_inventory
        else:
            lost_items = not_put_in_inventory
    
    cost_of_fuel = 0
    if fuel and fuel.duration_hours:
        sb_item = skyblock_items.search_by_name(fuel.name)
        # calculate how many fuels would be used in this time period
        # fuel.length_in_seconds is how long one fuel lasts
        cost_of_fuel = (float(seconds) / float(fuel.duration_hours*60*60)) * sb_item.bz_buy_price
    
    # ASSUMPTION: you have 29 minion slots.
    # yes, the cap is 31 but that requires grinding slayer and nether and pelts
    # treat it as some extra cash
    MINION_COUNT = 29
    if beacon_percent_boost:
        if beacon_percent_boost % 2 == 0:
            crystal = skyblock_items.search_by_name("Power Crystal")
        else:
            crystal = skyblock_items.search_by_name("Scorched Power Crystal")
        crystal_cost_24hrs_per_minion = (crystal.bz_sell_price / 2) / MINION_COUNT
        cost_of_fuel += crystal_cost_24hrs_per_minion * (seconds / 86400)
        
    
    # CALCULATE PRICE OF INVENTORY
    coins_if_inventory_sell_order_to_bz=0
    coins_if_inventory_instant_sold_to_bz=0
    coins_if_inventory_sold_to_npc=0
    coins_if_inventory_sold_optimally=0
    
    inventory_items = minionInventory.get_inventory_items()
    for item in inventory_items:
        sb_item = skyblock_items.search_by_name(item)
        npc = sb_item.npc_sell_price * inventory_items[item]
        
        instant_sell, sell_order = 0, 0
        if sb_item.bz_sell_price != None:
            instant_sell = sb_item.bz_sell_price * inventory_items[item]
            sell_order = sb_item.bz_buy_price * inventory_items[item] # TAX NOT INCLUDED!
        
        # print(seconds, item, inventory_items[item], sb_item.npc_sell_price, npc)
        # input()
        
        coins_if_inventory_sold_to_npc += npc
        coins_if_inventory_instant_sold_to_bz += instant_sell
        coins_if_inventory_sell_order_to_bz += sell_order
        coins_if_inventory_sold_optimally += max(npc, instant_sell, sell_order)
    
    # coins_per_day = int(((coins_if_inventory_sold_to_npc+hopper_money) / seconds) * 86400)
    # generate profit per day
    profit_24h_if_inventory_sold_to_npc = int(((coins_if_inventory_sold_to_npc+hopper_money-cost_of_fuel) / seconds) * 86400)
    profit_24h_if_inventory_instant_sold_to_bz = int(((coins_if_inventory_instant_sold_to_bz+hopper_money-cost_of_fuel) / seconds) * 86400)
    profit_24h_if_inventory_sell_order_to_bz = int(((coins_if_inventory_sell_order_to_bz+hopper_money-cost_of_fuel) / seconds) * 86400)
    profit_24h_if_inventory_sold_optimally = int(((coins_if_inventory_sold_optimally+hopper_money-cost_of_fuel) / seconds) * 86400)
    profit_24h_only_hopper = int((hopper_money-cost_of_fuel) / seconds * 86400)
    
    # some other stuff
    inventory_full = not_put_in_inventory != {}
    
    # generate minion cost taking into account minion level materials, items, hopper, and postcard
    minion_cost_total = 0
    minion_cost_recoverable = 0
    minion_cost_non_recoverable = 0
    
    # Calculate setup cost for all level materials at once
            
    minion_cost_non_recoverable += minion.get_cumulative_level_costs(minion_level, skyblock_items)
    
    if fuel != None and fuel.duration_hours == None: 
        item = skyblock_items.search_by_name(fuel.name)
        if item.bz_sell_price == None:
            skyblock_items.attempt_fetch_auction_data(item)
        minion_cost_recoverable += item.lowest_price()
        
    if hopper: minion_cost_recoverable += skyblock_items.search_by_name(hopper.name).bz_sell_price
    if item_1: minion_cost_recoverable += skyblock_items.search_by_name(item_1.name).bz_sell_price
    if item_2: minion_cost_recoverable += skyblock_items.search_by_name(item_2.name).bz_sell_price
    if storage: minion_cost_recoverable += skyblock_items.search_by_name(f"{storage.name} Storage").bz_sell_price
    if mithril_infusion: minion_cost_non_recoverable += skyblock_items.search_by_name("Mithril Infusion").bz_sell_price
    
    # yes it's not a 100% chance but it's close enough and you recover the price by selling the postcard
    if free_will: minion_cost_non_recoverable += skyblock_items.search_by_name("Free Will").bz_sell_price
    
    if postcard: 
        item = skyblock_items.search_by_name("Postcard")
        skyblock_items.attempt_fetch_auction_data(item)
        minion_cost_recoverable += item.lowest_price() / MINION_COUNT # 80m / 29 minions
        
    if beacon_percent_boost > 0:
        item = skyblock_items.search_by_name("Beacon V")
        skyblock_items.attempt_fetch_auction_data(item)
        minion_cost_recoverable += item.lowest_price() / MINION_COUNT
    
    # ignoring cost of pet and crystal here
    
    minion_cost_total = minion_cost_recoverable + minion_cost_non_recoverable
    
    # generate cash / day

    # generate APR
    APR_if_inventory_sell_order_to_bz = ((profit_24h_if_inventory_instant_sold_to_bz * 365)/minion_cost_total) * 100
    APR_only_hopper = ((profit_24h_only_hopper * 365)/minion_cost_total) * 100
    
    # clamp data to int because a fraction of a coin is not. relevant.
    cost_of_fuel = int(cost_of_fuel)
    hopper_money = int(hopper_money)
    
    coins_if_inventory_instant_sold_to_bz = int(coins_if_inventory_instant_sold_to_bz)
    coins_if_inventory_sell_order_to_bz = int(coins_if_inventory_sell_order_to_bz)
    coins_if_inventory_sold_to_npc = int(coins_if_inventory_sold_to_npc)
    coins_if_inventory_sold_optimally = int(coins_if_inventory_sold_optimally)
    
    APR_if_inventory_sell_order_to_bz = int(APR_if_inventory_sell_order_to_bz)
    APR_only_hopper = int(APR_only_hopper)

    
    minion_cost_total = int(minion_cost_total)
    minion_cost_recoverable = int(minion_cost_recoverable)
    minion_cost_non_recoverable = int(minion_cost_non_recoverable)
    
    return MinionSimulationOutput(
        seconds=seconds,
        percentage_boost=minion_speed_percentage,
        raw_item_drops=raw_item_drops,
        in_inventory=minionInventory.get_inventory_items(),
        
        # lost_items=lost_items,
        sold_to_hopper=hopper_items,
        hopper_coins=hopper_money,
        
        coins_if_inventory_sell_order_to_bz=coins_if_inventory_sell_order_to_bz,
        coins_if_inventory_instant_sold_to_bz=coins_if_inventory_instant_sold_to_bz,
        coins_if_inventory_sold_to_npc=coins_if_inventory_sold_to_npc,
        coins_if_inventory_sold_optimally=coins_if_inventory_sold_optimally,
        
        profit_24h_if_inventory_sell_order_to_bz=profit_24h_if_inventory_sell_order_to_bz,
        profit_24h_if_inventory_instant_sold_to_bz=profit_24h_if_inventory_instant_sold_to_bz,
        profit_24h_if_inventory_sold_to_npc=profit_24h_if_inventory_sold_to_npc,
        profit_24h_if_inventory_sold_optimally=profit_24h_if_inventory_sold_optimally,
        profit_24h_only_hopper=profit_24h_only_hopper,
        
        APR_if_inventory_sell_order_to_bz=APR_if_inventory_sell_order_to_bz,
        APR_only_hopper=APR_only_hopper,
        
        # total_coins_if_sell_order_to_bz=0,
        # total_coins_if_instant_sold_to_bz=0,
        # total_coins_if_sold_optimally=0,
        
        cost_of_fuel=cost_of_fuel,
        
        inventory_full=inventory_full,
        fuel_empty=fuel_runs_out,
        
        minion_cost_total=minion_cost_total,
        minion_cost_non_recoverable=minion_cost_non_recoverable,
        minion_cost_recoverable=minion_cost_recoverable,
        
        # coins_per_day=coins_per_day,
    )
            
            
    pass

@dataclass
class MinionCombinationSimulationResults:
    minion: str
    minion_level: int
    
    fuel: None | MinionFuelType
    hopper: None | MinionHopperType
    item_1: None | MinionItemType
    item_2: None | MinionItemType
    
    storagetype: None | str
    
    mithril_infusion: bool
    free_will: bool
    postcard: bool
    beacon_percent_boost: int
    
    time_combinations: list[MinionSimulationOutput]
    
    def __repr__(self):
        return json.dumps(self, default=lambda k: k.__dict__, indent=4)


simulation_outputs: list[MinionSimulationResult] = []
id: int = 0

for minion in MINIONS:
    
        
    for fuel in FUEL_TYPES:
        
        # plasma bucket is same as everburning for non-combat minions
        if fuel and fuel.name == "Everburning Flame" and minion.skill_type != "combat":
            continue
        
        
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
                if item_1.name == "Super Compactor 3000" and item_2.name == "Dwarven Super Compactor" or item_1.name == "Dwarven Super Compactor" and item_2.name == "Super Compactor 3000":
                    continue
                
                for storage in STORAGES:
                    
                    
                    # if the final level requires non-cash grind then we should also show the t11 version
                    # for now only sheep minion
                    levels = [len(minion.levels)]
                    if minion.name == "Sheep":
                        levels = [len(minion.levels)-1, len(minion.levels)]
                    
                    for level in levels:
                        
                        
                        for pet_bonus_percent in [0]: #, True]: // pet bonus don't work offline
                            
                            # if pet_bonus_percent:
                            #     if minion.max_pet_bonus_percentage == 0:
                            #         continue
                            #     else:
                            #         pet_bonus_percent = minion.max_pet_bonus_percentage
                            
                                
                            for crystal_bonus in [0]: #, True]: // crystal doesn't work offline
                                crystal_bonus_percent = 0
                                # the following code is broken
                                # if crystal_bonus == True and minion.crystal_bonus_percentage == 0:
                                #     continue
                                # crystal_bonus_percent = minion.crystal_bonus_percentage
                                
                                
                                for mithril_infusion in [False, True]:
                                    for free_will in [False, True]:
                                        for postcard in [False, True]:
                                            for beacon_percent_boost in [0, 10, 11]:
                                                
                                                for hopper in HOPPERS:
                                            
                                                    #time_increments = [60*5, 60*60, 60*60*6, 60*60*12, 60*60*24, 60*60*48, 60*60*24*7, 60*60*24*14, 60*60*24*365]
                                                    
                                                    time_increments = [60*60, 60*60*24, 60*60*48, 60*60*24*7, 60*60*24*14, 60*60*24*124]
                                                    
                                                    for seconds in time_increments:
                                                        sim = simulate_unloaded_minion_output(minion, level, fuel, hopper, item_1, item_2, storage, mithril_infusion, free_will, postcard, beacon_percent_boost, pet_bonus_percent, crystal_bonus, seconds)
                                                        
                                                        a = MinionSimulationResult(
                                                            id=id,
                                                            minion=minion.name,
                                                            minion_level=level,
                                                            fuel=fuel.name if fuel else None,
                                                            hopper=hopper.name if hopper else None,
                                                            item_1=item_1.name if item_1 else None,
                                                            item_2=item_2.name if item_2 else None,
                                                            storagetype=storage.name if storage else None,
                                                            mithril_infusion=mithril_infusion,
                                                            free_will=free_will,
                                                            postcard=postcard,
                                                            beacon_boost_percent=beacon_percent_boost,
                                                            pet_bonus_percent=pet_bonus_percent,
                                                            crystal_bonus_percent=crystal_bonus_percent,
                                                            
                                                            seconds=seconds,
                                                            percentage_boost=sim.percentage_boost,
                                                            raw_item_drops=str(sim.raw_item_drops),
                                                            in_inventory=str(sim.in_inventory),
                                                            sold_to_hopper=str(sim.sold_to_hopper),
                                                            hopper_coins=sim.hopper_coins,
                                                            coins_if_inventory_sell_order_to_bz=sim.coins_if_inventory_sell_order_to_bz,
                                                            coins_if_inventory_instant_sold_to_bz=sim.coins_if_inventory_instant_sold_to_bz,
                                                            coins_if_inventory_sold_to_npc=sim.coins_if_inventory_sold_to_npc,
                                                            coins_if_inventory_sold_optimally=sim.coins_if_inventory_sold_optimally,
                                                            profit_24h_if_inventory_sell_order_to_bz=sim.profit_24h_if_inventory_sell_order_to_bz,
                                                            profit_24h_if_inventory_instant_sold_to_bz=sim.profit_24h_if_inventory_instant_sold_to_bz,
                                                            profit_24h_if_inventory_sold_to_npc=sim.profit_24h_if_inventory_sold_to_npc,
                                                            profit_24h_if_inventory_sold_optimally=sim.profit_24h_if_inventory_sold_optimally,
                                                            profit_24h_only_hopper=sim.profit_24h_only_hopper,
                                                            APR_if_inventory_sell_order_to_bz=sim.APR_if_inventory_sell_order_to_bz,
                                                            APR_only_hopper=sim.APR_only_hopper,
                                                            cost_of_fuel=sim.cost_of_fuel,
                                                            inventory_full=sim.inventory_full,
                                                            fuel_empty=sim.fuel_empty,
                                                            minion_cost_total=sim.minion_cost_total,
                                                            minion_cost_non_recoverable=sim.minion_cost_non_recoverable,
                                                            minion_cost_recoverable=sim.minion_cost_recoverable,
                                                        )
                                                        id+=1
                                                        if id % 5000 == 0:
                                                            print(f"{id} combinations generated.")
                                                        
                                                        simulation_outputs.append(a)
                                                        
                                                        # m.time_combinations.append(sim)
                                        
                                                    
                                                    # print(json.dumps(m, default=lambda k: k.__dict__, indent=4))
                                                    # input()
                            

print(f"{len(simulation_outputs)} combinations generated.")


# decrease size of db we send to client
if True:
    for s in simulation_outputs:
        s.raw_item_drops = ""
        s.in_inventory = ""
        s.sold_to_hopper = ""
        

# print("Saving to json...")

# filepath = "data/sheep_minion_combinations.json"
# with open(filepath, 'w') as fi:
#     json.dump(simulation_outputs, fi, default=lambda k: k.__dict__, indent=4)
    
# print(f"Saved to {filepath}.")

try:
    if os.path.exists("data/sheep_minion_combinations.db"):
        os.remove("data/sheep_minion_combinations.db")
except Exception as e:
    print(f"Couldn't remove database: {e}")
    input("Hit any key to try again:")
    
    os.remove("data/sheep_minion_combinations.db")
    
    
engine = create_engine("sqlite:///data/sheep_minion_combinations.db")
SQLModel.metadata.create_all(engine)

print("Saving to database...")

try:
    with Session(engine) as session:
        session.add_all(simulation_outputs)
        session.commit()
except Exception as e:
    print(f"Couldn't save database: {e}")
    input("Hit any key to try again:")
    
    with Session(engine) as session:
        session.add_all(simulation_outputs)
        session.commit()

print("Saved to database.")