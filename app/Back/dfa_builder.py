# dfa_builder.py
# NFA -> DFA (subset) y minimización (Hopcroft)

from collections import deque
from typing import Set, FrozenSet, Dict, Tuple
from app.Back.nfa_builder import NFA, EPS

class DFA:
    def __init__(self):
        self.states: Set[FrozenSet[int]] = set()
        self.alphabet: Set[str] = set()
        self.delta: Dict[Tuple[FrozenSet[int], str], FrozenSet[int]] = {}
        self.start: FrozenSet[int] = frozenset()
        self.accepts: Set[FrozenSet[int]] = set()

def _eps_closure(nfa: NFA, S: Set[int]) -> Set[int]:
    stack = list(S)
    C = set(S)
    while stack:
        u = stack.pop()
        for v in nfa.trans[u].get(EPS, ()):
            if v not in C:
                C.add(v); stack.append(v)
    return C

def _move(nfa: NFA, S: Set[int], a: str) -> Set[int]:
    R = set()
    for u in S:
        for v in nfa.trans[u].get(a, ()):
            R.add(v)
    return R

def nfa_to_dfa(nfa: NFA) -> DFA:
    dfa = DFA()
    # alfabeto = todos los símbolos no epsilon que aparecen
    alphabet = set()
    for u in nfa.states:
        for sym in nfa.trans[u]:
            if sym != EPS:
                alphabet.add(sym)
    dfa.alphabet = alphabet

    start = frozenset(_eps_closure(nfa, {nfa.start}))
    dfa.start = start
    dfa.states.add(start)
    if nfa.accept in start:
        dfa.accepts.add(start)

    q = deque([start])
    while q:
        S = q.popleft()
        for a in alphabet:
            T = frozenset(_eps_closure(nfa, _move(nfa, set(S), a)))
            if not T:
                continue
            if T not in dfa.states:
                dfa.states.add(T)
                if nfa.accept in T:
                    dfa.accepts.add(T)
                q.append(T)
            dfa.delta[(S, a)] = T
    return dfa

def minimize_dfa(dfa: DFA) -> DFA:
    # completar con estado muerto si hace falta
    dead = frozenset({'__dead__'})
    delta = dict(dfa.delta)
    states = set(dfa.states)
    for S in list(states):
        for a in dfa.alphabet:
            if (S, a) not in delta:
                delta[(S, a)] = dead
    if any(T == dead for T in delta.values()):
        states.add(dead)
        for a in dfa.alphabet:
            delta[(dead, a)] = dead

    A = set(dfa.accepts)
    N = states - A
    P = [A, N] if N else [A]
    W = deque([A] if A else [])

    def pred(X, a):
        res = set()
        for (S, sym), T in delta.items():
            if sym == a and T in X:
                res.add(S)
        return res

    while W:
        Ablk = W.popleft()
        for a in dfa.alphabet:
            X = pred(Ablk, a)
            newP = []
            for Y in P:
                i, d = Y & X, Y - X
                if i and d:
                    newP += [i, d]
                    if Y in W:
                        W.remove(Y); W += [i, d]
                    else:
                        W.append(i if len(i) <= len(d) else d)
                else:
                    newP.append(Y)
            P = newP

    rep = {}
    min_states = set()
    for block in P:
        rep_state = frozenset(block)
        for s in block:
            rep[s] = rep_state
        min_states.add(rep_state)

    min_delta = {}
    for (S, a), T in delta.items():
        min_delta[(rep[S], a)] = rep[T]

    out = DFA()
    out.states = min_states
    out.alphabet = set(dfa.alphabet)
    out.delta = min_delta
    out.start = rep[dfa.start]
    out.accepts = {rep[s] for s in dfa.accepts}
    return out
