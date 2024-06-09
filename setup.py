from setuptools import setup

with open("README", "r") as f:
    long_description = f.read()

setup(
    name="bonk_bot",
    version="1.0.0",
    description="Python API wrapper for bonk.io web game.",
    license="MIT",
    long_description=long_description,
    author="Safizapi",
    packages=[
        "python-engineio",
        "python-socketio",
        "aiohttp",
        "requests",
        "nest-asyncio",
        "pymitter"
    ]
)
