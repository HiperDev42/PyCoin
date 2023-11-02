class Tx:
    VERSION = 1

    def __init__(self, src, dst, amount) -> None:
        self.src = src
        self.dst = dst
        self.amount = amount

    def __repr__(self) -> str:
        return f'Tx[{self.src} -{self.amount}-> {self.dst}]'
