# define the name of the virtual environment directory
VENV := venv

# list of .in files for pip-tools
REQS := requirements.in dev-requirements.in

# default target, when make executed without arguments
all: $(VENV)

# install required packages from .txt files
$(VENV): $(VENV)/bin/activate
	$(VENV)/bin/pip3 install pip-tools
	$(VENV)/bin/pip-sync *requirements.txt

# shortcut target
$(VENV)/bin/activate:
	python3 -m venv $(VENV)

# generate requirements .txt files
reqs:
	for file in $(REQS) ; do $(VENV)/bin/pip-compile --resolver=backtracking $$file ; done

# upgrade requirements versions
reqs_upgrade:
	for file in $(REQS) ; do $(VENV)/bin/pip-compile --resolver=backtracking --upgrade $$file ; done

# formatters
format:
	$(VENV)/bin/black src
	$(VENV)/bin/importanize src

clean:
	rm -rf images/*

# delete the venv
clean_venv:
	rm -rf $(VENV)

# run the thing
run: format
	$(VENV)/bin/python3 -m src.main

.PHONY: all, $(VENV), reqs, reqs_upgrade, format, clean, clean_venv, run