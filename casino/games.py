import random


################################################## COIN FLIP ##################################################


HEADS = 'Heads'
TAILS = 'Tails'
COIN_VALUES = [HEADS, TAILS]


def coin_flip() -> str:
    return random.choice(COIN_VALUES)


def coin_flip_is_win(chosen_side: str) -> tuple[bool]:
    result = coin_flip()
    return (result == chosen_side, result)


################################################################################################################


