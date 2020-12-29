class Command:
    name = '핑'
    async def run(self, client, message, ext): await message.channel.send('퐁')