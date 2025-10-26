from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/deals")
def get_deals():
    buff_url = "https://buff.163.com/api/market/goods/sell_order?game=csgo&page_num=1"
    buff = requests.get(buff_url).json()
    skinport_url = "https://api.skinport.com/v1/items?app_id=730&currency=USD"
    skinport = requests.get(skinport_url).json()

    deals = []
    for item in buff["data"]["items"]:
        name = item["market_hash_name"]
        buff_price = float(item["sell_min_price"])

        sp_item = next((x for x in skinport if x["market_hash_name"] == name), None)
        if sp_item:
            skinport_price = float(sp_item["min_price"])
            if skinport_price > 0 and buff_price < skinport_price * 0.9:
                deals.append({
                    "name": name,
                    "buff_price": buff_price,
                    "skinport_price": skinport_price,
                    "discount": round((1 - buff_price / skinport_price) * 100, 2)
                })

    deals = sorted(deals, key=lambda x: x["discount"], reverse=True)
    return {"deals": deals[:50]}
