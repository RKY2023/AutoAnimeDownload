from setuptools import find_packages, setup

with open("AutoAnimeDownloader/Readme.md", "r") as f:
  long_description = f.read()
  
setup(
  name="autoanimedownloader",
  version="0.0.01",
  description="To download anime automaticaly based on Aired",
  author="Rky",
  install_requires=["os >= 0.5.10"],
  # extra_require={"dev"": ["pytest >= 7.0"]}
  python_requires=">=3.10",
)
