import sys
import pandas
import os
import glob

num_args = 4
tpl_item = 'latex-templates/tpl_item_full.tex'
tpl_inventory = 'latex-templates/tpl_inventory_full.tex'
inventory_out_name = 'inventory_full.tex'

output_dir = '.out/'
dir_items = 'items'
dir_list = 'main'

id_col = 'ID'
items_replacements = [
  ('ITEM_NAME', 'Name'), ('ITEM_COUNT', 'Anzahl'), ('ITEM_TYPE', 'Kategorie'),
  ('ITEM_DESCRIPTION', 'Beschreibung'), ('ITEM_ID', 'ID'),
  ('ITEM_PUR_DATE', 'Kaufdatum'), ('ITEM_PUR_PRICE', 'Kaufpreis einzeln'),
  ('ITEM_OWNER', 'Besitzer'), ('ITEM_PIC_NAME', 'ID')]

list_replacements_subfiles = ('ALL_SUBFILES', '{subfile_per_id}')

# arguments: path to excel, name of sheet, number of rows to read
def main():
  if (len(sys.argv) != (num_args + 1)):
     print('Incorrect number of variables given!')

     return

  filepath = sys.argv[1]
  sheet_name = sys.argv[2]
  num_rows = int(sys.argv[3])
  sort_by = sys.argv[4]

  print(f"Reading '{sheet_name}' from '{filepath}'...")

  excel_sheet = pandas.read_excel(filepath, sheet_name=sheet_name, nrows=num_rows)
  # print(excel_sheet)
  
  if (sort_by != 'None'):
    print(f'Sorting by {sort_by}...')
    excel_sheet = excel_sheet.sort_values(sort_by)

  # cleanFolder(os.path.join(output_dir, dir_items))
  create_all_templates(excel_sheet, tpl_item, items_replacements, id_col, os.path.join(output_dir, dir_items))
  
  # cleanFolder(os.path.join(output_dir, dir_list))
  merge_templates(tpl_inventory, os.path.join('..', dir_items), excel_sheet, id_col, os.path.join(output_dir, dir_list, inventory_out_name))

  print('Finished!')

  return 0

def merge_templates(list_template: str, full_items_dir: str, df_sorted: pandas.DataFrame, id_col: int, out_file: str):
  file_order = df_sorted[id_col]

  template_content = getFileContent(list_template)
  subfile_per_id = ''

  for id in file_order:
    subfile_per_id += f'\\subfile{{{full_items_dir}/{id}}}\n'

  (old, new) = list_replacements_subfiles
  template_content = template_content.replace(old, new.format(subfile_per_id = subfile_per_id))

  writeToFile(out_file, template_content)

def create_all_templates(df: pandas.DataFrame, item_template: str, replacements: [tuple], id_col: str, out_dir: str):
  print('Creating all templates...')

  for i in df.index:
    #print(df['ID'][i], df['Kategorie'][i], '\t', df['Name'][i])
    data = []
    for (template, col) in replacements:
      current_value = str(df[col][i]).replace(' 00:00:00', '')

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

if __name__ == '__main__':
    main()