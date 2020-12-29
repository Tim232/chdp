import setuptools

setuptools.setup(
    name = 'chdp',
    version = '4.0.9',
    description = 'Command Handler for Discord.Py',
    author = 'kiki7000',
    author_email = 'devkiki7000@gmail.com',
    url = 'https://github.com/kiki7000/chdp',
    packages = setuptools.find_packages(),
    license = 'GPL-V3',
    long_description = open('README.md', 'r', encoding = 'utf-8').read(),
    long_description_content_type = 'text/markdown',
    keywords = ['discord', 'discord.py', 'commandhandler', 'chdp', 'handler', 'command', 'kiki'],
    python_requires = '>=3.8',
    install_requires = ['discord.py', 'asyncio', 'importlib'],
    zip_save = False
)