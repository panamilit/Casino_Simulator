class Player:
    def __init__(self, *, name: str, balance: int):
        self.name = name
        self.balance = balance

    def bet(self, amount):
        if amount <= 0:
            raise ValueError("Bet amount must be greater than $0.")
        elif amount > self.balance:
            raise ValueError("Insufficient funds: bet cannot exceed your current balance.")
        else:
            self.balance -= amount

    def win(self, amount):
        if amount <= 0:
            raise ValueError
        else:
            self.balance += amount

    def __str__(self):
        return f"\nPlayer Account Information: Name: {self.name} | Balance: {self.balance}"
    

 