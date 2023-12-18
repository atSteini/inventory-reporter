import sys
import pandas
import os
import glob

template_file = 'latex-templates/item_full.tex'
output_dir = '.out/inventory_list/items'
num_args = 4
id_col = 'ID'
to_replace = [('ITEM_NAME', 'Name'), ('ITEM_COUNT', 'Anzahl'),
              ('ITEM_DESCRIPTION', 'Beschreibung'), ('ITEM_ID', 'ID'),
              ('ITEM_PUR_DATE', 'Kaufdatum'), ('ITEM_PUR_PRICE', 'Kaufpreis einzeln'),
              ('ITEM_OWNER', 'Besitzer'), ('ITEM_PIC_NAME', 'ID')]

# arguments: path to excel, name of sheet, number of rows to read
def main():
  if (len(sys.argv) != (num_args + 1)):
     print("Incorrect number of variables given!")

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

  cleanFolder(output_dir)

  doWork(excel_sheet, to_replace, id_col)

  return 0

def doWork(df: pandas.DataFrame, replacements: [tuple], id_col: str):
  for i in df.index:
    #print(df['ID'][i], df['Kategorie'][i], '\t', df['Name'][i])
    data = []
    for (template, col) in replacements:
      data.append(tuple((template, str(df[col][i]))))

    copyAndModifyTemplate(template_file, os.path.join(output_dir, f'{df[id_col][i]}.tex'), data)

def copyAndModifyTemplate(template_file: str, out_filepath: str, data: [tuple]):
  template_content = ''
  with open(template_file, 'r') as template:
    template_content = template.read()

  item_content = template_content
  for (old, new) in data:
    item_content = item_content.replace(old, new)

  with open(out_filepath, 'w') as output_file:
    output_file.write(item_content)

def cleanFolder(dir):
  if (not os.path.exists(dir)):
    print("Output path does not exist. Making directory...")

    os.makedirs(dir)

    return

  print("Cleaning output directory...")

  files = glob.glob(f'{dir}/*')
  for f in files:
    os.remove(f)

if __name__ == "__main__":
    main()