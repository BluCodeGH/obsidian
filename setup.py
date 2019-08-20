from setuptools import setup

setup(name="obsidian",
      version="0.1",
      description="Edit command block chains in a normal text editor and import them into Minecraft: Bedrock Edition.",
      keywords="minecraft bedrock commandblock",
      url="https://github.com/BluCodeGH/obsidian",
      packages=["obsidian"],
      install_requires=["bedrock"],
      dependency_links=["git+https://github.com/BluCodeGH/bedrock/tarball/master#egg=bedrock"],
      author="BluCode")
