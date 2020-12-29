from discord import (
    AutoShardedClient, 
    Color, 
    Status, 
    Game, 
    Status, 
    Embed, 
    TextChannel, 
    Role, 
    Member, 
    Reaction, 
    Message
)

from .chdp_funcs import (
    dir_object,
    get_json,
    save_json,
    get_time,
    async_sleep,
    async_gather,
    use_func
)

from .errors import (
    AsyncTimeoutError, 
    SpaceinPrefixError
)

from .handler import Handler

class Extension: 
    def __init__(self, index: str, args: list, first_member: Member, first_channel: TextChannel, first_role: Role):
        self.index = str(index)
        self.args = list(args)
        self.first_member = first_member
        self.first_channel = first_channel
        self.first_role = first_role

class CHDPClient(AutoShardedClient):
    def __init__(self, config_file = 'config.json'):
        super().__init__()

        self.config_file = str(config_file)
        self.config_data = get_json(self.config_file)

        # Use Configuration
        self.token = self.config_data['token']
        try: self.is_bot = self.config_data['bot']
        except KeyError: self.is_bot = True
        try: self.prefix = self.config_data['prefix']
        except KeyError: self.prefix = '' 
        if ' ' in self.prefix: raise SpaceinPrefixError('Space in Prefix')
        self.ix = self.prefix.count(' ')
        try: command_dir = self.config_data['handler']['command_dir']
        except KeyError: command_dir = 'commands'
        try: sub_dir = self.config_data['handler']['sub_dir']
        except KeyError: sub_dir = True
        try: ignore_folder = self.config_data['handler']['ignore_folder']
        except KeyError: ignore_folder = ['__pycache__', 'node_modules']
        try: ignore_file = self.config_data['handler']['ignore_file']
        except KeyError: ignore_file = ['test.py']
        try: self.blacklist = self.config_data['blacklist']
        except KeyError: 
            self.blacklist = []
            self.config_data['blacklist'] = []
        try: self.botdev = self.config_data['botdev']
        except KeyError: 
            self.botdev = []
            self.config_data['botdev'] = []
        save_json(self.config_file, self.config_data)

        """
        Config.json Example
        {
            "token": "Your Token",
            "prefix": "Your Prefix (Default to '')",
            "blacklist": [
                Blacklist ID list (Integers)
            ],
            "botdev": [
                Bot developer ID list (Integers)
            ],
            "handler": {
                "command_dir": "Command Folder (Default to 'commands')",
                "sub_dir": (true, false) If to use sub_dir (Default to True),
                "ignore_folder": [
                    Folders to Ignore (Strings) (Default to ['__pycache__', 'node_modules'])
                ],
                "ignore_file": [
                    Files to Ignore (Strings) (Default to ['test.py'])
                ]
            }
        }
        """

        self.cooltimelist = {}

        # Get Commands
        self.command_handler = Handler(command_dir, sub_dir, ignore_folder, ignore_file)
        self.command_handler.gather_commands()
        self.cmds = self.command_handler.cmds
    
    def run_bot(self, **kwargs):
        self.starttime = get_time() # 업타임 계산을 위해
        return self.run(self.token, bot = self.is_bot, **kwargs)
    
    @property
    def uptime(self) -> float: return get_time() - self.starttime

    async def change_presence_loop(self, games: list, wait: int = 5, status = Status.online, activity = Game, *args, **kwargs):
        await self.wait_until_ready()

        while not self.is_closed():
            for game in games:
                await self.change_presence(status = status, activity = activity(str(game).replace('[u]', str(len(super().users))).replace('[g]', str(len(super().guilds))).replace('[p]', self.prefix), *args, **kwargs))
                await async_sleep(int(wait))
    
    async def use_cmd(self, message: Message) -> bool:
        if not message.content.startswith(self.prefix): return
        if message.author.bot: return
        if message.author.id in self.blacklist: return
        if str(message.channel.type) != 'text': return

        index = message.content.split(self.prefix)[1].split(' ')[0]
        try: args = message.content.split(index)[1][self.ix:].split(' ')[1:]
        except: args = []

        async def run(c):
            ext = Extension(index, args, self.get_user_msg(message, args), self.get_channel_msg(message, args), self.get_role_msg(message, args))
            dirs = dir_object(c)

            if 'check' in dirs: 
                res = await use_func(c.check, self, message, ext)
                if not res: return 
            if 'user_per' in dirs:
                r = self.check_permissions(message.author, c.user_per)
                if r:
                    if 'user_no_permission' in dirs: return await use_func(c.user_no_permission, self, message, ext, r) 
                    else: return
            if 'bot_per' in dirs:
                r = self.check_permissions(message.guild.me, c.bot_per)
                if r:
                    if 'bot_no_permission' in dirs: return await use_func(c.bot_no_permission, self, message, ext, r) 
                    else: return
            if 'cooltime' not in dirs: await use_func(c.run, self, message, ext)
            else:
                if not c.name in self.cooltimelist.keys(): self.cooltimelist[str(c.name)] = {}
                if not str(message.author.id) in self.cooltimelist[str(c.name)].keys(): 
                    self.cooltimelist[str(c.name)][str(message.author.id)] = get_time()
                    await use_func(c.run, self, message, ext)
                elif get_time() - self.cooltimelist[str(c.name)][str(message.author.id)] >= int(c.cooltime):
                    self.cooltimelist[str(c.name)][str(message.author.id)] = get_time()
                    await use_func(c.run, self, message, ext)
                else: 
                    if 'cooltime_nopass' in dirs: return await use_func(c.cooltime_nopass, self, message, ext)
            if 'after_run' in dirs: await use_func(c.after_run, self, message, ext)

        for m in self.cmds:
            dirs = dir_object(m)
            if 'aliases' not in dirs:
                if index == m.name: 
                    await run(m)
                    return True
            else: 
                if index in m.aliases or index == m.name: 
                    await run(m)
                    return True
    
    # permission check

    def check_permissions(self, author: Member, ps: list) -> bool:
        fail = list(filter(lambda x: not self.check_permission(author, x), ps))
        if not fail: return None
        else: return list(fail)

    def check_permission(self, author: Member, p: str) -> bool:
        memper = author.guild_permissions
        p = str(p).replace(' ', '_').replace(' ', '').lower()
        if not p: return True
        if p in ['botdev', 'dev', 'developer']: return author.id in self.botdev
        elif p in ['guildowner', 'owner', 'serverowner']: return bool(author.guild.owner == author)
        elif memper.administrator: return True
        elif p in ['create_instance_invite', 'create_invite', 'make_invite'] and memper.create_instance_invite: return True
        elif p in ['kick_members', 'kick'] and memper.kick_members: return True
        elif p in ['ban_members', 'ban'] and memper.ban_members: return True
        elif p in ['manage_channels', 'manage_channel'] and memper.manage_channels: return True
        elif p in ['manage_guild'] and memper.manage_guild: return True
        elif p in ['add_reactions', 'react'] and memper.add_reactions: return True
        elif p in ['view_audit_log', 'log'] and memper.view_audit_log: return True
        elif p in ['priority_speaker'] and memper.priority_speaker: return True
        elif p in ['stream', 'golive'] and memper.stream: return True
        elif p in ['send_tts', 'tts'] and memper.send_tts: return True
        elif p in ['mention_everyone', 'everyone'] and memper.mention_everyone: return True
        elif p in ['external_emojis'] and memper.external_emojis: return True
        elif p in ['view_guild_insights', 'insight'] and memper.view_guild_insights: return True
        elif p in ['connect'] and memper.connect: return True
        elif p in ['speak'] and memper.speak: return True
        elif p in ['mute_members', 'mute'] and memper.mute_members: return True
        elif p in ['deafen_members', 'deaf'] and memper.deafen_members: return True
        elif p in ['move_members', 'move'] and memper.move_members: return True
        elif p in ['manage_emojis'] and memper.manage_emojis: return True
        elif p in ['manage_webhooks'] and memper.manage_webhooks: return True
        elif p in ['manage_roles'] and memper.manage_roles: return True
        elif p in ['manage_nicknames'] and memper.manage_nicknames and memper.change_nickname: return True
        elif p in ['use_voice_activation'] and memper.use_voice_activation: return True
        else: return False
    
    # get things

    async def get_reaction(self, msg: Message, message: Message, emojilist: list = ['⭕', '❌'], timeout: int = 60, cls_reaction: bool = False, embed: Embed = Embed(title = '시간이 종료되었습니다', description = f'정해진 시간이 끝나서 자동으로 반응 콜랙터가 종료되었습니다', color = Color.red())) -> Reaction:
        for e in emojilist: await message.add_reaction(str(e))
        try: reaction = list(await self.wait_for('reaction_add', timeout = timeout, check = lambda r, u: r.message.id == message.id and u == msg.author and str(r.emoji) in emojilist))[0]
        except AsyncTimeoutError:
            await async_gather(message.delete(), message.channel.send(embed = embed))
            return None
        else:
            try: await message.clear_reactions()
            except: pass
            return reaction
    
    async def get_message(self, message: Message, timeout: int = 60, embed: Embed = Embed(title = '시간이 종료되었습니다', description = f'정해진 시간이 끝나서 자동으로 메시지 콜랙터가 종료되었습니다', color = Color.red())) -> Message:
        try: m = await self.wait_for('message', timeout = timeout, check = lambda m: m.channel == message.channel and m.author == message.author)
        except AsyncTimeoutError:
            await message.channel.send(embed = embed)
            return None
        else: return m
    
    # get from message

    def get_user_msg(self, message: Message, args: list, index: int = 0) -> Member:
        member = message.mentions
        try:
            if member[0]: return member[0]
        except: pass
        try: userid = args[int(index)]
        except: return None
        if userid == '봇': return message.guild.me
        try: user = list(filter(lambda m: m.display_name == userid or m.name == userid, message.guild.members))[0]
        except: pass
        else: return user
        try: user = message.guild.get_member(int(userid))
        except: return None
        if user: return user
        return None
    
    def get_channel_msg(self, message: Message, args: list, index: int = 0) -> TextChannel:
        channels = message.channel_mentions
        try:
            if channels[0]: return channels[0]
        except: pass
        try: chanid = args[int(index)]
        except: return None
        if chanid == '여기': return message.channel
        try: chan = list(filter(lambda m: m.name == chanid, message.guild.channels))[0]
        except: pass
        else: return chan
        try: chan = message.guild.get_channel(int(chanid))
        except: return None
        if chan: return chan
        return None
    
    def get_role_msg(self, message: Message, args: list, index: int = 0) -> Role:
        role = message.role_mentions
        try:
            if role[0]: return role[0]
        except: pass
        try: roleid = args[int(index)]
        except: return None
        try: role = list(filter(lambda m: m.name == roleid, message.author.roles))[0]
        except: pass
        else: return role
        try: role = message.guild.get_role(int(roleid))
        except: return None
        if role: return role
        return None
    
    def get_int_msg(self, message: Message, args: list) -> int:
        if not args[0]: return None
        try: a = int(args[0])
        except ValueError: return None
        return a

    def get_code_msg(self, message: Message, lang: str = 'py') -> str:
        try: code = message.content.split(f'```{lang}')[1].split('```')[0]
        except IndexError: return None
        return str(code)
    
    # settings
    
    def append_botdev(self, id: int) -> bool:
        id = int(id)
        if id in self.config_data['botdev']: return False
        self.config_data['botdev'].append(id)
        self.botdev.append(id)
        save_json(self.config_file, self.config_data)
        return True
    
    def remove_botdev(self, id: int) -> bool:
        id = int(id)
        if id in self.config_data['botdev']: return False
        self.config_data['botdev'].remove(id)
        self.botdev.remove(id)
        save_json(self.config_file, self.config_data)
        return True
    
    def append_black(self, id: int) -> bool:
        id = int(id)
        if id in self.config_data['black']: return False
        self.config_data['black'].append(id)
        self.blacklist.append(id)
        save_json(self.config_file, self.config_data)
        return True
    
    def remove_black(self, id: int) -> bool:
        id = int(id)
        if id in self.config_data['black']: return False
        self.config_data['black'].remove(id)
        self.blacklist.remove(id)
        save_json(self.config_file, self.config_data)
        return True