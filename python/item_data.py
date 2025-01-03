from dataclasses import dataclass
from enum import Enum

SMELT_MAP = {
        "Cobblestone": "Stone",
        "Sand": "Glass",
        "Red Sand": "Red Glass",
        "Iron Ore": "Iron Ingot",
        "Gold Ore": "Gold Ingot",
        "Oak Wood": "Coal",
        "Birch Wood": "Coal",
        "Spruce Wood": "Coal",
        "Jungle Wood": "Coal",
        "Dark Oak Wood": "Coal",
        "Acacia Wood": "Coal",
        "Clay": "Brick",
        "Cactus": "Cactus Green"
    }

def is_smeltable(item:str) -> bool:
    return item in SMELT_MAP

def convert_to_smelted(item:str) -> str:
    return SMELT_MAP.get(item, item)

@dataclass
class ItemCompactor:
    input_item: str
    input_count: int
    output_item: str

COMPACTOR_MAP:dict[str, ItemCompactor] = {
    "Glowstone Dust": ItemCompactor("Glowstone Dust", 4, "Glowstone"),
    "Ice": ItemCompactor("Ice", 4, "Packed Ice"),
    "Coal": ItemCompactor("Coal", 9, "Block of Coal"), 
    "Iron Ingot": ItemCompactor("Iron Ingot", 9, "Block of Iron"),
    "Gold Ingot": ItemCompactor("Gold Ingot", 9, "Block of Gold"),
    "Lapis Lazuli": ItemCompactor("Lapis Lazuli", 9, "Lapis Lazuli Block"),
    "Redstone": ItemCompactor("Redstone", 9, "Block of Redstone"),
    "Emerald": ItemCompactor("Emerald", 9, "Block of Emerald"), 
    "Nether Quartz": ItemCompactor("Nether Quartz", 4, "Block of Quartz"),
    "Snowball": ItemCompactor("Snowball", 4, "Snow Block"),
    "Clay": ItemCompactor("Clay", 4, "Clay Block"),
    "Wheat": ItemCompactor("Wheat", 9, "Hay Bale"),
    "Melon": ItemCompactor("Melon", 9, "Melon Block"),
    "Red Mushroom": ItemCompactor("Red Mushroom", 9, "Red Mushroom Block"), 
    "Brown Mushroom": ItemCompactor("Brown Mushroom", 9, "Brown Mushroom Block"),
    "Slimeball": ItemCompactor("Slimeball", 9, "Slime Block")
}

def is_compactable(item:str) -> bool:
    return item in COMPACTOR_MAP

def convert_to_compacted(item:str) -> ItemCompactor:
    assert item in COMPACTOR_MAP
    return COMPACTOR_MAP.get(item)

SUPER_COMPACTOR_MAP:dict[str, ItemCompactor] = {
    "Mutton": ItemCompactor("Mutton", 160, "Enchanted Mutton"),
    "Enchanted Mutton": ItemCompactor("Enchanted Mutton", 160, "Enchanted Cooked Mutton"),
    "White Wool": ItemCompactor("White Wool", 160, "Enchanted Wool"),
    "Sulphur": ItemCompactor("Sulphur", 160, "Enchanted Sulphur"),
}


def is_super_compactable(item:str) -> bool:
    return item in SUPER_COMPACTOR_MAP

def convert_to_super_compacted(item:str) -> ItemCompactor:
    assert item in SUPER_COMPACTOR_MAP
    return SUPER_COMPACTOR_MAP.get(item)

@dataclass
class Item:
    name: str
    hypixel_id: str
    npc_price: int
    bazaar_sell_order_price: float
    
