# obsidian
Forget the days of old, manually placing and editing command blocks with their terrible UI. Now with mouse support, find and replace, lots of screen real estate and a nice looking UI: your text edior! obsidian is a tool that converts text files with a simple syntax into command block chains in-game, in a matter of cpu cycles (a couple billion of them).

# Usage
`python obsidian.py myWorld path/to/commands/file.cmds`

`myWorld` should be the name of the internal world folder in your `minecraftWorlds` directory. You can instead specify an entire path pointing to the world folder if it is not in the default location.

Note: obsidian produces a `.cmds.old` file alongside the specified `.cmds` file. This file lets it know what to remove before starting, such that if a command chain is shortened the previous blocks are not left behind. This file should be kept with the source `.cmds` file, although it is not crucial and will be created if it does not exist. When distributing a `.cmds` file to others, do not include the `.cmds.old` file, as that file represents the current state of your world, not theirs.

Note: bedrock (the library this uses to interface with minecraft worlds) requires a leveldb `.dll` or `.so` to be provided alongside it. No gurantees are given as to the state of the included files, so you may want to obtain them for yourself. See https://github.com/BluCodeGH/bedrock for more details.

# Syntax
The .cmds file format is a simple one, a text file. Inside this file you can specify one or more chains, which act like normal chains of commands do in-game. The first command block in a chain can be any type, and the following ones are all chain command blocks.

### Chain Header
The syntax for specifying the start of a chain looks like the following:
```
type x y z direction
```
`type` can be one of `I`, `C`, `R`.

`x`, `y` and `z` are integers.

`direction` can be one of `u`, `d`, `+x`, `-x`, `+z`, `-z`.

### Command 
After the start of a chain comes one or more commands, which should be indented by two spaces:
```
  [-][?][hover|]command
```
`-` specifies that the command needs redstone.

`?` specifies that the command is conditional. The order of `-` and `?` does not matter.

`hover` is the hover text, and can be empty (for example, when specifying a blank command block, as blank lines are ignored)

`command` is a minecraft command, and can also be empty (see above). Prefixing the command with `/` is optional and not recommended.

### Comments
Lines that, when stripped of whitespace, start with `#` are ignore. Lines containing only whitespace are also ignored.

# Example .cmds file
```
I 0 5 0 +x
  # Start with a needs redstone, impulse command block
  -this says hi|say hi
  # Followed by a conditional chain.
  ?say Said hi successfully.
  # And next comes an empty chain.
  |
  # Finishing with a needs redstone, conditional chain.
  ?-does nothing|

R 1 1 1 u
  # Always active repeating command block.
  chat spam|say chat spam
```
