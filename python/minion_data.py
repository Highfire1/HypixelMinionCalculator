from dataclasses import dataclass

# ============== MINION FUELS ==============

@dataclass
class MinionFuelType:
    name: str
    duration_hours: None | int
    percentage_boost: None | int
    special_case: bool
    

FUEL_TYPES = (
    # None,
    # MinionFuelType("None", None, None, True),
    # MinionFuelType("Block of Coal", 5, 5, False),
    # MinionFuelType("Enchanted Bread", 12, 5, False),
    # MinionFuelType("Enchanted Coal", 24, 10, False),
    # MinionFuelType("Enchanted Charcoal", 24, 10, False),
    # MinionFuelType("Solar Panel", None, None, True),
    MinionFuelType("Enchanted Lava Bucket", None, 25, False),
    MinionFuelType("Magma Bucket", None, 30, False),
    MinionFuelType("Plasma Bucket", None, 30, False),
    
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
    # None,
    # MinionStorageType("None", 0),
    # MinionStorageType("Small", 3),
    # MinionStorageType("Medium", 9),
    MinionStorageType("Large", 15),
    # MinionStorageType("X-Large", 21),
    # MinionStorageType("XX-Large", 27),
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
        
        self.levels = levels
        self.actions = actions


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
            MinionAction("harvest", [MinionDrop("Slimeball", 1, 100), MinionDrop("Slimeball", 1, 50), MinionDrop("Slimeball", 1, 50)])
        ]
        
    )
    
    
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
