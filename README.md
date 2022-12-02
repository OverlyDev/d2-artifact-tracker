# d2-artifact-tracker

## Overview

Using a simple `.yaml` file and some custom classes we can make cool things.

The goal of this project was to generate pretty graphs from relatively simple input data. Future additions are just another entry in the `.yaml`.

The graphs can be used to extrapolate trends and predict future outcomes.

## Graphs

The generated graphs are located in the `images` folder

## Usage

To play with it yourself, clone the repo and:

#### Using the makefile
1. Create the virtual environment with `make`
2. Run it with `make run`

or

#### Via straight commandline
1. Have python3 and pip installed
2. Create the virtual environment with `python3 -m venv venv`
3. Install the requirements with `venv/bin/pip3 install -r requirements.txt`
4. Run it with `venv/bin/python3 -m src.main`
