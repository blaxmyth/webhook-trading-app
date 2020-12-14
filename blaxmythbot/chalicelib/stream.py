import asyncio
import websocket
import requests
from chalicelib import config
import json

ws_endpoint = 'wss://ws.tradier.com/v1/'

response = requests.post('https://api.tradier.com/v1/markets/events/session',
    data={},
    headers={'Authorization': 'Bearer {}'.format(config.PROD_TOKEN), 'Accept': 'application/json'}
)
json_response = response.json()
print(response.status_code)
print(json_response['stream']['sessionid'])



# async def connect_and_consume():
#   uri = "wss://ws.tradier.com/v1/markets/events"
#   async with websockets.connect(uri) as websocket:
#     payload = '{"symbols": ["SPY"], "sessionid": {}, "linebreak": true}'.format(session_id)

#     await websocket.send(payload)
#     print(f"> {payload}")

#     while True:
#       response = await websocket.recv()
#       print(f"< {response}")

# asyncio.get_event_loop().run_until_complete(connect_and_consume())

headers = {
  'Accept': 'application/json'
}

payload = { 
  'sessionid': json_response['stream']['sessionid'],
  'symbols': 'SPY',
  'linebreak': True
}

r = requests.get('https://stream.tradier.com/v1/markets/events', stream=True, params=payload, headers=headers)
print(r)
for line in r.iter_lines():
  if line:
    print(json.loads(line))