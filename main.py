from casino.player import Player
from casino.games import HEADS, TAILS
from casino.simulation import play_coinflip_round, play_flat_bet, play_martingale


def ask_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            return value
        except ValueError:
            print("Please enter a valid value (integer).")


def ask_side(prompt: str) -> str:
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("h", "heads"):
            return HEADS
        if raw in ("t", "tails"):
            return TAILS
        print("Enter 'H/Heads' or 'T/Tails'.")


def ask_name(prompt: str) -> str:
        while True:
            name = input(prompt)
            if len(name) <= 0:
                print("Invalid value. Please enter a valid username.")
                continue
            else:
                return name


def choose_game(prompt: str) -> str:
    while True:
        print("\n1) Coin flip")
        print("2) Roulette (Coming soon...)")
        print("3) My Profile")
        print("q) Quit\n")
        game = input(prompt)
        if game in ("1", "2", "3", "q"):
            return game
        else:
            print("Invalid input. Enter valid value.")
            continue

      
def choose_mode(prompt: str) -> str:
        while True:
            print("\n1) Manual (one round)")
            print("2) Flat bet")
            print("3) Martingale")
            print("b) Back\n")
            game_mode = input(prompt)
            if game_mode in ("1", "2", "3", "b"):
                return game_mode
            else:
                print("Invalid input. Enter valid value.")
                continue


def main():
    print("Welcome to Casino Simulator!")
    print("Follow the instructions below to create a profile.")

    name = ask_name("Enter your username: ")
    balance = ask_int("Enter your starting balance (e.g. 100): ")
    player = Player(name=name, balance=balance)

    print(f"\nHello {player.name}!")
    print(f"Your balance is {player.balance}$")


    while True:
        game = choose_game("Choose game to play: ")
        if game == "q":
            break
        elif game == "3":
            print(player)
            continue

        if game == "1":
            while True:
                mode = choose_mode("Choose mode to simulate: ")

                if mode == "b":
                    break

                if mode == "1":
                    while True:   
                        if player.balance <= 0:
                                print("You're out of funds. Game over!")
                                break
                        raw = input("Press Enter to play a new round, or type 'q' to quit: ").strip().lower()
                        if raw == 'q':
                            break
                        bet_amount = ask_int(f"Bet amount (<= {player.balance}): ")
                        side = ask_side("Choose side (H/T): ")
                        try:
                            win = play_coinflip_round(player=player, bet_amount=bet_amount, chosen_side=side)
                        except ValueError as e:
                            print(f"Cannot place bet: {e}")
                            continue
                        print("WIN!" if win else "LOSE!")
                        print(player)


                elif mode == "2":
                    bet_amount = ask_int("Enter bet amount: ")
                    n_rounds = ask_int("Enter number of rounds: ")
                    side = ask_side("Choose side (H/T): ")
                    rounds_played, final_balance = play_flat_bet(
                        player= player,
                    bet_amount= bet_amount, 
                    n_rounds= n_rounds, 
                    side= side)
                    print(f"Rounds played: {rounds_played}")
                    print(f"Final balance: {final_balance}")
                    continue
     

                elif mode == "3":
                    base_net = ask_int("Enter bet amount: ")
                    n_rounds = ask_int("Enter number of rounds: ")
                    side = ask_side("Choose side (H/T): ")
                    rounds_played, final_balance = play_martingale(
                        player= player,
                        base_net= base_net,
                        n_rounds= n_rounds,
                        side = side
                    )
                    print(f"Rounds played: {rounds_played}")
                    print(player)
                    continue


if __name__ == "__main__":
    main()