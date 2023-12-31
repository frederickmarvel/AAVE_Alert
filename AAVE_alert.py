import requests
import telegram
import time
import asyncio

WHITELISTED_CHAT_IDS = [1489703363, 5028701122]  

def aavescan_req(threshold):
    api_url = 'https://api.thegraph.com/subgraphs/name/aave/protocol-v3-polygon'
    headers = {
        'Content-Type': 'application/json'
    }

    query = {
        "query": """
            query Reserves {
                reserves(first: 100) {
                    id
                    name
                    decimals
                    symbol
                    liquidityRate
                    variableBorrowRate
                    stableBorrowRate
                    totalLiquidity
                    utilizationRate
                    availableLiquidity
                    liquidityIndex
                    totalCurrentVariableDebt
                    price {
                        priceInEth
                        oracle {
                            usdPriceEth
                        }
                    }
                }
            }
        """
    }
    response = requests.post(api_url, json=query, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for reserve in data['data']['reserves']:
            if reserve['symbol'] == 'USDT':
                variable_borrow_rate = float(reserve['variableBorrowRate'])/ 10000000000000000000000000
                if variable_borrow_rate > threshold:
                    borrow_rate = variable_borrow_rate
                    processed_data = {
                        'name': reserve['name'],
                        'symbol': reserve['symbol'],
                        'liquidity': reserve['totalLiquidity'],
                        'price_eth': float(reserve['price']['priceInEth'])/100000000,
                        'variable_borrow_rate': borrow_rate
                    }
                    return processed_data, True
                else:
                    return None, False
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None, False

async def send_to_telegram(data, threshold_crossed):
    bot_token = '6469465654:AAHAYHDOhoJWATlQFyOXThGKysOEDnhEBds'
    bot = telegram.Bot(token=bot_token)
    message = f"⚠️ Threshold crossed!\nToken: {data['symbol']}\nName: {data['name']}\nLiquidity: {data['liquidity']}\nPrice: {data['price_eth']}\nVariable Borrow Rate: {data['variable_borrow_rate']}"
    
    for chat_id in WHITELISTED_CHAT_IDS:
        if threshold_crossed:
            await bot.send_message(chat_id=chat_id, text=message) 

async def main():
    threshold = 2

    while True:
        data, threshold_crossed = aavescan_req(threshold)

        if data:
            await send_to_telegram(data, threshold_crossed)

        await asyncio.sleep(10) 

if __name__ == "__main__":
    asyncio.run(main())  