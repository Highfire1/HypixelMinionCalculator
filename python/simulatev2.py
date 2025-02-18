
import copy
from dataclasses import dataclass
import json
from math import floor
from typing import List, Optional
import time

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
class MinionSimulationCombination:
    minion: MinionBase
    level: int
    fuel: MinionFuelType
    hopper: MinionHopperType
    item_1: MinionItemType
    item_2: MinionItemType
    storage: MinionStorageType
    mithril_infusion: bool
    free_will: bool
    postcard: bool
    beacon_percent_boost: int
    seconds: int
    

def generate_simulation_combinations() -> list[MinionSimulationCombination]:
    out = []
    
    for minion in MINIONS:
        
        
        # if the final level requires non-cash grind then we should also show the t11 version
        # for now only sheep minion
        levels = [len(minion.levels)]
        if minion.name == "Sheep":
            levels = [len(minion.levels)-1, len(minion.levels)]
        
        for level in levels:
            
            
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
                    
                    # technically you can use two compactors but it doesn't do anything
                    if item_1.name == "Super Compactor 3000" and item_2.name == "Dwarven Super Compactor" or item_1.name == "Dwarven Super Compactor" and item_2.name == "Super Compactor 3000":
                        continue
                        
                        
                    for fuel in FUEL_TYPES:
                        if fuel and fuel.name == "Everburning Flame" and minion.skill_type != "combat":
                            continue

                        
                        for storage in STORAGES:
                    
                            
                            for mithril_infusion in [False, True]:
                                for free_will in [False, True]:
                                    for postcard in [False, True]:
                                        for beacon_percent_boost in [0, 10, 11]:
                                            
                                            for hopper in HOPPERS:
                                        
                                                #time_increments = [60*5, 60*60, 60*60*6, 60*60*12, 60*60*24, 60*60*48, 60*60*24*7, 60*60*24*14, 60*60*24*365]
                                                
                                                time_increments = [60*60*24, 60*60*48, 60*60*24*7, 60*60*24*14, 60*60*24*30, 60*60*24*124]
                                                
                                                for seconds in time_increments:
                                                    
                                                    out.append(
                                                        MinionSimulationCombination(
                                                            minion=minion,
                                                            level=level,
                                                            fuel=fuel,
                                                            hopper=hopper,
                                                            item_1=item_1,
                                                            item_2=item_2,
                                                            storage=storage,
                                                            mithril_infusion=mithril_infusion,
                                                            free_will=free_will,
                                                            postcard=postcard,
                                                            beacon_percent_boost=beacon_percent_boost,
                                                            seconds=seconds
                                                        )
                                                    )
    return out
                                     
                                     
# Start timing
start_time = time.time()

simulation_combinations = generate_simulation_combinations()

# End timing
end_time = time.time()
elapsed_time = end_time - start_time

print(f"Total combinations: {len(simulation_combinations)}")
print(f"Time taken: {elapsed_time:.2f} seconds")