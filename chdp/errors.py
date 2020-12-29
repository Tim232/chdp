from asyncio import TimeoutError

class CHDPException(Exception): pass
class HandlerException(CHDPException): pass

class CommandClassNotFound(HandlerException):
    msg = '모듈 안에 "Command" 클래스가 없습니다\nNo Class named "Command" in the module'

    def __init__(self) -> Exception: super().__init__(self.msg)
    def __str__(self) -> str: return self.msg

class AsyncTimeoutError(TimeoutError): pass

class SpaceinPrefixError(CHDPException): pass