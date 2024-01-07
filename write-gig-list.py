import pandas
import argparse
import globals as gb
from collections import Counter
import json

CLI = argparse.ArgumentParser(
  prog="Gig List writer",
  description="Writes lists of ids for the last gig in a sheet of gigs"
)
CLI.add_argument(
  "-filepath",
  type=str,
  required=True
)
CLI.add_argument(
  "-gigsheet",
  type=str,
  required=True,
  help="Name of the sheet where gig log is stored"
)
CLI.add_argument(
  "-outpath",
  type=str,
  required=True
)
CLI.add_argument(
  "-gearcol",
  type=str,
  required=True,
  help="Name of col where the ids for the inventory are stored in gigsheet"
)
CLI.add_argument(
  "-invsheet",
  type=str,
  default=None,
  required=True,
  help="Name of sheet where named gear lists are stored"
)
CLI.add_argument(
  "--namedgearcols",
  nargs=2,
  type=str,
  default=gb.DEFAULT_GEAR_NAME_KV,
  help="Name of the two columns representing key and value pair for name gear lists"
)
CLI.add_argument(
  "--forrow",
  type=int,
  default=-1
)
CLI.add_argument(
  "--forid",
  type=int,
  default=-1
)
CLI.add_argument(
  "--idcol",
  type=str,
  default=gb.ID_COL
)

def main():
  args = CLI.parse_args()
  print("Parsed arguments: ", args)

  file_path = args.filepath
  gig_sheet = args.gigsheet
  gear_col = args.gearcol
  named_gear_sheet = args.invsheet
  for_row = args.forrow
  for_id = args.forid
  id_col = args.idcol
  named_gear_kv = args.namedgearcols
  out_path = args.outpath

  print(f"Reading '{gig_sheet}' from '{file_path}'...")

  if (for_row == -1):
    gig_log = pandas.read_excel(file_path, sheet_name=gig_sheet)
  else:
    gig_log = pandas.read_excel(file_path, sheet_name=gig_sheet, nrows=for_row)

  print(f"Reading '{named_gear_sheet}' from '{file_path}'...")
  named_gear = pandas.read_excel(file_path, sheet_name=named_gear_sheet)

  gig = gig_log.iloc[-1:]

  if (for_id == -1):
    gig = gig_log.iloc[for_row:]
  else:
    gig = gb.atId(gig_log, id_col, for_id)

  if (gig.empty):
    print("Gig not found or is empty! Exiting...")
    return -1

  gig_data = {}

  gig_data['ids'] = getAllIds(
    single_gig=gig, 
    nd_gear_sheet=named_gear, 
    gear_col=gear_col,
    nd_name_col=named_gear_kv[0],
    nd_val_col=named_gear_kv[1]
  )

  gig_data['unique_ids'] = dict(Counter(gig_data['ids']))

  gig_data.update(gb.getMapping(gig))

  print(f"Writing gig data to {out_path}...")

  writeDataToFile(out_path, gig_data)

  print("Finished writing data!")

def writeDataToFile(file: str, data: dict):
  data_repl_keys = {}

  for key in data:
    value = data[key]

    if (type(value) == list):
      data[key] = gb.ARR_SEP.join(str(element) for element in value)

    data_repl_keys['GIG_'+str(key).upper()] = data[key]

  gb.writeToFile(file, json.dumps(data_repl_keys))

def getAllIds(single_gig: pandas.DataFrame, nd_gear_sheet: pandas.DataFrame, gear_col: str, nd_name_col: str, nd_val_col: str) -> [int]:
  content = str(single_gig.iloc[0][gear_col])

  tokens = content.split(gb.ARR_SEP)

  ids = []
  for token in tokens:
    token = token.strip()

    if (token.isnumeric()):
      ids.append(int(token))
      continue
    
    named_ids = getIdsOfNamedGear(nd_gear_sheet, token, nd_name_col, nd_val_col)
    
    if (named_ids == None):
      print(f"Could not find ids for '{token}' in '{nd_gear_sheet}'! Skipping...")
      continue
    
    ids += named_ids.split(gb.ARR_SEP)

  return ids

def getIdsOfNamedGear(df: pandas.DataFrame, gear_name: str, name_col: str, value_col: str) -> str:
  ids = (df.loc[df[name_col] == gear_name][value_col])

  if (ids.empty):
    return None

  return str(ids.iloc[0])

if __name__ == '__main__':
    main()