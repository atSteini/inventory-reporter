PATH_TO_EXCEL := '/Users/floriansteinkellner/Library/CloudStorage/OneDrive-Persönlich/Music Making/_Practice/_Practice Documents/Übungsprotokoll.xlsx'
SHEET := 'Inventar'
SORT_BY := 'Kategorie' 'Name'
INCLUDE_CHANGE_MARKERS := True

IMG_PATH := img/

OUT_PATH_GIG = .out/forgig
OUT_PATH_ITEMS_GIG = .out/forgig/items
OUT_PATH_MAIN_GIG = .out/forgig/main

OUT_PATH_FULL := .out/full
OUT_PATH_ITEMS_FULL := .out/full/items
OUT_PATH_MAIN_FULL := .out/full/main

PYTHON_SCRIPT := create-inventory-list.py

MAIN_TEX_NAME_FULL := inventory_full
MAIN_TEX_NAME_GIG := inventory_forgig

.DEFAULT_GOAL := default
.PHONY: default clean bin all run test help

default: help

clean: cleanfull cleanforgig

clean_full:
	@printf "[\e[0;36mINFO\e[0m] Cleaning up full list folders...\n"
	rm -f -d -r $(OUT_PATH_FULL)
	rm -f $(MAIN_TEX_NAME_FULL).pdf

clean_gig:
	@printf "[\e[0;36mINFO\e[0m] Cleaning up gig folders...\n"
	rm -f -d -r $(OUT_PATH_GIG)
	rm -f $(MAIN_TEX_NAME_GIG).pdf

run: clean run_full run_gig

run_full: clean_full
	@printf "Creating .out folders...\n"
	mkdir $(OUT_PATH_FULL)
	mkdir $(OUT_PATH_ITEMS_FULL)
	mkdir $(OUT_PATH_MAIN_FULL)

	@printf "[\e[0;36mINFO\e[0m] Executing python script...\n"
	python3 --version
	python3 $(PYTHON_SCRIPT) -filepath $(PATH_TO_EXCEL) -sheet $(SHEET) --sorts $(SORT_BY) --inclmarkers $(INCLUDE_CHANGE_MARKERS)
	@printf "[\e[0;36mINFO\e[0m] Python script finished!\n"

	@printf "[\e[0;36mINFO\e[0m] Generating pdf...\n"
	cd "$(OUT_PATH_MAIN_FULL)"; pdflatex $(MAIN_TEX_NAME_FULL).tex; pdflatex $(MAIN_TEX_NAME_FULL).tex; 

	cp $(OUT_PATH_MAIN_FULL)/$(MAIN_TEX_NAME_FULL).pdf $(MAIN_TEX_NAME_FULL).pdf
	@printf "[\e[0;36mINFO\e[0m] Finished generating pdf!\n"

run_gig: clean_gig	
	@printf "Creating .out folders...\n"
	mkdir $(OUT_PATH_GIG)
	mkdir $(OUT_PATH_ITEMS_GIG)
	mkdir $(OUT_PATH_MAIN_GIG)

	@printf "[\e[0;36mINFO\e[0m] Executing python script...\n"
	python3 $(PYTHON_SCRIPT) -filepath $(PATH_TO_EXCEL) -sheet $(SHEET) --sorts $(SORT_BY) --inclmarkers $(INCLUDE_CHANGE_MARKERS)
	@printf "[\e[0;36mINFO\e[0m] Python script finished!\n"

	@printf "[\e[0;36mINFO\e[0m] Generating pdf...\n"
	cd "$(MAIN_TEX_NAME_GIG)"; pdflatex $(MAIN_TEX_NAME_GIG).tex; pdflatex $(MAIN_TEX_NAME_GIG).tex; 

	cp $(OUT_PATH_MAIN_GIG)/$(MAIN_TEX_NAME_GIG).pdf $(MAIN_TEX_NAME_GIG).pdf
	@printf "[\e[0;36mINFO\e[0m] Finished generating pdf!\n"

help:
	@printf "Usage: make \e[0;36m<TARGET>\e[0m\n"
	@printf "Available targets:\n"
	@awk -F':.*?##' '/^[a-zA-Z_-]+:.*?##.*$$/{printf "  \033[36m%-10s\033[0m%s\n", $$1, $$2}' $(MAKEFILE_LIST)