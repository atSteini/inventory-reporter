include .env

PATH_TO_EXCEL := $(ENV_PATH_TO_EXCEL)
INV_SHEET := 'Inventar'
SORT_BY := 'Kategorie' 'Name'
INCLUDE_CHANGE_MARKERS := 1

GIG_ID = $(ENV_GIG_ID)

GIG_SHEET := 'Gigprotokoll'
GIG_GEAR_COL := 'Ausrüstung'
GIG_NAMED_GEAR_SHEET = 'Standardinventarlisten'
GIG_IDS_KV := 'Name' 'IDs'
GIG_BREAK_AFTER_SEC := 0
GIG_BREAK_AFTER_TOTAL := 19

IMG_PATH_SRC := $(ENV_IMG_PATH_SRC)
IMG_PATH_DEST := img/

TPL_FULL_ITEM = latex-templates/tpl_item_full.tex
TPL_FULL_MAIN = latex-templates/tpl_inventory_full.tex
TPL_GIG_ITEM = latex-templates/tpl_item_gig.tex
TPL_GIG_MAIN = latex-templates/tpl_inventory_gig.tex

OUT_PATH_GIG := .out/gig
OUT_PATH_ITEMS_GIG := items
OUT_PATH_MAIN_GIG := main
OUT_PATH_IDS_GIG := data
IDS_FILE = gig_data.txt
SECTION_CHANGE_GIG := '\section{$\{KATEGORIE}}'

OUT_PATH_FULL := .out/full
OUT_PATH_ITEMS_FULL := items
OUT_PATH_MAIN_FULL := main

PYTHON_SCRIPT := create-inventory-list.py

MAIN_TEX_NAME_FULL := inventory_full
MAIN_TEX_NAME_GIG := inventory_gig

default: help

sync_images:
	@printf "[\e[0;36mINFO\e[0m] Syncing image folders...\n"
	cp -a $(IMG_PATH_SRC) $(IMG_PATH_DEST)

clean: clean_img clean_full clean_gig

clean_img:
	@printf "[\e[0;36mINFO\e[0m] Cleaning up img folder...\n"
	rm -f -d -r $(IMG_PATH_DEST)

clean_full:
	@printf "[\e[0;36mINFO\e[0m] Cleaning up full list folders...\n"
	rm -f -d -r $(OUT_PATH_FULL)
	rm -f $(MAIN_TEX_NAME_FULL).pdf

clean_gig:
	@printf "[\e[0;36mINFO\e[0m] Cleaning up gig folders...\n"
	rm -f -d -r $(OUT_PATH_GIG)
	rm -f $(MAIN_TEX_NAME_GIG).pdf

run: clean sync_images run_full run_gig

run_full: clean_full
	@printf "Creating .out folders...\n"
	mkdir $(OUT_PATH_FULL); cd $(OUT_PATH_FULL); mkdir $(OUT_PATH_ITEMS_FULL); mkdir $(OUT_PATH_MAIN_FULL)

	@printf "[\e[0;36mINFO\e[0m] Executing python script...\n"
	python3 --version
	python3 $(PYTHON_SCRIPT) -filepath $(PATH_TO_EXCEL) -sheet $(INV_SHEET) --sorts $(SORT_BY) --writesections $(INCLUDE_CHANGE_MARKERS)
	@printf "[\e[0;36mINFO\e[0m] Python script finished!\n"

	@printf "[\e[0;36mINFO\e[0m] Generating pdf...\n"
	cd "$(OUT_PATH_FULL)/$(OUT_PATH_MAIN_FULL)"; pdflatex $(MAIN_TEX_NAME_FULL).tex; pdflatex $(MAIN_TEX_NAME_FULL).tex; 

	cp $(OUT_PATH_FULL)/$(OUT_PATH_MAIN_FULL)/$(MAIN_TEX_NAME_FULL).pdf $(MAIN_TEX_NAME_FULL).pdf
	@printf "[\e[0;36mINFO\e[0m] Finished generating pdf!\n"

run_gig: clean_gig
	@printf "Creating .out folders...\n"
	mkdir $(OUT_PATH_GIG); cd $(OUT_PATH_GIG); mkdir $(OUT_PATH_ITEMS_GIG); mkdir $(OUT_PATH_MAIN_GIG); mkdir $(OUT_PATH_IDS_GIG)

	@printf "[\e[0;36mINFO\e[0m] Executing id finder for gig python script...\n"
	python3 write-gig-list.py -filepath $(PATH_TO_EXCEL) -gigsheet $(GIG_SHEET) -outpath $(OUT_PATH_GIG)/$(OUT_PATH_IDS_GIG)/$(IDS_FILE) -gearcol $(GIG_GEAR_COL) -invsheet $(GIG_NAMED_GEAR_SHEET) --namedgearcols $(GIG_IDS_KV) --forid $(GIG_ID)
	@printf "[\e[0;36mINFO\e[0m] ID finder script finished!\n"

	@printf "[\e[0;36mINFO\e[0m] Executing latex generator python script...\n"
	python3 $(PYTHON_SCRIPT) -filepath $(PATH_TO_EXCEL) -sheet $(INV_SHEET) --sorts $(SORT_BY) --writesections 0 --tplitem $(TPL_GIG_ITEM) --tplmain $(TPL_GIG_MAIN) --outpath $(OUT_PATH_GIG) --namemain $(MAIN_TEX_NAME_GIG).tex --braftersection $(GIG_BREAK_AFTER_SEC) --braftertotal $(GIG_BREAK_AFTER_TOTAL) --gigdatafrom $(OUT_PATH_GIG)/$(OUT_PATH_IDS_GIG)/$(IDS_FILE)
	@printf "[\e[0;36mINFO\e[0m] Latex generator script finished!\n"

	@printf "[\e[0;36mINFO\e[0m] Generating pdf...\n"
	cd "$(OUT_PATH_GIG)/$(OUT_PATH_MAIN_GIG)"; pdflatex $(MAIN_TEX_NAME_GIG).tex; pdflatex $(MAIN_TEX_NAME_GIG).tex; 

	cp $(OUT_PATH_GIG)/$(OUT_PATH_MAIN_GIG)/$(MAIN_TEX_NAME_GIG).pdf $(MAIN_TEX_NAME_GIG).pdf
	@printf "[\e[0;36mINFO\e[0m] Finished generating pdf!\n"

help:
	@printf "Usage: make \e[0;36m<TARGET>\e[0m\n"
	@printf "Available targets:\n"
	@awk -F':.*?##' '/^[a-zA-Z_-]+:.*?##.*$$/{printf "  \033[36m%-10s\033[0m%s\n", $$1, $$2}' $(MAKEFILE_LIST)