OPERATORS = {'|', '.', '*', '+', '?', '(', ')'}
UNARY = {'*', '+', '?'}
PREC = {'|': 1, '.': 2, '*': 3, '+': 3, '?': 3}
RIGHT_ASSOC = UNARY

def _is_symbol(tok: str) -> bool:
    return tok not in OPERATORS

def insert_concat_ops(pattern: str):
    raw, i = [], 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == '\\':
            if i + 1 >= len(pattern): raise ValueError("Escape final inválido")
            raw.append(pattern[i+1]); i += 2
        else:
            raw.append(ch); i += 1
    out = []
    for j, a in enumerate(raw):
        out.append(a)
        if j == len(raw) - 1: break
        b = raw[j+1]
        a_left  = (_is_symbol(a) or a == ')' or a in UNARY)
        b_right = (_is_symbol(b) or b == '(')
        if a_left and b_right: out.append('.')
    return out

def to_postfix(tokens):
    out, stack = [], []
    for t in tokens:
        if _is_symbol(t): out.append(t)
        elif t == '(':
            stack.append(t)
        elif t == ')':
            while stack and stack[-1] != '(':
                out.append(stack.pop())
            stack.pop()
        else:
            while stack and stack[-1] != '(':
                top = stack[-1]
                if (PREC.get(top, 0) > PREC.get(t, 0) or
                    (PREC.get(top, 0) == PREC.get(t, 0) and t not in RIGHT_ASSOC)):
                    out.append(stack.pop())
                else: break
            stack.append(t)
    while stack: out.append(stack.pop())
    return out
