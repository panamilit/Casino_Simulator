from casino.player import Player
from casino.games import coin_flip, coin_flip_is_win



def play_flat_bet(player: Player, 
                  bet_amount: int, 
                  n_rounds: int, 
                  side: str):
    rounds_played = 0
    for _ in range(n_rounds):
        try:
            play_coinflip_round(player= player, bet_amount= bet_amount, chosen_side=side)
        except ValueError:
            break 
        rounds_played += 1
    return (rounds_played, player.balance)



def play_coinflip_round(player: Player, bet_amount: int, chosen_side: str) -> tuple[bool, str]:
    if player.balance < bet_amount:
        raise ValueError("Not enough balance")
    player.bet(bet_amount)
    win, result_side = coin_flip_is_win(chosen_side)
    if win:
        player.win(bet_amount * 2)
    return win, result_side 



def play_martingale(player: Player, base_bet: int, n_rounds: int, side: str):
    current_bet = base_bet
    rounds_played = 0
    for i in range(n_rounds):
        if current_bet > player.balance:
            break
        win  = play_coinflip_round(player=player, bet_amount=current_bet, chosen_side=side)
        if win:
            current_bet = base_bet
        else:
            current_bet *= 2
        rounds_played += 1
    return rounds_played, player.balance

