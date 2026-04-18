class Usage:
    def __init__(self, tokens=0, expenses=None):
        self.tokens = tokens
        self.expenses = expenses or []

    def add_usage(self, tokens):
        self.tokens += tokens
        self.expenses.append(tokens * 0.0001)  # условная цена
