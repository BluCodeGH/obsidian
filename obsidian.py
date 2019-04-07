import argparse
import os.path
import sys
import json
import bedrock

if sys.platform == "win32":
  mcWorlds = os.path.expanduser("~") + "\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds"
else: # linux
  mcWorlds = os.path.expanduser("~") + "/Minecraft/minecraftWorlds"

def nextPos(pos, d):
  index = {"u":1, "d":1, "+x":0, "-x":0, "+z":2, "-z":2}[d]
  direction = {"u":1, "d":-1, "+x":1, "-x":-1, "+z":1, "-z":-1}[d]
  pos[index] += direction

def prevPos(pos, d):
  index = {"u":1, "d":1, "+x":0, "-x":0, "+z":2, "-z":2}[d]
  direction = {"u":1, "d":-1, "+x":1, "-x":-1, "+z":1, "-z":-1}[d]
  pos[index] -= direction

def go(worldPath, cmds, oldCmds):
  with bedrock.World(worldPath) as world:
    for pos, d, length in oldCmds: # Remove old command chains
      for _ in range(length):
        world.setBlock(*pos, bedrock.Block("minecraft:air"))
        nextPos(pos, d)

    cmdsData = []
    pos = []
    d = None
    for i, line in enumerate(cmds.splitlines()):
      if line.strip() == "" or line.strip()[0] == "#":
        continue
      if not line.startswith("  ") and not line.startswith("\t"): # Start of a new command chain
        if pos:
          prevPos(pos, d)
        try:
          blockType, x, y, z, d = line.split(" ")
        except ValueError:
          raise ValueError("Invalid header format on line {}".format(i))

        if x[0] == "~":
          if len(x) > 1:
            x = pos[0] + int(x[1:])
          else:
            x = pos[0]
        if y[0] == "~":
          if len(y) > 1:
            y = pos[1] + int(y[1:])
          else:
            y = pos[1]
        if z[0] == "~":
          if len(z) > 1:
            z = pos[2] + int(z[1:])
          else:
            z = pos[2]
        pos = [int(x), int(y), int(z)]
        cmdsData.append([pos[:], d, 0])
      else: # Command
        line = line.strip()
        cond = line[0] == "?" or line[:2] == "-?" # commands can start with either - or ? first.
        redstone = line[0] == "-" or line[:2] == "?-"
        if blockType == "R" and not redstone:
          redstone = True
          print("Warning: Always active on repeating command blocks not supported.")
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
        cmdsData[-1][2] += 1

  return cmdsData

def main(worldPath, file):
  if not os.path.isabs(worldPath):
    worldPath = os.path.join(mcWorlds, worldPath)

  with open(file, encoding="utf-8") as f:
    cmds = f.read()
  try:
    with open(file + ".old", encoding="utf-8") as f:
      oldCmds = json.load(f)
  except FileNotFoundError:
    oldCmds = []
  except json.decoder.JSONDecodeError:
    print("Warn: Could not decode {}. Acting like it does not exist.".format(file + ".old"))
    oldCmds = []

  cmdsData = go(worldPath, cmds, oldCmds)

  with open(file + ".old", "w", encoding="utf-8") as f:
    json.dump(cmdsData, f)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="A CLI for importing text files of commands into Minecraft Bedrock Edition.")
  parser.add_argument("world", help="Path to the world folder.")
  parser.add_argument("fname", help="Path to the .cmds file to process.")
  args = parser.parse_args()
  main(args.world, args.fname)
