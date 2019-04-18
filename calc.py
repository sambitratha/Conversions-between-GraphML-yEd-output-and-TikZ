# This example implements a LOGO-like toy language for Python's turtle, with interpreter.

try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass

import turtle

from lark import Lark

calc_grammar = """
    start: LBRACE (instruction SEMICOLON)+ RBRACE
    instruction: NODE node_prop

    node_prop: pos? attrs? name?

    pos: AT LPARAN expr COMMA expr RPARAN

    attrs: LBOX attr RBOX
    
    attr: STR_CONST
        | STR_CONST EQUALS STR_CONST
        | STR_CONST EQUALS expr
    
    name: LBRACE STR_CONST RBRACE

    STR_CONST: NAME

    expr:   expr PLUS expr      -> add
            | expr STAR expr    -> mul
            | expr DIVIDE expr  -> div
            | expr SUB expr     -> sub
            | INT_CONST         -> num

    INT_CONST: NUMBER

    %import common.CNAME -> NAME
    %import common.INT -> NUMBER

    PLUS: "+"
    STAR: "*"
    DIVIDE: "/"
    SUB: "-"
    LBRACE: "{"
    RBRACE: "}"
    LPARAN: "("
    RPARAN: ")"
    LBOX: "["
    RBOX: "]"
    EQUALS: "="
    COMMA: ","
    NODE: "node"
    AT: "at"
    SEMICOLON: ";"
    
    %import common.WS_INLINE
    %ignore WS_INLINE
"""

parser = Lark(calc_grammar)

def run_instruction(t):
    if t.data == 'add':
        return run_instruction(t.children[0])+run_instruction(t.children[2])
    elif t.data == 'mul':
        return run_instruction(t.children[0])*run_instruction(t.children[2])
    elif t.data == 'div':
        return run_instruction(t.children[0])/run_instruction(t.children[2])
    elif t.data == 'sub':
        return run_instruction(t.children[0])-run_instruction(t.children[2])
    elif t.data == 'num':
        return (int)(t.children[0])
    else:
        raise SyntaxError('Unknown instruction: %s' % t.data)


def run_calc(program):
    parse_tree = parser.parse(program)
    print parse_tree
    exit()
    for expr in parse_tree.children:
        x = run_instruction(expr)
        print x

def main():
    while True:
        code = input('> ')
        try:
            run_calc(code)
        except Exception as e:
            print(e)

def test():
    text = """
        c red yellow
        fill { repeat 36 {
            f200 l170
        }}
    """
    run_turtle(text)

main()



