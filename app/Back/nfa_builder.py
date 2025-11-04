# nfa_builder.py
# Thompson: postfix -> NFA

from collections import defaultdict

EPS = ''  # epsilon

class NFA:
    def __init__(self):
        self.start = None
        self.accept = None
        self.states = set()
        self.trans = defaultdict(lambda: defaultdict(set))

    def add_state(self):
        s = len(self.states)
        self.states.add(s)
        return s

    def add(self, u, sym, v):
        self.trans[u][sym].add(v)

def postfix_to_nfa(postfix):
    stack = []

    def literal(ch):
        m = NFA()
        s = m.add_state()
        f = m.add_state()
        m.start, m.accept = s, f
        m.add(s, ch, f)
        return m

    def graft_into(dst, src):
        mp = {}
        for st in src.states:
            mp[st] = dst.add_state()
        for u in src.states:
            for sym, dests in src.trans[u].items():
                for v in dests:
                    dst.add(mp[u], sym, mp[v])
        return mp[src.start], mp[src.accept]

    def concat(A, B):
        m = NFA()
        sA, fA = graft_into(m, A)
        sB, fB = graft_into(m, B)
        m.start, m.accept = sA, fB
        m.add(fA, EPS, sB)
        return m

    def alternate(A, B):
        m = NFA()
        s = m.add_state()
        f = m.add_state()
        sA, fA = graft_into(m, A)
        sB, fB = graft_into(m, B)
        m.start, m.accept = s, f
        m.add(s, EPS, sA); m.add(s, EPS, sB)
        m.add(fA, EPS, f);  m.add(fB, EPS, f)
        return m

    def star(A):
        m = NFA()
        s = m.add_state()
        f = m.add_state()
        sA, fA = graft_into(m, A)
        m.start, m.accept = s, f
        m.add(s, EPS, sA); m.add(s, EPS, f)
        m.add(fA, EPS, sA); m.add(fA, EPS, f)
        return m

    def clone(A):
        c = NFA()
        graft_into(c, A)
        c.start, c.accept = 0, len(c.states)-1  # por construcción
        return c

    def plus(A):
        # A+ = A . A*
        return concat(A, star(clone(A)))

    def optional(A):
        # A? = A | ε
        m = NFA()
        s = m.add_state()
        f = m.add_state()
        sA, fA = graft_into(m, A)
        m.start, m.accept = s, f
        m.add(s, EPS, sA); m.add(s, EPS, f)
        m.add(fA, EPS, f)
        return m

    for t in postfix:
        if t not in {'|', '.', '*', '+', '?'}:
            stack.append(literal(t))
        elif t == '.':
            B = stack.pop(); A = stack.pop()
            stack.append(concat(A, B))
        elif t == '|':
            B = stack.pop(); A = stack.pop()
            stack.append(alternate(A, B))
        elif t == '*':
            A = stack.pop()
            stack.append(star(A))
        elif t == '+':
            A = stack.pop()
            stack.append(plus(A))
        elif t == '?':
            A = stack.pop()
            stack.append(optional(A))
        else:
            raise ValueError(f"Operador postfix inválido: {t}")

    if len(stack) != 1:
        raise ValueError("Postfix inválido")
    return stack[0]
