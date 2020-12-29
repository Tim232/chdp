from inspect import iscoroutinefunction
from time import time
from importlib import reload, import_module
from os import listdir
from asyncio import sleep, gather
from json import load, dump

def importm(thang: str) -> object: return import_module(str(thang))
def reloadm(thang: str) -> object: return reload(importm(str(thang)))

def get_varnames(func: object) -> list:  return list(func.__code__.co_varnames)
def check_async(o: object) -> bool: return bool(iscoroutinefunction(o))

def get_json(filename: str, encoding = 'utf-8') -> dict: return load(open(str(filename), 'r', encoding = str(encoding)))
def save_json(filename: str, data: dict, encoding = 'utf-8', indent = '\t') -> dict:
    with open(str(filename), 'w', encoding = str(encoding)) as f: dump(dict(data), f, indent = str(indent), ensure_ascii = False)
    return data

async def use_func(func, *args, **kwargs):
    if check_async(func): res = await func(*args, **kwargs)
    else: res = func(*args, **kwargs)
    return res

def dir_object(thang: object) -> list: return list(dir(thang))
def dir_list(directory: str) -> list: return list(listdir(str(directory)))

def get_time() -> float: return float(time())

async def async_sleep(second: int) -> int: 
    await sleep(int(second))
    return int(second)

async def async_gather(first_arg, *args): 
    if args:
        if type(first_arg) == list: res = await gather(*first_arg, *args)
        else: res = await gather(first_arg, *args)
    else:
        if type(first_arg) == list: res = await gather(*first_arg)
        else: res = await first_arg
    return res