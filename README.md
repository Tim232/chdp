# CHDP
Command Handler for Discord.Py

⚠ 해당 프로젝트는  AGPL-3.0 License 입니다 ⚠


## Download
```shell
$ pip install chdp
```

## Use
1. Create Main file and config.json and folder **commands**

2. Fill config.json like below
```json
{
    "token": "Your Token",
    "prefix": "Your Prefix"
}
```

3. create a file in folder **commands** and fill it like below
```python
class Command:
    name = 'ping'
    async def run(self, client, message, ext): await message.channel.send('pong')
```

4. Run the Main file

## Contribute
Find a bug and tell it on the Issue tab or to 키키#7000 on discord

You can also Pull a request


## Log
4.0.7: Permission Handler Upgrade
+ 원더님 감사합니다! 님이 포크해준것 덕분에 복원할수 있었어요!

4.0.8: Added Category and added more help and edited Extension class, edited lot of functions

4.0.9: Fixed Fatal Error
