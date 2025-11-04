from app.Back.regex_evaluator import compile_regex_to_dfa
from app.Back.state_tracker import StateTracker
from app.Back.transitions_log import TransitionsLog

BLANK = "_"

class TuringMachine:
    def __init__(self, tape):
        self.tape = tape
        self.head = 0
        self.state_name = {}
        self.name_counter = 0
        self.tracker = StateTracker("q0")
        self.log = TransitionsLog()

    def _name(self, dfa_state):
        if dfa_state not in self.state_name:
            self.state_name[dfa_state] = f"q{self.name_counter}"
            self.name_counter += 1
        return self.state_name[dfa_state]

    def _step(self, de, leer, mov, a):
        self.log.add(de, leer, a, "_", mov)
        self.tracker.push(a)
        if mov == "R":
            self.head += 1
        elif mov == "L":
            self.head = max(0, self.head - 1)

    def run_dfa(self, dfa, input_len):
        q = dfa.start
        cur = self._name(q)
        for _ in range(input_len):
            sym = self.tape[self.head]
            nxt = dfa.delta.get((q, sym))
            if nxt is None:
                self._step(cur, sym, "R", "q_dead")
                self._step("q_dead", BLANK, "S", "q_reject")
                return "reject"
            nxt_name = self._name(nxt)
            self._step(cur, sym, "R", nxt_name)
            q, cur = nxt, nxt_name
        final = "q_accept" if q in dfa.accepts else "q_reject"
        self._step(cur, BLANK, "S", final)
        return "accept" if final == "q_accept" else "reject"

def simulate(pattern: str, input_str: str):
    input_str = (input_str or "").strip()
    dfa = compile_regex_to_dfa(pattern)
    margin = 8
    tape = list(BLANK * margin + input_str + BLANK * margin)
    tm = TuringMachine(tape)
    tm.head = margin
    result = tm.run_dfa(dfa, len(input_str))
    return {
        "pattern": pattern,
        "input": input_str,
        "result": result,
        "steps": tm.log.snapshot(),
        "states_table": tm.tracker.snapshot(),
        "transitions_table": tm.log.snapshot()
    }
