import requests
import telegram
import time

def aavescan_req():
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
              variable_borrow_rate = reserve['variableBorrowRate']
              if variable_borrow_rate > threshold:
                  processed_data = {
                      'name': reserve['name'],
                      'symbol': reserve['symbol'],
                      'liquidity': reserve['totalLiquidity'],
                      'price_eth': reserve['price']['priceInEth'],
                      'borrow_rate': reserve['variableBorrowRate']/1000000000000000000000000000
                  }
                  return processed_data, True  
              else:
                  return None, False  
  else:
    print(f"Request failed with status code: {response.status_code}")
    return None, False
    
def send_to_telegram(data, threshold_crossed):
    bot_token = '6469465654:AAHAYHDOhoJWATlQFyOXThGKysOEDnhEBds'
    chat_id = '5028701122'

    bot = telegram.Bot(token=bot_token)
    if threshold_crossed:
        message = f"⚠️ Threshold crossed!\nToken: {data['symbol']}\nName: {data['name']}\nLiquidity: {data['liquidity']}\nPrice (ETH): {data['price_eth']}\nVariable Borrow Rate: {data['variable_borrow_rate']}"
    else:
        message = f"Token: {data['symbol']}\nName: {data['name']}\nLiquidity: {data['liquidity']}\nPrice (ETH): {data['price_eth']}"

    bot.send_message(chat_id=chat_id, text=message)
  
def main():
    threshold = 0.1  

    while True:
        data, threshold_crossed = aavescan_req(threshold)

        if data:
            send_to_telegram(data, threshold_crossed)

        time.sleep(3600)  

if __name__ == "__main__":
    main()