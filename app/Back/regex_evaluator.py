from app.Back.regex_parser import insert_concat_ops, to_postfix
from app.Back.nfa_builder import postfix_to_nfa
from app.Back.dfa_builder import nfa_to_dfa, minimize_dfa

def compile_regex_to_dfa(pattern: str):
    pattern = pattern.strip()
    tokens = insert_concat_ops(pattern)
    postfix = to_postfix(tokens)
    nfa = postfix_to_nfa(postfix)
    dfa = nfa_to_dfa(nfa)
    return minimize_dfa(dfa)
