# Netclass Information Plugin

This KiCad plugin analyzes **netclasses** in your PCB and **generates custom DRC rules** based on each netclass's maximum trace length. It also provides an interface that lets you filter and view detailed information about your netclasses and their associated nets.

## Special thanks
This approach to manually modify (key 9) the length of a track and thus be able to define the same distance for all tracks of the same netclass, comes from the solution proposed by [JamesJ](https://forum.kicad.info/u/jamesj/summary) in the [Kicad forum discussion](https://forum.kicad.info/t/kiwi-length-matching-plugin-works-for-you/57268/7)

## Features

1. **Netclass Listing**: Displays each netclass and the nets that belong to it.  
2. **Net Length Calculation**: Computes the total length (in mm) of each net.  
3. **Filtering**: Allows you to display only those netclasses specified by the user.  
4. **DRC Rule Generation**: Creates `(rule ...)` blocks for KiCad, setting the detected maximum length as a constraint.  
5. **"ALL" Button**: Shows all netclasses without filtering.

## Installation Instructions

Copy `NetclassInfoPlugin.py` to the scripting/plugins path, in my case it would be in this path

C:\Users\Jairo\Documents\KiCad\8.0\scripting\plugins.

## Plugin Usage

1. Open your project in KiCad and go to the **PCB Editor**.
2. Navigate to `Tools > external plugins`, or to the plugins section (depending on your KiCad version).
3. Select **"Netclass Information"** from the list of available plugins (or from the contextual menu, if configured).
4. A window will appear containing:
   - A text field to **enter Netclass Names** (comma-separated).
   - A main text area showing the information.
   - Buttons: **Filter**, **ALL**, **Show DRC Rules**, and **Close**.

### Interface Details

- **Enter Netclass Names (comma-separated)**  
  Use this field to type the netclass names you want to filter, separated by commas. Example: `PWM, USBC, Vin`

- **Filter Button**  
  Displays information only for the netclasses you entered.  
  - You will see the list of nets associated with each netclass and their lengths.  
  - You will also see the **maximum length** detected for each netclass.

- **ALL Button**  
  Displays information for **all** netclasses detected in the PCB, without filtering.

- **Show DRC Rules Button**  
  Generates `(rule ...)` blocks with the maximum length for each netclass **currently shown** in the window.  
  - If you previously clicked Filter, only those filtered netclasses are included.  
  - If you clicked ALL, rules are generated for every netclass.

- **Close Button**  
  Closes the plugin window.

## Example of Generated Rules

When you click **Show DRC Rules**, you get something like:

```
(version 1)

(rule PWM_LENGTH (condition "A.NetClass=='PWM'") (constraint length (opt 18.673mm)) )

(rule DATA_LENGTH (condition "A.NetClass=='DATA'") (constraint length (opt 25.500mm)) )

; -- End of generated DRC rules --
```


You can **copy and paste** this block into your KiCad DRC configuration file or integrate it however you prefer.

## Final Notes

- You can modify the source code to change the `(constraint length (opt ...))` to `(max ...)` or other KiCad options.
- The plugin **does not** automatically overwrite or modify your `.kicad_drc` file; it only shows the text for you to use manually.
- The length accuracy depends on how KiCad sums track segments and their bending radii (if applicable).

---

Enjoy this plugin! Any feedback or improvements are welcome as *issues* or *pull requests*!
