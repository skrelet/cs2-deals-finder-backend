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
    try:
        # Fetch Skinport data (official API)
        skinport_url = "https://api.skinport.com/v1/items?app_id=730&currency=USD"
        sp_resp = requests.get(skinport_url, timeout=10)
        if sp_resp.status_code != 200:
            return {"error": "Failed to fetch Skinport data"}
        skinport = sp_resp.json()

        # Example: find items with discount > 10% vs suggested price
        deals = []
        for item in skinport:
            min_price = float(item.get("min_price") or 0)
            suggested = float(item.get("suggested_price") or 0)
            if suggested > 0 and min_price < suggested * 0.9:
                deals.append({
                    "name": item["market_hash_name"],
                    "min_price": min_price,
                    "suggested_price": suggested,
                    "discount": round((1 - min_price / suggested) * 100, 2)
                })

        deals = sorted(deals, key=lambda x: x["discount"], reverse=True)
        return {"deals": deals[:50]}

    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}
