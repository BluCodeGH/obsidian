import argparse
import os.path
import sys
import json
import bedrock

def nextPos(pos, d):
  index = {"u":1, "d":1, "+x":0, "-x":0, "+z":2, "-z":2}[d]
  direction = {"u":1, "d":-1, "+x":1, "-x":-1, "+z":1, "-z":-1}[d]
  pos[index] += direction

def prevPos(pos, d):
  index = {"u":1, "d":1, "+x":0, "-x":0, "+z":2, "-z":2}[d]
  direction = {"u":1, "d":-1, "+x":1, "-x":-1, "+z":1, "-z":-1}[d]
  pos[index] -= direction

def go(path, cmds, oldCmds):
  with bedrock.World(path) as world:
    for pos, d, length in oldCmds: # Remove old command chains
      for _ in range(length):
        world.setBlock(*pos, bedrock.Block("minecraft:air"))
        nextPos(pos, d)

    cmdsData = []
    pos = [None, None, None]
    d = None
    for i, line in enumerate(cmds.splitlines()):
      if line.strip() == "" or line.strip()[0] == "#":
        continue
      if not line.startswith("  ") and not line.startswith("\t"): # Start of a new command chain
        try:
          blockType, *newPos, d = line.split(" ")
        except ValueError:
          raise ValueError("Invalid header format on line {}".format(i))
        if pos[0] is not None:
          prevPos(pos, d)
        for j in range(3):
          if newPos[j][0] == "~":
            if len(newPos[j]) > 1:
              pos[j] += int(newPos[j][1:])
          else:
            pos[j] = int(newPos[j])
        cmdsData.append([pos[:], d, 0])
      else: # Command
        line = line.strip()
        cond = line[0] == "?" or line[:2] == "-?" # commands can start with either - or ? first.
        redstone = line[0] == "-" or line[:2] == "?-"
        if blockType == "R" and not redstone:
          redstone = True
          print("Warning: Always active on repeating command blocks not supported.")
        line = line.lstrip(" ?-")
        hover = ""
        time = 0
        first = False
        if line.count("|") == 2:
          time, hover, command = line.split("|", 2)
          first = "F" in time
          time = int(time.strip("F"))
        elif line.count("|") == 1:
          hover, command = line.split("|", 1)
        else:
          command = line
        commandBlock = bedrock.CommandBlock(command, hover, blockType, d, cond, redstone, time, first)
        world.setBlock(*pos, commandBlock)
        blockType = "C"
        nextPos(pos, d)
        cmdsData[-1][2] += 1
  return cmdsData

def main():
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

  with open(args.fname, encoding="utf-8") as f:
    cmds = f.read()

  try:
    with open(args.fname + ".old", encoding="utf-8") as f:
      oldCmds = json.load(f)
  except FileNotFoundError:
    oldCmds = []
  except json.decoder.JSONDecodeError:
    print("Warn: Could not decode {}. Acting like it does not exist.".format(args.fname + ".old"))
    oldCmds = []

  cmdsData = go(args.world, cmds, oldCmds)

  with open(args.fname + ".old", "w", encoding="utf-8") as f:
    json.dump(cmdsData, f)

if __name__ == '__main__':
  main()
