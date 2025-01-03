import requests
import json
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class OrderSummary:
    amount: int
    pricePerUnit: float
    orders: int

@dataclass
class QuickStatus:
    productId: str
    sellPrice: float
    sellVolume: int
    sellMovingWeek: int
    sellOrders: int
    buyPrice: float
    buyVolume: int
    buyMovingWeek: int
    buyOrders: int

@dataclass
class Product:
    product_id: str
    sell_summary: List[OrderSummary]
    buy_summary: List[OrderSummary]
    quick_status: QuickStatus

@dataclass
class BazaarResponse:
    success: bool
    lastUpdated: int
    products: dict[str, Product]

@dataclass
class SBItem:
    name: str
    sb_id: str
    bz_sell_price: Optional[float]
    bz_buy_price: Optional[float]
    bz_weekly_sell_volume: Optional[int]
    bz_weekly_buy_volume: Optional[int]
    npc_sell_price: Optional[int]
    
    auction_average_buy_price: Optional[int] = None
    
    def lowest_price(self) -> int:
        if self.bz_sell_price is not None:
            return self.bz_sell_price
        if self.auction_average_buy_price is not None:
            return self.auction_average_buy_price
        raise ValueError(f"Item '{self.name}' has no price data")

class SkyblockItems:
    def __init__(self, only_bazaar=True):
        self.bazaar_data = self.fetch_bazaar_data()
        self.items = self.fetch_items(only_bazaar)

    def fetch_items(self, only_bazaar=True) -> List[SBItem]:
        response = requests.get("https://api.hypixel.net/v2/resources/skyblock/items")
        data = response.json()
        items = [
            SBItem(
                name=item["name"],
                sb_id=item["id"],
                bz_sell_price=self.bazaar_data.products[item["id"]].quick_status.sellPrice if item["id"] in self.bazaar_data.products else None,
                bz_buy_price=self.bazaar_data.products[item["id"]].quick_status.buyPrice if item["id"] in self.bazaar_data.products else None,
                bz_weekly_sell_volume=self.bazaar_data.products[item["id"]].quick_status.sellMovingWeek if item["id"] in self.bazaar_data.products else None,
                bz_weekly_buy_volume=self.bazaar_data.products[item["id"]].quick_status.buyMovingWeek if item["id"] in self.bazaar_data.products else None,
                npc_sell_price=item.get("npc_sell_price")
            )
            for item in data["items"]
        ]
        
        if only_bazaar:
            items = [item for item in items if item.bz_sell_price is not None or item.bz_buy_price is not None]
        return items

    def fetch_bazaar_data(self) -> BazaarResponse:
        response = requests.get("https://api.hypixel.net/v2/skyblock/bazaar")
        data = response.json()
        
        products = {
            k: Product(
                product_id=v["product_id"],
                sell_summary=[OrderSummary(**s) for s in v["sell_summary"]],
                buy_summary=[OrderSummary(**b) for b in v["buy_summary"]],
                quick_status=QuickStatus(**v["quick_status"])
            )
            for k, v in data["products"].items()
        }
        return BazaarResponse(success=data["success"], lastUpdated=data["lastUpdated"], products=products)

    def search_by_name(self, name: str) -> SBItem:
        item = next((item for item in self.items if item.name == name), None)
        if item is None:
            raise ValueError(f"Item with name '{name}' not found")
        return item

    def search_by_sb_id(self, sb_id: str) -> Optional[SBItem]:
        return next((item for item in self.items if item.sb_id == sb_id), None)

    def export_to_json(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump([item.__dict__ for item in self.items], f, indent=4)
    
    def attempt_fetch_auction_data(self, item: SBItem):
        if item.auction_average_buy_price is not None:
            return
        assert item.bz_buy_price == None
        
        response = requests.get(f"https://sky.coflnet.com/api/auctions/tag/{item.sb_id}/active/overview")
        data = response.json()
        
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch auction data for item '{item.name}'")
        
        total = 0
        
        for auction in data:
            total += auction["price"]
        
        avg = int(total / len(data))
        item.auction_average_buy_price = avg
        
        print(f"Fetched auction data for '{item.name}' (${item.auction_average_buy_price}) from cofl.net")
    
    

# Example usage:
skyblock_items = SkyblockItems()
# item = skyblock_items.search_by_name("Farm Armor Chestplate")
skyblock_items.export_to_json("data/sb_items.json")