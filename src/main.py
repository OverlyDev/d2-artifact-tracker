import pathlib
from typing import List

import matplotlib
import numpy as np
from matplotlib import pyplot as plt

from src.data.generate import (
    CWD,
    Season,
    convert_input_yaml_to_season_list,
    create_template_yml,
)


CUTOFF_SEASON = 12


SAVE_FOLDER = CWD.parent.parent / "images"
pathlib.Path.mkdir(SAVE_FOLDER, exist_ok=True)

# Tweak matplotlib settings
font = {"family": "monospace", "weight": "normal", "size": 6}
matplotlib.rc("font", **font)


def save_graph_as_image(filename: str):
    save_file_path = SAVE_FOLDER / filename
    plt.tight_layout()
    plt.savefig(save_file_path, dpi=300)


def total_champ_occurrences(seasons: List[Season], cutoff=False):
    data = {}

    for season in seasons:

        if cutoff:
            if season.number < CUTOFF_SEASON:
                continue
            title = f"Total Occurrences (S{CUTOFF_SEASON} to now)"
            file_suffix = "-cutoff"
        else:
            title = "Total Occurrences (S8 to now)"
            file_suffix = ""

        for mod in season.champion_weapons:
            if mod.champ_type not in data:
                data[mod.champ_type] = 1
            else:
                data[mod.champ_type] = data[mod.champ_type] + 1

    champ_types = []
    occurrences = []
    for k, v in data.items():
        champ_types.append(k.name.title())
        occurrences.append(v)

    x = np.array(champ_types)
    y = np.array(occurrences)

    # plt.figure(figsize=(3, 2))
    plt.bar(x, y, width=0.5)
    plt.title(title)
    save_graph_as_image(f"total-occurrences{file_suffix}.png")
    plt.clf()


def per_weapon_count(seasons: List[Season], cutoff=False):
    data = {}

    for season in seasons:

        if cutoff:
            if season.number < CUTOFF_SEASON:
                continue
            title_suffix = f"Occurrence Per Weapon Type (S{CUTOFF_SEASON} to now)"
            file_suffix = "-cutoff"
        else:
            title_suffix = "Occurrence Per Weapon Type (S8 to now)"
            file_suffix = ""

        for mod in season.champion_weapons:
            if mod.champ_type not in data:
                data[mod.champ_type] = {}
            if mod.weapon_type not in data[mod.champ_type]:
                data[mod.champ_type][mod.weapon_type] = 1
            else:
                data[mod.champ_type][mod.weapon_type] = (
                    data[mod.champ_type][mod.weapon_type] + 1
                )

    for champ, weapons in data.items():
        weapon_type = []
        occurrences = []
        for weapon, value in weapons.items():
            weapon_type.append(weapon.name.title().replace("_", " "))
            occurrences.append(int(value))
        x = np.array(weapon_type)
        y = np.array(occurrences)

        plt.figure(figsize=(6, 2))
        plt.bar(x, y, width=0.5)
        plt.title(f"{champ.name.title()} {title_suffix}")
        save_graph_as_image(f"{champ.name.lower()}{file_suffix}.png")
        plt.clf()


if __name__ == "__main__":

    CUTOFF = False

    create_template_yml()
    seasons = convert_input_yaml_to_season_list()

    total_champ_occurrences(seasons, cutoff=CUTOFF)
    per_weapon_count(seasons, cutoff=CUTOFF)
