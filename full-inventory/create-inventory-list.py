import sys
import pandas
import os
import glob
import argparse
from string import Template
from pandas.api.types import is_float_dtype

TPL_FULL_ITEM = 'latex-templates/tpl_item_full.tex'
TPL_FULL_MAIN = 'latex-templates/tpl_inventory_full.tex'
OUT_NAME_FULL = 'inventory_full.tex'
OUT_NAME_FORGIG = 'inventory_forgig.tex'

OUT_DIR = '.out/'
DIR_ITEMS_FULL = 'full/items'
DIR_MAIN_FULL = 'full/main'
DIR_ITEMS_FORGIG = 'forgig/items'
DIR_MAIN_FORGIG = 'forgig/main'

LATEXT_CMDS_SUBFILE = ['\\subfile{${SUBFILE}/${ID}}']
LATEX_CMDS_CHANGE = ['\\pagebreak', '\\section{${SORT_BY}}']#, '\\chapter']
LATEX_CMDS_AFTER_N_ITEMS = {'cmds': ['\\pagebreak'], 'after_n': 2}

ID_COL = 'ID'

REPLACEMENTS_GLOBAL = {
  'ALL_SUBFILES': '${SUBFILE_CMD}',
  'ALL_SUBFILES_WITH_CHANGE_MARKERS': '${SECTION_MAKER_AND_SUBFILE_CMD}'
}

GLOBAL_CONSTANTS = {
  'AUTHOR': 'Florian Steinkellner'
}

SUB_IDENTIFIER = ('€{', '${')

CLI = argparse.ArgumentParser()
CLI.add_argument(
  "-filepath",
  type=str,
  default=''
)
CLI.add_argument(
  "-sheet",
  type=str,
  default=''
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
  "--inclmarkers",
  type=bool,
  default=True
)

def main():
  args = CLI.parse_args()
  # print("Parsed arguments: ", args)

  filepath = args.filepath  # sys.argv[1]
  sheet_name = args.sheet  # sys.argv[2]
  num_rows = args.nrows  # int(sys.argv[3])
  sort_by_list = args.sorts  # sys.argv[4]
  include_change_markers = args.inclmarkers  # bool(sys.argv[5])

  if (sort_by_list[0] == 'None'):
    sort_by = ID_COL
  if (sort_by_list[0] == ID_COL):
    include_change_markers = False

  print(f"Reading '{sheet_name}' from '{filepath}'...")

  if (num_rows > 0):
    excel_sheet = pandas.read_excel(filepath, sheet_name=sheet_name, nrows=num_rows)
  else:
    excel_sheet = pandas.read_excel(filepath, sheet_name=sheet_name)

  print(f'Sorting by {sort_by_list}...')
  excel_sheet = excel_sheet.sort_values(sort_by_list)

  sort_by = sort_by_list[0]

  create_templates(excel_sheet, TPL_FULL_ITEM, os.path.join(OUT_DIR, DIR_ITEMS_FULL))
  
  merge_templates(TPL_FULL_MAIN, os.path.join('../..', DIR_ITEMS_FULL), excel_sheet, ID_COL, os.path.join(OUT_DIR, DIR_MAIN_FULL, OUT_NAME_FULL), include_change_markers, sort_by)

  print('Finished!')

  return 0

def merge_templates(tpl_list: str, full_items_dir: str, df: pandas.DataFrame, id_col: int, out_file: str, incl_markers: bool, sort_by: str):
  file_order = df[id_col]

  template_content = getFileContent(tpl_list, True)
  latex_subfile_cmd = ''

  num_items = 0
  old_sort_by = atIdAndCol(df, file_order[0], sort_by)
  for id in file_order:
    sort_by_val = atIdAndCol(df, id, sort_by)

    if (old_sort_by != sort_by_val and incl_markers):
      for change_marker in LATEX_CMDS_CHANGE:
        latex_subfile_cmd += substituteGlobal(Template(change_marker), {'SORT_BY': sort_by_val}) + '\n'
      old_sort_by = sort_by_val

    for subfile_marker in LATEXT_CMDS_SUBFILE:
      latex_subfile_cmd += substituteGlobal(Template(subfile_marker), {'SUBFILE': full_items_dir, 'ID': id}) + '\n'
    
    if (num_items != 0 and num_items % LATEX_CMDS_AFTER_N_ITEMS['after_n'] == 0):
      latex_subfile_cmd += '\n'.join(LATEX_CMDS_AFTER_N_ITEMS['cmds']) + '\n'

    num_items += 1

  mapping = getGlobalMappingBy({'SUBFILE_CMD': latex_subfile_cmd, 'SECTION_MAKER_AND_SUBFILE_CMD': latex_subfile_cmd})
  template_content = substituteGlobal(Template(template_content), mapping)

  writeToFile(out_file, template_content)

def create_templates(df: pandas.DataFrame, item_template: str, out_dir: str):
  print('Creating all templates...')

  for i in df.index:
    row_mapping = getMappingForRow(df, i)

    copyAndModifyTemplate(item_template, os.path.join(out_dir, f'{df[ID_COL][i]}.tex'), row_mapping)

def copyAndModifyTemplate(tpl_file: str, out_path: str, row_mapping: {}):
  template_content = getFileContent(tpl_file, True)

  item_content = substituteGlobal(Template(template_content),row_mapping)

  writeToFile(out_path, item_content)

### Helper functions...
def substituteGlobal(tpl: Template, mapping: dict):
  mapping_with_global = mapping
  mapping_with_global.update(GLOBAL_CONSTANTS)

  return tpl.safe_substitute(mapping_with_global)

def getGlobalMappingBy(sub_dict: dict):
  ret_dict = {}

  for key in REPLACEMENTS_GLOBAL:
    value = REPLACEMENTS_GLOBAL[key]

    ret_dict[key] = substituteGlobal(Template(value), sub_dict)

  return ret_dict

def writeToFile(file: str, content: str):
  with open(file, 'w') as output_file:
    output_file.write(content)

def getFileContent(file: str, sub_from_latex: bool):
  file_content = None

  with open(file, 'r') as template:
    file_content = template.read()
  
  if (sub_from_latex):
    file_content = file_content.replace(SUB_IDENTIFIER[0], SUB_IDENTIFIER[1])
  
  return file_content

def timestamp_to_tex(ts: pandas.Timestamp) -> str:
  return ts.to_pydatetime().strftime('%m.%d.%Y')

def tex_escape(text: str):
    translation_table = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
        'ä': r'\"a',
        'ö': r'\"o',
        'Ä': r'\"A',
        'Ö': r'\"O',
        'ü': r'\"u',
        'Ü': r'\"U',
    }

    return text.translate(str.maketrans(translation_table))

def getMappingForRow(df: pandas.DataFrame, item_id: int) -> {}:
  ret_dict = {}
  num_rows = len(df.index)

  for column in df.columns:
    value = atIdAndCol(df, item_id, column)

    if (type(value) == pandas.Timestamp):
      value = value.strftime('%d.%m.%Y')
    elif (is_float_dtype(value)):
      value = f"{value:.2f}"

    if (column == ID_COL):
      ret_dict['ID_LEADING_ZEROES'] = str(value).zfill(len(str(num_rows)))

    ret_dict[column.replace(' ', '_').upper()] = tex_escape(str(value))

  return ret_dict

def atIdAndCol(df: pandas.DataFrame, id: int, col: str):
  return df.at[df[df[ID_COL] == id].index[0], col]

if __name__ == '__main__':
    main()