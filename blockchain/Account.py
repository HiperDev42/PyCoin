class Account:
    def __init__(self, id) -> None:
        self.id = id

    def __repr__(self) -> str:
        return f'Account({self.id})'
