import argparse
import os.path
import sys
import bedrock

parser = argparse.ArgumentParser(description="A CLI for importing text files of commands into Minecraft Bedrock Edition.")
parser.add_argument("world", help="Path to the world folder.")
parser.add_argument("fname", help="Path to the .cmds file to process.")
args = parser.parse_args()

if sys.platform == "win32":
  mcWorlds = os.path.expanduser("~") + "\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds"
else: # linux
  mcWorlds = os.path.expanduser("~") + "/Minecraft/minecraftWorlds"

if not os.path.isabs(args.world):
  args.world = os.path.join(mcWorlds, args.world)

with open(args.fname) as f:
  cmds = f.read()

try:
  with open(args.fname + ".old") as f:
    oldCmds = f.read()
except FileNotFoundError:
  oldCmds = ""

def nextPos(pos, d):
  index = {"u":1,"d":1,"+x":0,"-x":0,"+z":2,"-z":2}[d]
  direction = {"u":1,"d":-1,"+x":1,"-x":-1,"+z":1,"-z":-1}[d]
  pos[index] += direction

with bedrock.World(args.world) as world:
  for line in oldCmds.splitlines(): # Overwrite old command chains with air, to handle removing commands.
    if line.strip() == "" or line.strip()[0] == "#":
      continue
    if not line.startswith("  "): # Start of a new command chain
      _, x, y, z, d = line.split(" ")
      pos = [int(x), int(y), int(z)]
    else:
      world.setBlock(*pos, bedrock.Block("minecraft:air")) # Overwrite
      nextPos(pos, d)

  for line in cmds.splitlines():
    if line.strip() == "" or line.strip()[0] == "#":
      continue
    if not line.startswith("  "): # Start of a new command chain
      blockType, x, y, z, d = line.split(" ")
      pos = [int(x), int(y), int(z)]
    else: # Command
      line = line.strip()
      cond = line[0] == "?" or line[:2] == "-?" # commands can start with either - or ? first.
      redstone = line[0] == "-" or line[:2] == "?-"
      line = line.lstrip(" ?-")
      if "|" in line: # hover text and command seperator
        hover, command = line.split("|", 1)
      else:
        hover = ""
        command = line
      commandBlock = bedrock.CommandBlock(command, hover, blockType, d, cond, redstone)
      world.setBlock(*pos, commandBlock)
      blockType = "C"
      nextPos(pos, d)

with open(args.fname + ".old", "w") as f:
  f.write(cmds)

print("Done")
