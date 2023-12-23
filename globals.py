import pandas
from pandas.api.types import is_float_dtype
from string import Template

ID_COL = 'ID'

ARR_SEP = ";"

REPLACEMENTS_GLOBAL = {
  'ALL_SUBFILES': '${SUBFILE_CMD}',
  'ALL_SUBFILES_WITH_CHANGE_MARKERS': '${SECTION_MAKER_AND_SUBFILE_CMD}',
  'IMG_PATH': '${IMG_PATH}',
  'TOC': '${TOC_IF_MARKERS}'
}

GLOBAL_CONSTANTS = {
  'AUTHOR': 'Florian Steinkellner',
  'COPYRIGHT': r'\copyright  Florian Steinkellner'
}

DEFAULT_GEAR_NAME_KV = ['Name', 'IDs']

SUB_IDENTIFIER = ('€{', '${')

def getMapping(row: pandas.DataFrame) -> dict:
  ret_dict = {}
  first = row.iloc[0]

  for column in row.columns:
    value = first[column]

    if (type(value) == pandas.Timestamp):
      value = value.strftime('%d.%m.%Y')
    elif (is_float_dtype(value)):
      value = f"{value:.2f}"

    ret_dict[key_escape(column.replace(' ', '_').upper())] = tex_escape(str(value))

  return ret_dict

def getMappingForRow(df: pandas.DataFrame, item_id: int, id_col: str) -> dict:
  num_rows = len(df.index)
  row = atId(df, id_col, item_id)

  mapping = getMapping(row)
  mapping['ID_LEADING_ZEROES'] = mapping[id_col].zfill(len(str(num_rows)))

  return mapping

def atIdAndCol(df: pandas.DataFrame, id_col: str, id: int, col: str):
  return df.at[atId(df, id_col, id).index[0], col]

def atId(df: pandas.DataFrame, id_col: str, id: int):
  return df[df[id_col] == id]

def tex_escape(text: str) -> str:
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

def key_escape(text: str) -> str:
  translation_table = {
    'ä': 'ae',
    'Ä': 'AE',
    'ö': 'oe',
    'Ö': 'OE',
    'ü': 'ue',
    'Ü': 'UE'
  } 
  return text.translate(str.maketrans(translation_table))

def timestamp_to_tex(ts: pandas.Timestamp) -> str:
  return ts.to_pydatetime().strftime('%m.%d.%Y')

def writeToFile(file: str, content: str):
  with open(file, 'w') as output_file:
    output_file.write(content)

def getFileContent(file: str, sub_from_latex: bool) -> str:
  file_content = None

  with open(file, 'r') as template:
    file_content = template.read()
  
  if (sub_from_latex):
    file_content = file_content.replace(SUB_IDENTIFIER[0], SUB_IDENTIFIER[1])
  
  return file_content

def substituteGlobal(tpl: Template, mapping: dict) -> str:
  mapping_with_global = mapping
  mapping_with_global.update(GLOBAL_CONSTANTS)

  return tpl.safe_substitute(mapping_with_global)

def getGlobalMappingBy(sub_dict: dict) -> dict:
  ret_dict = {}

  for key in REPLACEMENTS_GLOBAL:
    value = REPLACEMENTS_GLOBAL[key]

    ret_dict[key] = substituteGlobal(Template(value), sub_dict)

  return ret_dict