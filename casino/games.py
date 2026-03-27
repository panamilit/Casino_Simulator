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




################################################## MACHINE SLOTS ##################################################


SLOT_SYMBOLS = ["7", "GOLD", "CHERRY", "LEMON"]


def spin_slots() -> list[str]:
    return random.choices(SLOT_SYMBOLS, k=3)


def get_slots_multiplier(result: list[str]) -> int:
    unique = len(set(result))
    
    if unique == 1:
        return 3
    elif unique == 2:
        return 2
    else: 
        return 0


################################################################################################################