class TransitionsLog:
    def __init__(self):
        self.rows = []
    def add(self, de, leer, a, escribir, mov):
        self.rows.append({
            "from": de, "read": leer, "to": a, "write": escribir, "move": mov
        })
    def snapshot(self):
        return self.rows[:]
