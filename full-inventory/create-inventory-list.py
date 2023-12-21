import sys
import pandas
import os
import glob
import argparse

num_args = 5
tpl_item = 'latex-templates/tpl_item_full.tex'
tpl_inventory = 'latex-templates/tpl_inventory_full.tex'
inventory_out_name = 'inventory_full.tex'
forgig_out_name = 'inventory_forgig.tex'

output_dir = '.out/'
dir_items = 'items'
dir_list = 'main'

latex_cmd_subfile = ['\\subfile']
latex_cmd_change_marker = ['\\section']#, '\\chapter']

id_col = 'ID'
items_replacements = [
  ('ITEM_NAME', 'Name'), ('ITEM_COUNT', 'Anzahl'), ('ITEM_TYPE', 'Kategorie'),
  ('ITEM_DESCRIPTION', 'Beschreibung'), ('ITEM_ID', 'ID'),
  ('ITEM_PUR_DATE', 'Kaufdatum'), ('ITEM_PUR_PRICE', 'Kaufpreis einzeln'),
  ('ITEM_OWNER', 'Besitzer'), ('ITEM_PIC_NAME', 'ID')]

list_replacements_subfiles = [('ALL_SUBFILES', '{subfile_per_id}'), ('ALL_SUBFILES_WITH_CHANGE_MARKERS', '{subfile_per_id}')]

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
    sort_by = id_col
  if (sort_by_list[0] == id_col):
    include_change_markers = False

  print(f"Reading '{sheet_name}' from '{filepath}'...")

  if (num_rows > 0):
    excel_sheet = pandas.read_excel(filepath, sheet_name=sheet_name, nrows=num_rows)
  else:
    excel_sheet = pandas.read_excel(filepath, sheet_name=sheet_name)

  print(f'Sorting by {sort_by_list}...')
  excel_sheet = excel_sheet.sort_values(sort_by_list)

  # print(excel_sheet["Name"])

  sort_by = sort_by_list[0]

  # cleanFolder(os.path.join(output_dir, dir_items))
  create_all_templates(excel_sheet, tpl_item, items_replacements, id_col, os.path.join(output_dir, dir_items), len(str(num_rows)))
  
  # cleanFolder(os.path.join(output_dir, dir_list))
  merge_templates(tpl_inventory, os.path.join('..', dir_items), excel_sheet, id_col, os.path.join(output_dir, dir_list, inventory_out_name), include_change_markers, sort_by)

  print('Finished!')

  return 0

def merge_templates(list_template: str, full_items_dir: str, df: pandas.DataFrame, id_col: int, out_file: str, incl_markers: bool, sort_by: str):
  file_order = df[id_col]

  template_content = getFileContent(list_template)
  subfile_per_id = ''

  old_sort_by = atIdAndCol(df, file_order[0], sort_by)

  for id in file_order:
    sort_by_val = atIdAndCol(df, id, sort_by)

    if (old_sort_by != sort_by_val and incl_markers):
      for change_marker in latex_cmd_change_marker:
        subfile_per_id += f'{change_marker}{{{sort_by_val}}}\n'
      old_sort_by = sort_by_val

    for subfile_marker in latex_cmd_subfile:
      subfile_per_id += f'{subfile_marker}{{{full_items_dir}/{id}}}\n'

  (old, new) = list_replacements_subfiles[1 if incl_markers else 0]
  template_content = template_content.replace(old, new.format(subfile_per_id = subfile_per_id))

  writeToFile(out_file, template_content)

def create_all_templates(df: pandas.DataFrame, item_template: str, replacements: [tuple], id_col: str, out_dir: str, id_num_dig: int):
  print('Creating all templates...')

  for i in df.index:
    #print(df['ID'][i], df['Kategorie'][i], '\t', df['Name'][i])
    data = []
    for (template, col) in replacements:
      value = df[col][i]

      if (type(value) == pandas.Timestamp):
        value = timestamp_to_tex(value)
      
      if (col == id_col and template != 'ITEM_PIC_NAME'):
        value = str(value).zfill(id_num_dig)

      current_value = str(value)

      data.append(tuple((template, current_value)))

    copyAndModifyTemplate(item_template, os.path.join(out_dir, f'{df[id_col][i]}.tex'), data)

def copyAndModifyTemplate(item_template: str, out_filepath: str, data: [tuple]):
  template_content = getFileContent(item_template)

  item_content = template_content
  for (old, new) in data:
    item_content = item_content.replace(old, tex_escape(new).strip())

  writeToFile(out_filepath, item_content)

def cleanFolder(dir: str):
  if (not os.path.exists(dir)):
    print(f'{dir} does not exist. Making directory...')

    os.makedirs(dir)

    return

  print(f'Cleaning {dir}...')

  files = glob.glob(f'{dir}/*')
  for f in files:
    os.remove(f)

def writeToFile(file: str, content: str):
  with open(file, 'w') as output_file:
    output_file.write(content)

def getFileContent(file: str):
  file_content = None
  with open(file, 'r') as template:
    file_content = template.read()
  
  return file_content

def timestamp_to_tex(ts: pandas.Timestamp):
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

def atIdAndCol(df: pandas.DataFrame, id: int, col: str):
  return df.at[df[df[id_col] == id].index[0], col]

if __name__ == '__main__':
    main()