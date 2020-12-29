from .chdp_funcs import importm, reloadm, dir_list, dir_object
from .errors import CommandClassNotFound

class Handler:
    cmds = []

    def __init__(self, command_dir: str = 'commands', sub_dir: bool = True, ignore_folder: list = ['__pycache__', 'node_modules'], ignore_file: list = ['test.py']):
        # Configuration
        self.command_dir = str(command_dir)
        self.sub_dir = bool(sub_dir)
        self.ignore = list(list(ignore_folder) + list(ignore_file))

    def search_files(self, base: str, end: str = '.py') -> list:
        files = [[base + '/' + x, base] for x in list(filter(lambda x: str(x).endswith(str(end)) and str(x) not in self.ignore, dir_list(base)))] # 무시할 파일들 필터림
        folders = list(filter(lambda x: '.' not in str(x) and str(x) not in self.ignore, dir_list(base))) # 파일들 검색
        for f in folders: files.extend(self.search_files(base + '/' + str(f)))
        return files
    
    def gather_commands(self) -> list:
        if not self.sub_dir: files = [[self.command_dir + '/' + x, 'no category'] for x in list(filter(lambda x: str(x).endswith('.py') and str(x) not in self.ignore, dir_list(self.command_dir)))] # sub_dir 비활성화
        else: files = self.search_files(self.command_dir) # 파일들 검색
        for f in files: self.add_cmd(f[0], f[1]) # 명령어 추가
        return self.cmds

    def add_cmd(self, cmd: str, ct: str): 
        m = self.get_cmd(cmd)
        if not m: raise CommandClassNotFound
        setattr(m, 'category', str(ct))
        self.cmds.append(m)
        return m
    
    def get_cmd(self, cmd: str, reload: bool = False):
        cmd = self.dir_to_module(cmd)
        if reload: m = reloadm(str(cmd))
        else: m = importm(str(cmd))
        d = dir_object(m)
        if 'Command' not in d: return None
        c = m.Command()
        if 'name' not in dir_object(c): return None
        else: return c

    def reload_cmd(self, cmd: str): 
        m = self.get_cmd(cmd)
        if m: raise CommandClassNotFound
        self.cmds.remove(m)
        m = self.get_cmd(cmd, True)
        self.cmds.append(m)
        return m

    def remove_cmd(self, cmd: str):
        m = self.get_cmd(cmd)
        if m: raise CommandClassNotFound
        self.cmds.remove(m)
        return m
    
    def dir_to_module(self, string: str):
        return str(string).split('.')[0].replace('/', '.')