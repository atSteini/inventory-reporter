import pandas
import os
import argparse
from string import Template
import globals as gb
import json

# TODO: Write Anzahl von items when gig list contains id multiple times

TPL_FULL_ITEM = 'latex-templates/tpl_item_full.tex'
TPL_FULL_MAIN = 'latex-templates/tpl_inventory_full.tex'
OUT_NAME_FULL = 'inventory_full.tex'
OUT_NAME_ITEMS = '${ID}.tex'
OUT_NAME_FORGIG = 'inventory_forgig.tex'

OUT_DIR = '.out/full'
DIR_ITEMS_FULL = 'items'
DIR_MAIN_FULL = 'main'
DIR_ITEMS_FORGIG = 'forgig/items'
DIR_MAIN_FORGIG = 'forgig/main'

LATEXT_CMDS_SUBFILE = ['\\subfile{${SUBFILE}/${ID}}']
LATEX_CMDS_CHANGE = ['\\section{${KATEGORIE}}']#, '\\chapter']
LATEX_CMDS_AFTER_N_ITEMS = {'cmds': ['\\pagebreak'], 'after_n_insection': 2, 'after_n_total': 10}

CLI=argparse.ArgumentParser(
  prog="Inventory List maker",
  description="Generates list of inventory items and writes to pdf using latex templates"
)
CLI.add_argument(
  "-filepath",
  type=str,
  default='',
  required=True
)
CLI.add_argument(
  "-sheet",
  type=str,
  default='',
  required=True
)
CLI.add_argument(
  "--tplitem",
  type=str,
  default=TPL_FULL_ITEM
)
CLI.add_argument(
  "--tplmain",
  type=str,
  default=TPL_FULL_MAIN
)
CLI.add_argument(
  "--outpath",
  type=str,
  default=OUT_DIR
)
CLI.add_argument(
  "--outitems",
  type=str,
  default=DIR_ITEMS_FULL
)
CLI.add_argument(
  "--outmain",
  type=str,
  default=DIR_MAIN_FULL
)
CLI.add_argument(
  "--namemain",
  type=str,
  default=OUT_NAME_FULL
)
CLI.add_argument(
  "--nameitems",
  type=str,
  default=OUT_NAME_ITEMS
)
CLI.add_argument(
  "--imgpath",
  type=str,
  default="../../../img"
)
CLI.add_argument(
  "--idcol",
  type=str,
  default=gb.ID_COL
)
CLI.add_argument(
  "--nrows",
  type=int,
  default=0
)
CLI.add_argument(
  "--sorts",
  nargs="*",
  type=str,
  default=["Kategorie", "Name"]
)
CLI.add_argument(
  "--braftersection",
  type=int,
  default=LATEX_CMDS_AFTER_N_ITEMS['after_n_insection']
)
CLI.add_argument(
  "--braftertotal",
  type=int,
  default=LATEX_CMDS_AFTER_N_ITEMS['after_n_total']
)
CLI.add_argument(
  "--sectioncmds",
  nargs="*",
  type=str,
  default=LATEX_CMDS_CHANGE
)
CLI.add_argument(
  "--gigdatafrom",
  type=str,
  default=None
)
CLI.add_argument(
  "--onlyids",
  nargs="*",
  type=int,
  default=[-1]
)
CLI.add_argument(
  "--writesections",
  type=int,
  default=1,
  choices=[0, 1]
)
CLI.add_argument(
  "--ndidcol",
  type=str,
  default='GIG_'+gb.DEFAULT_GEAR_NAME_KV[1].upper()
)

def main():
  args = CLI.parse_args()
  print("Parsed arguments: ", args)

  filepath = args.filepath  # sys.argv[1]
  sheet_name = args.sheet  # sys.argv[2]
  num_rows = args.nrows  # int(sys.argv[3])
  sort_by_list = args.sorts  # sys.argv[4]
  include_change_markers = bool(args.writesections)  # bool(sys.argv[5])
  tpl_main = args.tplmain
  tpl_item = args.tplitem
  out_dir_main = args.outmain
  out_dir_items = args.outitems
  img_path = args.imgpath
  id_col = args.idcol
  name_main = args.namemain
  name_items = args.nameitems
  break_after_insection = args.braftersection
  break_after_total = args.braftertotal
  section_change = args.sectioncmds
  out_path = args.outpath
  only_ids = args.onlyids
  get_gig_data_from = args.gigdatafrom
  named_gear_id_col = args.ndidcol

  latex_after_n = LATEX_CMDS_AFTER_N_ITEMS
  latex_after_n['after_n_insection'] = break_after_insection
  latex_after_n['after_n_total'] = break_after_total

  if (sort_by_list[0] == 'None'):
    sort_by = gb.ID_COL
  if (sort_by_list[0] == gb.ID_COL):
    include_change_markers = False

  print(f"Reading '{sheet_name}' from '{filepath}'...")

  if (num_rows > 0):
    excel_sheet = pandas.read_excel(filepath, sheet_name=sheet_name, nrows=num_rows)
  else:
    excel_sheet = pandas.read_excel(filepath, sheet_name=sheet_name)

  print(f'Sorting data by {sort_by_list}...')
  excel_sheet = excel_sheet.sort_values(sort_by_list)

  if (get_gig_data_from != None):
    print(f'Loading gig data from {get_gig_data_from}...')

    gig_data = getGigDataFromFile(get_gig_data_from, named_gear_id_col)
    gb.GLOBAL_CONSTANTS.update(gig_data)

    only_ids = gig_data[named_gear_id_col]
    only_ids_unique = list(set(only_ids))

  if (only_ids[0] != -1):
    print("Filtering data by ids...")
    excel_sheet = excel_sheet.loc[excel_sheet[id_col].isin(only_ids_unique)]
    excel_sheet = addGigCount(excel_sheet, gig_data['GIG_UNIQUE_IDS'])

  sort_by = sort_by_list[0]

  substitutions = {
    'TOC_IF_MARKERS': r'\tableofcontents' if include_change_markers else '',
    'ITEM_COUNT_TOTAL': len(excel_sheet.index) if only_ids[0] == -1 else len(only_ids) 
  }

  print(countItemsInSections(excel_sheet, sort_by))

  createTemplates(
    df=excel_sheet, 
    item_template=tpl_item, 
    item_name=name_items, 
    out_dir=os.path.join(out_path, out_dir_items), 
    id_col=id_col)

  main_sub_content = getSubstituteContentMain(
    df=excel_sheet, 
    path_to_item_from_main=os.path.join("..", out_dir_items), 
    id_col=id_col,
    incl_markers=include_change_markers, 
    sort_by=sort_by, 
    latex_after_n=latex_after_n, 
    latex_section_cmds=section_change)

  mergeTemplates(
    out_file=os.path.join(out_path, out_dir_main, name_main), 
    template_content=gb.getFileContent(tpl_main, True), 
    sub_content=main_sub_content, 
    img_path=img_path,
    sub_additions=substitutions
  )

  print('Finished!')

  return 0

def getSubstituteContentMain(df: pandas.DataFrame, path_to_item_from_main: str, id_col: int, incl_markers: bool, sort_by: str, latex_after_n: dict, latex_section_cmds: [str]):
  file_order = df[id_col]

  latex_subfile_cmd = ''
  item_counter_total = 0            # total number of items
  item_counter_insection = 0        # number of items in current section, gets reset if new section starts
  item_counter_before_break = 0     # number of items before break, gets reset if new page starts
  item_counter = 0                  # number of items in current section if after_n_insection > 0, else number of items on current page
  next_section_num_items = -1       # number of items in next section
  old_sort_by = gb.atIdAndCol(df, id_col, file_order.iloc[0], sort_by)
  is_first_sort_check = True

  after_n_value = latex_after_n['after_n_insection'] if (incl_markers and latex_after_n['after_n_insection'] > 0) else latex_after_n['after_n_total']
  until_section_change = -1
  overrideBreak = False
  broke_in_middle_of_section = False

  for i, id in enumerate(file_order):
    sort_by_val = gb.atIdAndCol(df, id_col, id, sort_by)

    substitutions = gb.getMappingForRow(df, id, id_col)
    substitutions.update({'SORT_BY': sort_by_val, 'SUBFILE': path_to_item_from_main})

    item_counter_before_break += 1
    until_section_change = countUntilNextSectionChange(df, id_col, sort_by, i)

    if (until_section_change == 0):
      next_section_num_items = countUntilNextSectionChange(df, id_col, sort_by, i + 1) + 1
      if (next_section_num_items >= 0 and item_counter_before_break + (next_section_num_items + gb.SECTION_WEIGHT) > after_n_value):
        overrideBreak = True and not broke_in_middle_of_section
        next_section_num_items = -1

    if ((is_first_sort_check and incl_markers) or (old_sort_by != sort_by_val and incl_markers)):
      # mark new section
      is_first_sort_check = False
      old_sort_by = sort_by_val
      
      item_counter_insection = 0

      item_counter_before_break += gb.SECTION_WEIGHT
      for section_cmd in latex_section_cmds:
        latex_subfile_cmd += gb.substituteGlobal(Template(section_cmd), substitutions) + '\n'

    for subfile_cmd in LATEXT_CMDS_SUBFILE:
      latex_subfile_cmd += gb.substituteGlobal(Template(subfile_cmd), substitutions) + '\n'

    item_counter_total += 1
    item_counter_insection += 1
    item_counter = item_counter_insection if (latex_after_n['after_n_insection'] > 0) else item_counter_before_break
    break_because_aftern = (after_n_value > 0 and item_counter != 0 and item_counter % after_n_value == 0)

    if (break_because_aftern or overrideBreak):
      latex_subfile_cmd += '\n'.join(latex_after_n['cmds']) + '\n'
      item_counter_before_break = 0
      overrideBreak = False
      broke_in_middle_of_section = until_section_change > 0
  
  return latex_subfile_cmd

def countItemsInSections(df: pandas.DataFrame, sort_by: str) -> dict:
  ret_dict = {}
  all_sort_by_values = set(df[sort_by])
  for sort_by_val in all_sort_by_values:
    num_items = len(df[df[sort_by] == sort_by_val])
    ret_dict[sort_by_val] = num_items
  return ret_dict

def countUntilNextSectionChange(df: pandas.DataFrame, id_col: str, sort_by: str, start_index: int):
  if (start_index >= len(df.index) or df.size == 0):
    return 0
  
  if (start_index == len(df.index) - 1):
    return 1

  old_sort_by = gb.atIdAndCol(df, id_col, df.index[start_index], sort_by)
  num_items_until_unequal = 0

  for i, id in enumerate(df.index):
    if (i <= start_index):
      continue
    
    sort_by_val = gb.atIdAndCol(df, id_col, id, sort_by)

    if (old_sort_by != sort_by_val):
      break

    num_items_until_unequal += 1

  return num_items_until_unequal

def mergeTemplates(out_file: str, template_content: str, sub_content: str, img_path: str, sub_additions: dict):
  print("Merging templates...")

  subs = {
    'SUBFILE_CMD': sub_content, 
    'SECTION_MAKER_AND_SUBFILE_CMD': sub_content, 
    'IMG_PATH': img_path
  }
  subs.update(sub_additions)

  mapping = gb.getGlobalMappingBy(subs)
  template_content = gb.substituteGlobal(Template(template_content), mapping)

  gb.writeToFile(out_file, template_content)

def createTemplates(df: pandas.DataFrame, item_template: str, item_name: str, out_dir: str, id_col: str):
  print('Creating all templates...')

  for i in df.index:
    row_mapping = gb.getMappingForRow(df, i, id_col)

    file_name = gb.substituteGlobal(Template(item_name), {id_col: gb.atIdAndCol(df, id_col, i, id_col)})
    # copyAndModifyTemplate(item_template, os.path.join(out_dir, f'{df[id_col][i]}.tex'), row_mapping)
    copyAndModifyTemplate(item_template, os.path.join(out_dir, file_name), row_mapping)

def copyAndModifyTemplate(tpl_file: str, out_path: str, row_mapping: {}):
  template_content = gb.getFileContent(tpl_file, True)

  item_content = gb.substituteGlobal(Template(template_content),row_mapping)

  gb.writeToFile(out_path, item_content)

def addGigCount(df: pandas.DataFrame, lookup: dict) -> pandas.DataFrame:
  df_new = df
  values = []

  for i in df_new.index:
    values.append(lookup[str(i)])

  df_new.insert(5, 'GIG_ITEM_COUNT', values, True)

  return df_new

### Helper functions...
def getGigDataFromFile(file: str, nd_id_col: str) -> dict:
  data = ''

  with open(file, 'r') as f:
    data = f.read()

  js_data = json.loads(data.replace("'", '"'))
  ids_str_list = [int(x) for x in str(js_data[nd_id_col]).split(gb.ARR_SEP) if x != '']
  js_data[nd_id_col] = ids_str_list
  
  return js_data

if __name__ == '__main__':
    main()