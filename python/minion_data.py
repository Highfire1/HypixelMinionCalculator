from dataclasses import dataclass

from bazaar import SkyblockItems

# ============== MINION FUELS ==============

@dataclass
class MinionFuelType:
    name: str
    duration_hours: None | int
    percentage_boost: None | int
    special_case: bool
    

FUEL_TYPES = (
    # MinionFuelType("None", None, None, True),
    # missing coal/charcoal?
    # MinionFuelType("Block of Coal", 5, 5, False), # NOT IN BAZAAR, DO NOT USE
    # MinionFuelType("Enchanted Bread", 12, 5, False),
    # MinionFuelType("Enchanted Coal", 24, 10, False),
    # MinionFuelType("Enchanted Charcoal", 24, 10, False),
    # MinionFuelType("Solar Panel", None, None, True),
    
    MinionFuelType("Enchanted Lava Bucket", None  , 25, False),
    MinionFuelType("Magma Bucket", None, 30, False),
    MinionFuelType("Plasma Bucket", None, 35, False),
    
    MinionFuelType("Hamster Wheel", 24, 50, False),
    MinionFuelType("Foul Flesh", 5, 90, False),
    
    # special cases
    MinionFuelType("Everburning Flame", None, None, True),
    MinionFuelType("Tasty Cheese", 1, None, True),
    MinionFuelType("Catalyst", 3, None, True),
    MinionFuelType("Hyper Catalyst", 6, None, True),
    
    # not handling due to complexity
    # MinionFuelType("Inferno Minion Fuel (Rare)", None, None, True),
    # MinionFuelType("Inferno Minion Fuel (Epic)", None, None, True),
    # MinionFuelType("Inferno Minion Fuel (Legendary)", None, None, True),
    
    
)


# ========= MINION ITEMS =========

@dataclass
class MinionItemType:
    name: str
    percentage_boost: None | int
    special_case: bool
    can_stack: bool
    
    eligible_minions: list[str]
    
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name
    

ITEMS = (
    # MinionItemType("None", False, special_case=True, can_stack=True, eligible_minions=["all"]),
    # Flat bonuses
    MinionItemType("Minion Expander", 5, False, True, ["all"]),
    MinionItemType("Flycatcher", 20, False, True, ["all"]),
    
    # New items:
    MinionItemType("Diamond Spreading", None, True, False, ["all"]),
    # MinionItemType("Lesser Soulflow Engine", None, True, False, ["all"]),
    # MinionItemType("Soulflow Engine", None, True, False, ["all"]),
    
    MinionItemType("Corrupt Soil", None, True, False, [
        "Cow", "Pig", "Chicken", "Sheep", "Rabbit", "Zombie", "Revenant", 
        "Voidling", "Inferno", "Vampire", "Skeleton", "Creeper", "Spider", 
        "Tarantula", "Cave Spider", "Blaze", "Magma Cube", "Enderman", "Ghast", "Slime"]),
    
    MinionItemType("Berberis Fuel Injector", None, True, True, [
        "Cactus", "Carrot", "Chicken", "Cocoa Beans", "Cow", "Melon", "Mushroom", 
        "Nether Wart", "Pig", "Potato", "Pumpkin", "Rabbit", "Sheep", "Sugar Cane", "Wheat"
    ]),
    
    # # only 1 per profile
    # MinionItemType("Krampus Helmet", None, True, False, ["all"]),
    # MinionItemType("Sleepy Hollow", None, True, False, ["all"]),
    # MinionItemType("Potato Spreading", None, True, False, ["all"]),
    
    # # Misc.
    # MinionItemType("Auto Smelter", None, True, False, [
    #     "Cobblestone", "Sand", "Red Sand", "Iron", "Gold", "Oak", "Birch", 
    #     "Spruce", "Jungle", "Dark Oak", "Acacia", "Clay", "Cactus"]),
    
    # MinionItemType("Compactor", None, True, False, [
    #     "Glowstone", "Ice", "Coal", "Iron", "Gold", "Lapis", "Redstone", 
    #     "Emerald", "Quartz", "Snow", "Clay", "Wheat", "Melon", "Mushroom", 
    #     "Slime"]), # technically voidling and tarantula should as well... but why would you???
    
    MinionItemType("Super Compactor 3000", None, True, False, ["all"]),
    # MinionItemType("Dwarven Super Compactor", None, False, False, ["all"]),
    
    # # minion specific 
    # MinionItemType("Enchanted Shears", None, True, False, ["Sheep"]),
    # MinionItemType("Enchanted Egg", None, True, False, ["Chicken"]),
    # MinionItemType("Flint Shovel", None, True, False, ["Gravel"]),
)



# MINION STORAGES


@dataclass
class MinionStorageType:
    name: str
    inventory_slots: int
    
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name

STORAGES: list[None | MinionStorageType] = [
    None,
    # MinionStorageType("None", 0),
    # MinionStorageType("Small", 3),
    # MinionStorageType("Medium", 9),
    # MinionStorageType("Large", 15),
    # MinionStorageType("X-Large", 21),
    MinionStorageType("XX-Large", 27),
]

# THE MINIONS THEMSELVES

@dataclass
class MinionLevelCost:
    level: int
    seconds_per_action: int
    inventory_slots: int
    items: dict[str, int]
    npc_required: None | str

    
class MLC(MinionLevelCost):
    def __init__(self, level, seconds_per_action, inventory_slots, items, npc_required):
        super().__init__(level, seconds_per_action, inventory_slots, items, npc_required)


@dataclass
class MinionDrop:
    item: str
    amount: int
    percentage: int

@dataclass
class MinionAction:
    name: str
    drops: None | list[MinionDrop]

    
class MinionBase:
    def __init__(self, name, skill_type, crystal_bonus_percentage:int, max_pet_bonus_percentage:int, non_minion_spawning_exists, non_minion_harvest_exists, levels:list[MinionLevelCost], actions:list[MinionAction]):
        self.name = name
        self.skill_type = skill_type
        
        self.crystal_bonus_percentage = crystal_bonus_percentage
        self.max_pet_bonus_percentage = max_pet_bonus_percentage
        self.non_minion_spawning_exists = non_minion_spawning_exists
        self.non_minion_harvest_exists = non_minion_harvest_exists
        self.non_minion_harvest_and_spawning_exists = non_minion_spawning_exists and non_minion_harvest_exists
        
        self.levels:list[MLC] = levels
        self.actions:list[MinionAction] = actions
        
        self.__cumulative_level_costs = {}
        
    def get_cumulative_level_costs(self, level:int, skyblock_items: SkyblockItems):
        if level not in self.__cumulative_level_costs:
            cost = 0
            for minion_level_info_object in self.levels[:level]:
                
                for item, amount in minion_level_info_object.items.items():
                    if "Wooden" in item or "Pelts" in item:  
                        # technically pelt has value but its whatever
                        continue
                    sb_item = skyblock_items.search_by_name(item)
                    cost += sb_item.bz_sell_price * amount
                        
            self.__cumulative_level_costs[level] = cost
            
        return self.__cumulative_level_costs[level]


ISLAND_MODIFIERS = ["Derpy", "Postcard", "Beacon"]
MINION_MODIFIERS = ["Mithril Infusion", "Free Will"]

MINIONS = [
    MinionBase("Sheep", 
        skill_type="farming",
        crystal_bonus_percentage=0, 
        max_pet_bonus_percentage=False, 
        non_minion_spawning_exists=False, 
        non_minion_harvest_exists=False, 
        
        levels = [
            MLC(1, 24, 2, {"Mutton": 64, "Wooden Sword": 1}, False),
            MLC(2, 24, 4, {"Mutton": 128}, None),
            MLC(3, 22, 4, {"Mutton": 256}, None),
            MLC(4, 22, 6, {"Mutton": 512}, None),
            MLC(5, 20, 6, {"Enchanted Mutton": 8}, None),
            MLC(6, 20, 9, {"Enchanted Mutton": 24}, None),
            MLC(7, 18, 9, {"Enchanted Mutton": 64}, None),
            MLC(8, 18, 12, {"Enchanted Mutton": 128}, None),
            MLC(9, 16, 12, {"Enchanted Mutton": 256}, None),
            MLC(10, 16, 15, {"Enchanted Mutton": 512}, None),
            MLC(11, 12, 15, {"Enchanted Cooked Mutton": 8}, None),
            MLC(12, 9, 15, {"Enchanted Cooked Mutton": 16, "Pelts": 75}, "Tony"),
        ],
        
        actions = [
            MinionAction("spawn", None),
            MinionAction("harvest", [MinionDrop("Mutton", 1, 100), MinionDrop("White Wool", 1, 100)]),
        ]
    ),
    
    MinionBase("Slime",
        skill_type="combat",
        crystal_bonus_percentage=0,
        max_pet_bonus_percentage=30,
        non_minion_spawning_exists=False,
        non_minion_harvest_exists=False,
        
        levels = [
            MLC(1, 26, 2, {"Slimeball": 80, "Wooden Sword": 1}, None),
            MLC(2, 26, 4, {"Slimeball": 160}, None), 
            MLC(3, 24, 4, {"Slimeball": 320}, None),
            MLC(4, 24, 6, {"Slimeball": 512}, None),
            MLC(5, 22, 6, {"Enchanted Slimeball": 8}, None),
            MLC(6, 22, 9, {"Enchanted Slimeball": 24}, None),
            MLC(7, 19, 9, {"Enchanted Slimeball": 64}, None),
            MLC(8, 19, 12, {"Enchanted Slimeball": 128}, None),
            MLC(9, 16, 12, {"Enchanted Slimeball": 256}, None),
            MLC(10, 16, 15, {"Enchanted Slimeball": 512}, None),
            MLC(11, 12, 15, {"Enchanted Slime Block": 8}, None),
        ],
        actions = [
            MinionAction("spawn", None),
            MinionAction("harvest", [
                MinionDrop("Slimeball", 1, 100), MinionDrop("Slimeball", 1, 50), MinionDrop("Slimeball", 1, 50)])
        ]
        
    ),
    
    MinionBase("Tarantula",
        skill_type="combat",
        crystal_bonus_percentage=0,
        max_pet_bonus_percentage=0,
        non_minion_spawning_exists=False,
        non_minion_harvest_exists=True,
        
        levels = [
            MLC(1, 29, 1, {"Tarantula Web": 80, "Enchanted Fermented Spider Eye": 1}, None),
            MLC(2, 29, 3, {"Tarantula Web": 140, "String": 80, "Wooden Sword": 1}, None),
            MLC(3, 26, 3, {"Tarantula Web": 280, "String": 160}, None),
            MLC(4, 26, 6, {"Tarantula Web": 448, "String": 320}, None),
            MLC(5, 23, 6, {"Tarantula Silk": 7, "String": 512}, None),
            MLC(6, 23, 9, {"Tarantula Silk": 14, "Enchanted String": 8}, None),
            MLC(7, 19, 9, {"Tarantula Silk": 28, "Enchanted String": 16}, None),
            MLC(8, 19, 12, {"Tarantula Silk": 56, "Enchanted String": 32}, None),
            MLC(9, 14.5, 12, {"Tarantula Silk": 112, "Enchanted String": 64}, None),
            MLC(10, 14.5, 15, {"Tarantula Silk": 224, "Enchanted String": 128}, None),
            MLC(11, 10, 15, {"Tarantula Silk": 448, "Enchanted String": 256}, None),
        ],
        
        actions = [
            MinionAction("spawn", None),
            MinionAction("harvest", [
                MinionDrop("String", 3.16, 100), 
                MinionDrop("Spider Eye", 1, 100),
                MinionDrop("Iron Ingot", 1, 20),
                ]),
        ]
    ),
    
    MinionBase("Clay",
        skill_type="fishing",
        crystal_bonus_percentage=0,
        max_pet_bonus_percentage=0,
        non_minion_spawning_exists=False,
        non_minion_harvest_exists=True,
        
        levels = [
            MLC(1, 32, 1, {"CLAY_BALL": 80, "Wooden Shovel": 1}, None),
            MLC(2, 32, 3, {"CLAY_BALL": 160}, None),
            MLC(3, 30, 3, {"CLAY_BALL": 320}, None),
            MLC(4, 30, 6, {"CLAY_BALL": 512}, None),
            MLC(5, 27.5, 6, {"ENCHANTED_CLAY_BALL": 8}, None),
            MLC(6, 27.5, 9, {"ENCHANTED_CLAY_BALL": 16}, None),
            MLC(7, 24, 9, {"ENCHANTED_CLAY_BALL": 32}, None),
            MLC(8, 24, 12, {"ENCHANTED_CLAY_BALL": 64}, None),
            MLC(9, 20, 12, {"ENCHANTED_CLAY_BALL": 128}, None),
            MLC(10, 20, 15, {"ENCHANTED_CLAY_BALL": 256}, None),
            MLC(11, 16, 15, {"ENCHANTED_CLAY_BALL": 512}, None),
        ],
        
        actions = [
            MinionAction("spawn", None),
            MinionAction("harvest", [
                MinionDrop("CLAY_BALL", 4, 100), 
                ]),
        ]  
    ),
    
    MinionBase("Oak",
        skill_type="foraging",
        crystal_bonus_percentage=10, 
        max_pet_bonus_percentage=0,
        non_minion_spawning_exists=False,
        non_minion_harvest_exists=True,
        
        levels = [
            MLC(1, 48, 1, {"Oak Wood": 80, "Wooden Axe": 1}, None),
            MLC(2, 48, 3, {"Oak Wood": 160}, None),
            MLC(3, 45, 3, {"Oak Wood": 320}, None),
            MLC(4, 45, 6, {"Oak Wood": 512}, None),
            MLC(5, 42, 6, {"Enchanted Oak Wood": 8}, None),
            MLC(6, 42, 9, {"Enchanted Oak Wood": 16}, None),
            MLC(7, 38, 9, {"Enchanted Oak Wood": 32}, None),
            MLC(8, 38, 12, {"Enchanted Oak Wood": 64}, None),
            MLC(9, 33, 12, {"Enchanted Oak Wood": 128}, None),
            MLC(10, 33, 15, {"Enchanted Oak Wood": 256}, None),
            MLC(11, 27, 15, {"Enchanted Oak Wood": 512}, None),
        ],
        
        actions = [
            MinionAction("spawn", None),
            MinionAction("harvest", [
                MinionDrop("Oak Wood", 4, 100),
                ]),
        ]
    ),
    
    MinionBase("Magma Cube",
        skill_type="combat",
        crystal_bonus_percentage=0,
        max_pet_bonus_percentage=30,
        non_minion_spawning_exists=False,
        non_minion_harvest_exists=True,
        
        levels = [
            MLC(1, 32, 2, {"Magma Cream": 80, "Wooden Sword": 1}, None),
            MLC(2, 32, 4, {"Magma Cream": 160}, None),
            MLC(3, 30, 4, {"Magma Cream": 320}, None), 
            MLC(4, 30, 6, {"Magma Cream": 512}, None),
            MLC(5, 28, 6, {"Enchanted Magma Cream": 8}, None),
            MLC(6, 28, 9, {"Enchanted Magma Cream": 16}, None),
            MLC(7, 25, 9, {"Enchanted Magma Cream": 32}, None),
            MLC(8, 25, 12, {"Enchanted Magma Cream": 64}, None),
            MLC(9, 22, 12, {"Enchanted Magma Cream": 128}, None),
            MLC(10, 22, 15, {"Enchanted Magma Cream": 256}, None),
            MLC(11, 18, 15, {"Enchanted Magma Cream": 512}, None),
            MLC(12, 16, 15, {"Enchanted Magma Cream": 1024, "coins": 2000000}, "Hilda"),
        ],
        
        actions = [
            MinionAction("spawn", None),
            MinionAction("harvest", [MinionDrop("Magma Cream", 1.8, 100)])
        ]
    ),
        
               
    
    
    
    
    # MinionBase("cobblestone", "mining", False, False, False, True,
    #     levels = [
    #         MLC(1, 14, 64/64, {"cobblestone": 80, "Wooden_pickaxe": 1}, None),
    #         MLC(2, 14, 192/64, {"cobblestone": 160}, None),
    #         MLC(3, 12, 192/64, {"cobblestone": 320}, None),
    #         MLC(4, 12, 384/64, {"cobblestone": 512}, None),
    #         MLC(5, 10, 384/64, {"enchanted_cobblestone": 8}, None),
    #         MLC(6, 10, 576/64, {"enchanted_cobblestone": 16}, None),
    #         MLC(7, 9, 576/64, {"enchanted_cobblestone": 32}, None),
    #         MLC(8, 9, 768/64, {"enchanted_cobblestone": 64}, None),
    #         MLC(9, 9, 768/64, {"enchanted_cobblestone": 128}, None),
    #         MLC(10, 8, 960/64, {"enchanted_cobblestone": 256}, None),
    #         MLC(11, 7, 960/64, {"enchanted_cobblestone": 512}, None),
    #         MLC(12, 6, 960/64, {"enchanted_cobblestone": 1024, "coins": 2000000}, "Bulvar"),
    #     ]
    # ),
]
