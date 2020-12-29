from chdp import CHDPClient
client = CHDPClient()

@client.event
async def on_ready():
    print('ready')

@client.event
async def on_message(message):
    await client.use_cmd(message)

client.run_bot()