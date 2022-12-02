import pathlib
import re
from enum import Enum
from sys import exit as sys_exit
from typing import List

import yaml
from fuzzywuzzy import fuzz
from pydantic import BaseModel


CWD = pathlib.Path(__file__).parent.resolve()
INPUT_YAML = CWD / "input.yaml"
TEMPLATE_YAML = CWD / "template.yaml"


class AbilityType(Enum):
    CLASS = 1
    GRENADE = 2
    MELEE = 3

    def __str__(self) -> str:
        return str(self.name.title())


class AbilityElement(Enum):
    ARC = 1
    SOLAR = 2
    VOID = 3
    STASIS = 4

    def __str__(self) -> str:
        return str(self.name.title())


class WeaponType(Enum):
    SCOUT = 1
    PULSE = 2
    AUTO = 3
    HAND_CANNON = 4
    SIDEARM = 5
    SMG = 6
    BOW = 7
    TRACE = 8
    SHOTGUN = 9
    SNIPER = 10
    GRENADE_LAUNCHER = 11
    FUSION = 12
    GLAIVE = 13
    ROCKET_LAUNCHER = 14
    SWORD = 15
    MACHINE_GUN = 16

    def __str__(self) -> str:
        return str(self.name.title().replace("_", " "))


class ChampType(Enum):
    BARRIER = 1
    OVERLOAD = 2
    UNSTOP = 3
    ANY = 4

    def __str__(self) -> str:
        return str(self.name.title())


class ChampionWeaponMod(BaseModel):
    champ_type: ChampType
    weapon_type: WeaponType


class ChampionAbilityMod(BaseModel):
    champ_type: ChampType
    ability_type: AbilityType
    ability_element: List[AbilityElement]


class ChampionOtherStunMod(BaseModel):
    champ_type: List[ChampType]
    trigger: str


class ChampionOtherMod(BaseModel):
    champ_type: List[ChampType]
    effect: str


class Season(BaseModel):
    number: int
    name: str
    champion_weapons: List[ChampionWeaponMod] = []
    champion_abilities: List[ChampionAbilityMod] = []
    champion_stun: List[ChampionOtherStunMod] = []
    champion_other: List[ChampionOtherMod] = []

    def neat_print(self):
        def border():
            print("-" * 30)

        border()
        print(f"Season {self.number} | {self.name}")

        if len(self.champion_weapons) > 0:
            print("Champion Weapon Mods:")
            for i in self.champion_weapons:
                print("\t", i.champ_type, i.weapon_type)

        if len(self.champion_abilities) > 0:
            print("Champion Ability Mods:")
            for i in self.champion_abilities:
                print(
                    "\t",
                    i.champ_type,
                    i.ability_type,
                    ", ".join([str(x) for x in i.ability_element]),
                )

        if len(self.champion_stun) > 0:
            print("Other Champion Stun Mods:")
            for i in self.champion_stun:
                print("\t", i.trigger, ", ".join([str(x) for x in i.champ_type]))

        if len(self.champion_other) > 0:
            print("Other Champion Related Mods:")
            for i in self.champion_other:
                print(
                    "\t",
                    i.effect,
                    ", ".join([str(x) for x in i.champ_type]),
                )

        border()


class MatchScore(BaseModel):
    string_one: str
    string_two: str
    score: int


class MatchResult(BaseModel):
    input_value: str
    best_match: str
    score: int


def fuzzy_match_score(string1: str, string2: str) -> MatchScore:
    score = fuzz.ratio(string1, string2)
    return MatchScore(string_one=string1, string_two=string2, score=score)


def fuzzy_match_against_list(input_string, items: list) -> MatchResult:
    best_match = None
    highest_score = 0
    for i in items:
        result = fuzzy_match_score(input_string, i)
        if result.score > highest_score:
            highest_score = result.score
            best_match = i
    return MatchResult(
        input_value=input_string, best_match=best_match, score=highest_score
    )


def match_weapon_str_to_weapon_type(input_weapon: str) -> WeaponType:
    compare_list = [x.lower().replace("_", " ") for x in WeaponType._member_names_]
    result = fuzzy_match_against_list(input_weapon, compare_list)
    best_match = WeaponType[result.best_match.upper().replace(" ", "_")]

    if result.score < 55:
        print(f"Double-check input.yml, best match for {input_weapon} was {best_match}")
    return best_match


def match_champ_str_to_champ_type(champ: str) -> ChampType:
    compare_list = [x.lower() for x in ChampType._member_names_]
    result = fuzzy_match_against_list(champ.lower(), compare_list)
    best_match = ChampType[result.best_match.upper()]
    return best_match


def match_ability_str_to_ability_type(input_ability: str) -> AbilityType:
    ability_compare_list = [x.lower() for x in AbilityType._member_names_]
    ability_string = input_ability.lower()
    ability_result = fuzzy_match_against_list(ability_string, ability_compare_list)
    ability = AbilityType[ability_result.best_match.upper()]
    return ability


def match_element_str_to_element_type(input_element: str) -> AbilityElement:
    element_compare_list = [x.lower() for x in AbilityElement._member_names_]
    element_str = input_element.lower()
    element_result = fuzzy_match_against_list(element_str, element_compare_list)
    element = AbilityElement[element_result.best_match.upper()]
    return element


def convert_input_yaml_to_season_list() -> List[Season]:
    with open(INPUT_YAML, "r", encoding="utf-8") as handle:
        raw = handle.read()
    yaml_obj = yaml.safe_load(raw)

    season_list: List[Season] = []

    for season in yaml_obj.keys():

        # Get the season number
        regex_str = re.compile(r"season_(?P<season>\d*)")
        match_result = re.match(regex_str, season)
        if match_result is None:
            print(f"Couldn't match '{season}'")
            sys_exit(1)
        else:
            season_num = match_result.group("season")

        # Get the season name
        season_name = yaml_obj[season]["name"]

        # Create instance of Season
        season_obj = Season(number=season_num, name=season_name)

        # Get the champ weapons
        for champ in yaml_obj[season]["champ_weapons"]:
            champ_type = match_champ_str_to_champ_type(champ)

            for weapon in yaml_obj[season]["champ_weapons"][champ]:
                weapon_type = match_weapon_str_to_weapon_type(weapon)
                weapon_mod = ChampionWeaponMod(
                    champ_type=champ_type, weapon_type=weapon_type
                )
                season_obj.champion_weapons.append(weapon_mod)

        # Get the champ abilities
        for champ in yaml_obj[season]["champ_abilities"]:
            champ_type = match_champ_str_to_champ_type(champ)

            for ability in yaml_obj[season]["champ_abilities"][champ]:
                if not ability:
                    continue
                ability_split = ability.split(" ")
                ability_type = match_ability_str_to_ability_type(
                    ability_split[0].lower()
                )

                elements = []
                for i in ability_split[1:]:
                    elements.append(match_element_str_to_element_type(i.lower()))

                ability_mod = ChampionAbilityMod(
                    champ_type=champ_type,
                    ability_type=ability_type,
                    ability_element=elements,
                )
                season_obj.champion_abilities.append(ability_mod)

        # Get the other champ stun mods
        for item in yaml_obj[season]["champ_stun"]:
            if len(item["champ_type"]) > 0:
                champ_types = []
                for champ in item["champ_type"]:
                    champ_types.append(match_champ_str_to_champ_type(champ))
                trigger = item["trigger"]

                champ_stun = ChampionOtherStunMod(
                    champ_type=champ_types, trigger=trigger
                )

                season_obj.champion_stun.append(champ_stun)

        # Get the other champ related mods
        for item in yaml_obj[season]["champ_other"]:
            if len(item["champ_type"]) > 0:
                champ_types = []
                for champ in item["champ_type"]:
                    champ_types.append(match_champ_str_to_champ_type(champ))
                effect = item["effect"]

                champ_other = ChampionOtherMod(champ_type=champ_types, effect=effect)

                season_obj.champion_other.append(champ_other)

        season_list.append(season_obj)

    return season_list


def create_template_yml():
    template = {
        "season_NUM": {
            "name": "",
            "champ_weapons": {
                "barrier": [],
                "overload": [],
                "unstop": [],
            },
            "champ_abilities": {
                "barrier": [],
                "overload": [],
                "unstop": [],
            },
            "champ_stun": [{"champ_type": [], "trigger": ""}],
            "champ_other": [{"champ_type": [], "effect": ""}],
        }
    }

    with open(TEMPLATE_YAML, "w", encoding="utf-8") as handle:
        handle.write(yaml.dump(template))
