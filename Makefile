PATH_TO_EXCEL = '/Users/floriansteinkellner/Library/CloudStorage/OneDrive-Persönlich/Music Making/_Practice/_Practice Documents/Übungsprotokoll.xlsx'
SHEET = 'Inventar'
NUM_ROWS = 57
SORT_BY = 'Kategorie'
OUT_PATH = .out
OUT_PATH_ITEMS = .out/items
OUT_PATH_MAIN = .out/main
PYTHON_SCRIPT = create-inventory-list.py
MAIN_TEX_NAME = inventory_full

.DEFAULT_GOAL := default
.PHONY: default clean bin all run test help

default: help

clean:
	@printf '[\e[0;36mINFO\e[0m] Cleaning up folder...\n'
	rm -f -d -r $(OUT_PATH)
	rm -f $(MAIN_TEX_NAME).pdf

all: clean

.IGNORE: run
run: all

	@printf '[\e[0;36mINFO\e[0m] Creating .out folders...\n'
	mkdir $(OUT_PATH)
	mkdir $(OUT_PATH_ITEMS)
	mkdir $(OUT_PATH_MAIN)

	@printf '[\e[0;36mINFO\e[0m] Executing python script...\n'
	python3 $(PYTHON_SCRIPT) $(PATH_TO_EXCEL) $(SHEET) $(NUM_ROWS) $(SORT_BY)
	@printf '[\e[0;36mINFO\e[0m] Python script finished!\n'

	@printf '[\e[0;36mINFO\e[0m] Generating pdf...\n'
	cd '$(OUT_PATH_MAIN)'; pdflatex $(MAIN_TEX_NAME).tex

	cp $(OUT_PATH_MAIN)/$(MAIN_TEX_NAME).pdf $(MAIN_TEX_NAME).pdf
	@printf '[\e[0;36mINFO\e[0m] Finished generating pdf!\n'

help:
	@printf "Usage: make \e[0;36m<TARGET>\e[0m\n"
	@printf "Available targets:\n"
	@awk -F':.*?##' '/^[a-zA-Z_-]+:.*?##.*$$/{printf "  \033[36m%-10s\033[0m%s\n", $$1, $$2}' $(MAKEFILE_LIST)