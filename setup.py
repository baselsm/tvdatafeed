from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tvdatafeed",
    version="1.0.4",
    packages=["tvDatafeed"],
    url="https://www.youtube.com/watch?v=qDrXmb2ZRjo",
    license="MIT License",
    author="@StreamAlpha",
    author_email="",
    description="TradingView historical data downloader",
    long_description_content_type="text/markdown",
    long_description=long_description,
)
