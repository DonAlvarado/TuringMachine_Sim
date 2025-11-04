class StateTracker:
    def __init__(self, start_state: str):
        self.history = [start_state]
    def push(self, state: str):
        self.history.append(state)
    def snapshot(self):
        seen, out = set(), []
        for s in self.history:
            if s not in seen:
                seen.add(s)
                out.append({"state": s})
        return out
