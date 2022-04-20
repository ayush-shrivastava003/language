class Error(Exception):
    def __init__(self, msg, token, *args: object) -> None:
        super().__init__(*args)
        self.msg = msg
        self.line = token.line
        self.column = token.column