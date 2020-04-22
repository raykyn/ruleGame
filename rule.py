#!/usr/bin/env python3

import json


DEBUG = True
TEXTS = None


def print_debug(text):
    if DEBUG:
        print(text)


def get_player_input(lower_input=True):
    answer = input(">> ")
    while(len(answer) == 0):
        answer = input(">> ")
    if lower_input:
        answer = answer.lower()
    return answer
    

def display_message_options_wait_for_answer(message, options):
    """
    message: string
    options: (func, string)
    """
    print(message)
    for func, op in options:
        print("> "+op)
    print()
    player_answer = get_player_input()
    for func, op in options:
        op = op.lower()
        if player_answer == op or op.startswith(player_answer):
            func()


def start_new_game():
    print("Starting a new game!")
    


def load_game():
    print("Loading an existing game!")


def show_menu():
    menu_string = TEXTS["game_menu"]["menu_text"]
    options = [
        (start_new_game, TEXTS["game_menu"]["start_new_game"]),
        (load_game, TEXTS["game_menu"]["load_game"]),
        (exit, TEXTS["game_menu"]["exit_game"])
        ]
    display_message_options_wait_for_answer(menu_string, options)


def main():
    global TEXTS
    TEXTS = json.load(open("modules/texts.json", encoding="utf8"))
    show_menu()


if __name__ == "__main__":
    main()