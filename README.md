# Inventory Reporter
Creates inventory lists from excel sheets.

## Usage
```make run``` runs all scripts with default options.

The ```.env``` file stores the paths to the excel file, image directory and what gig to generate a pdf for.

### Main Python script
```create-inventory-list.py``` is the main python file responsible for the latex file generation. It generates a ```.tex``` file for each item in a list of inventory items and one main file which includes these item files as subfiles. The make file calls this script and converts the resulting main ```.tex``` file to a pdf using ```pdflatex```.

The PDF formatting can be modified with the respective latex-templates:
* Full Inventory Main template: ```tpl_inventory_full.tex```
* Full Inventory template for each item: ```tpl_item_full.tex```
* Per Gig Inventory Main template: ```tpl_inventory_gig.tex```
* Per Gig Inventory for each item: ```tpl_item_gig.tex```

In the templates for each item, each column of the excel sheet can be used. To use values in the template, utilize the column name in upper cases and with '_' (underscore) instead of ' ' (space) surrounded by '€{}' as the placeholder. Ä,Ö,Ü will become ae, oe and ue in placeholders.

```€{KAUFPREIS_EINZELN} €``` would become ```58.00 €```

In addition to the column names in the item template, ```ID_LEADING_ZEROS``` can be used, which will have the ID of the item with leading zeros depending on the amount of items in the list.

In the main file, there are various placeholders which can be used. For example, ```€{TOC}``` can be used to create a table of contents if the option to include sections (```--write-sections```) was set to true.
The following placeholders can be used which will have different values depending on the logic behind them:

* ```ALL_SUBFILES``` - all subfiles.
* ```ALL_SUBFILES_WITH_CHANGE_MARKERS``` - all subfiles but with value of ```--sectioncmds``` before each file.
* ```IMG_PATH``` - static replacement with value of ```--imgpath```.
* ```TOC``` - display a table of contents if ```--writesection``` is ```1```.
* ```GIG_ITEM_COUNT``` - if ```--gigdatafrom``` is passed, this will be replaced by the number of times the item was taken on the gig.

### Globals.py
Also, Globally, there are certain constants which can be modified in the ```globals.py -> REPLACEMENTS_GLOBAL``` variable. Maybe I`ll add these globals as a cmd-line argument one day. Following constants can be used in all template files:

* ```AUTHOR```
* ```COPYRIGHT```

If the path to a file containing gig data as a json string is passed as ```--gigdatafrom```, the script will parse the json, save it as ```gig_data``` and use the value of ```gig_data['GIG_IDS']``` as a filter for the inventory list. This means that only the ids in this json (integer list seperated by ```;```) will be output. Also, all keys which are in the gig_data can be used as static substitutions in the main and item template files. If ```gig_data['GIG_IDS'][0] == -1```, the items will not be filtered, but the keys in ```gig_data``` can still be used as subtitutions.

### Gig Data
The data for a specific gig can be generated using the ```write-gig-list.py``` script. Run help of this script for information on its usage.