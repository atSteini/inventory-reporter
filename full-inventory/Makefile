PATH_TO_EXCEL := '/Users/floriansteinkellner/Library/CloudStorage/OneDrive-Persönlich/Music Making/_Practice/_Practice Documents/Übungsprotokoll.xlsx'
SHEET := 'Inventar'
SORT_BY := 'Kategorie' 'Name'
INCLUDE_CHANGE_MARKERS := True

IMG_PATH := img/

OUT_PATH_FORGIG = .out/forgig
OUT_PATH_ITEMS_FORGIG = .out/forgig/items
OUT_PATH_MAIN_FORGIG = .out/forgig/main

OUT_PATH_FULL := .out/full
OUT_PATH_ITEMS_FULL := .out/full/items
OUT_PATH_MAIN_FULL := .out/full/main

PYTHON_SCRIPT := create-inventory-list.py

MAIN_TEX_NAME_FULL := inventory_full
MAIN_TEX_NAME_FORGIG := inventory_forgig

.DEFAULT_GOAL := default
.PHONY: default clean bin all run test help

default: help

clean: cleanfull cleanforgig

cleanfull:
@printf "[\e[0;36mINFO\e[0m] Cleaning up full list folders...\n"
rm -f -d -r $(OUT_PATH)
rm -f $(MAIN_TEX_NAME_FULL).pdf

cleanforgig:
@printf "[\e[0;36mINFO\e[0m] Cleaning up gig folders...\n"
rm -f -d -r $(OUT_PATH_FORGIG)
rm -f $(MAIN_TEX_NAME_FORGIG).pdf

all: clean

fulllist: all	
	@printf "Creating .out folders...\n"
	mkdir $(OUT_PATH)
	mkdir $(OUT_PATH_ITEMS)
	mkdir $(OUT_PATH_MAIN)

	@printf "[\e[0;36mINFO\e[0m] Executing python script...\n"
	python3 $(PYTHON_SCRIPT) -filepath $(PATH_TO_EXCEL) -sheet $(SHEET) --sorts $(SORT_BY) --inclmarkers $(INCLUDE_CHANGE_MARKERS)
	@printf "[\e[0;36mINFO\e[0m] Python script finished!\n"

	@printf "[\e[0;36mINFO\e[0m] Generating pdf...\n"
	cd "$(OUT_PATH_MAIN)"; pdflatex $(MAIN_TEX_NAME).tex; pdflatex $(MAIN_TEX_NAME).tex; 

	cp $(OUT_PATH_MAIN)/$(MAIN_TEX_NAME).pdf $(MAIN_TEX_NAME).pdf
	@printf "[\e[0;36mINFO\e[0m] Finished generating pdf!\n"

forgig: all	
	@printf "Creating .out folders...\n"
	mkdir $(OUT_PATH)
	mkdir $(OUT_PATH_ITEMS)
	mkdir $(OUT_PATH_MAIN)

	@printf "[\e[0;36mINFO\e[0m] Executing python script...\n"
	python3 $(PYTHON_SCRIPT) -filepath $(PATH_TO_EXCEL) -sheet $(SHEET) --sorts $(SORT_BY) --inclmarkers $(INCLUDE_CHANGE_MARKERS)
	@printf "[\e[0;36mINFO\e[0m] Python script finished!\n"

	@printf "[\e[0;36mINFO\e[0m] Generating pdf...\n"
	cd "$(OUT_PATH_MAIN)"; pdflatex $(MAIN_TEX_NAME).tex; pdflatex $(MAIN_TEX_NAME).tex; 

	cp $(OUT_PATH_MAIN)/$(MAIN_TEX_NAME).pdf $(MAIN_TEX_NAME).pdf
	@printf "[\e[0;36mINFO\e[0m] Finished generating pdf!\n"

help:
	@printf "Usage: make \e[0;36m<TARGET>\e[0m\n"
	@printf "Available targets:\n"
	@awk -F':.*?##' '/^[a-zA-Z_-]+:.*?##.*$$/{printf "  \033[36m%-10s\033[0m%s\n", $$1, $$2}' $(MAKEFILE_LIST)