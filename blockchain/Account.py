class Account:
    def __init__(self, id) -> None:
        self.id = id

    def __repr__(self) -> str:
        return f'Account({self.id})'

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Account):
            raise TypeError()
        return self.id == __value.id
