# yellow!80
# variable get range 
#make changes here for which nodes the edge belongs to

try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass


from class_objects import *

from lark import Lark


#how to write grammar for node_draw (conflict issues)

calc_grammar = """
    start: LBRACE (instruction SEMICOLON)+ RBRACE

    instruction: BACKSLASH NODE for_each* node_prop             -> node_ins
                |BACKSLASH DRAW node_draw (edge_details? node_draw)*    -> draw_ins

    node_draw:    position? NODE node_prop              -> typenode
                | LPARAN STR_CONST RPARAN                 -> lookup



    edge_details: EDGE attrs?

    for_each: FOREACH variable IN LBRACE range RBRACE

    variable: BACKSLASH STR_CONST


    range: loopvar COMMA DOT DOT DOT COMMA loopvar  -> rangetype1 
            | INT_CONST (COMMA INT_CONST)*              -> rangetype2

    loopvar: INT_CONST                              -> integer
            | variable                              -> var

    node_prop: id? pos? attrs? name?

    id: LPARAN STR_CONST RPARAN                        

    pos: AT LPARAN expr COMMA expr RPARAN

    position: LPARAN expr COMMA expr RPARAN

    attrs: LBOX attr (COMMA attr)* RBOX
    
    attr: STR_CONST+                         -> unnamed_attr
        | STR_CONST+ EQUALS STR_CONST+        -> str_attr
        | STR_CONST+ EQUALS expr             -> num_attr
        | STR_CONST+ EQUALS 
    
    name: LBRACE STR_CONST RBRACE

    expr:   expr PLUS expr                  -> add
            | expr SUB expr                 -> sub
            | mul_expr                      -> expr2
            | variable                     -> lookup


    mul_expr: mul_expr STAR mul_expr        -> mul
            | mul_expr DIVIDE mul_expr      -> div
            | INT_CONST                     -> num
            | variable                     -> lookup


    INT_CONST: NUMBER
    STR_CONST: NAME


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
    SEMICOLON: ";"
    DOT: "."
    BACKSLASH: "$"
   
    NODE: "node"
    DRAW: "draw"
    EDGE: "edge"
    AT: "at"
    IN: "in"
    FOREACH: "foreach"
    %import common.CNAME -> NAME
    %import common.INT -> NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""

parser = Lark(calc_grammar)

def run_mult_expr(t, dictionary = None):
    if t.data == 'mul':
        return run_mult_expr(t.children[0], dictionary)*run_mult_expr(t.children[2], dictionary)
    if t.data == 'div':
        numerator = run_mult_expr(t.children[0], dictionary)
        denominator = run_mult_expr(t.children[2], dictionary)
        if denominator == 0:
            raise SyntaxError('Divison by Zero: %s' % t.data)
        return numerator/denominator
    elif t.data == 'num':
        return (float)(t.children[0])
    elif t.data == 'lookup':
        key = str(t.children[0].children[1])
        if key not in dictionary:
            raise SyntaxError('key not found: %s' % key)
        else:
            return dictionary[key]
    else:
        raise SyntaxError('Unknown expression: %s' % t.data)

def run_add_expr(t, dictionary = None):
    if t.data == 'add':
        return run_add_expr(t.children[0], dictionary)+run_add_expr(t.children[2], dictionary)
    elif t.data == 'sub':
        return run_add_expr(t.children[0], dictionary)-run_add_expr(t.children[2], dictionary)
    elif t.data == 'expr2':
        return run_mult_expr(t.children[0], dictionary)
    elif t.data == 'lookup':
        key = str(t.children[0].children[1])
        if key not in dictionary:
            raise SyntaxError('key not found: %s' % key)
        else:
            return dictionary[key]
    else:
        raise SyntaxError('Unknown expression: %s' % t.data)


def run_node_loop(t, foreach_list):
    if foreach_list == []:
        return [run_node(t)]
    else:
        nodes = []
        for i in range(1, len(foreach_list[0])):
            dictionary = {}
            dictionary[foreach_list[0][0]] =  foreach_list[0][i]
            nodes.extend(process_loop(t, foreach_list, 1, dictionary))
        return nodes


def process_loop(t, foreach_list, loopnumber, dictionary):
    if loopnumber == len(foreach_list):
        return [run_node(t, dictionary)]
    else:
        print "loopnumber = ", loopnumber, "dictionary = ", dictionary
        nodes = []
        looprange = []

        if type(foreach_list[loopnumber][1]) != type("1") and type(foreach_list[loopnumber][-1]) != type("2"):
            looprange = foreach_list[loopnumber]

        else:
            start = end = 0
            if type(foreach_list[loopnumber][1]) == type("1"):
                start = dictionary[foreach_list[loopnumber][1]]
            else:
                start = foreach_list[loopnumber][1]

            if type(foreach_list[loopnumber][-1]) == type("1"):
                end = dictionary[foreach_list[loopnumber][-1]]
            else:
                end = foreach_list[loopnumber][-1]

            print start, end
            looprange = range(start, end + 1)

            print looprange

        for i in range(len(looprange)):
            dictionary[foreach_list[loopnumber][0]] = looprange[i]
            nodes.extend(process_loop(t, foreach_list, loopnumber + 1, dictionary))
        
        return nodes

def run_node(t, dictionary = None, position = (0,0)):
    global node_dictionary

    print dictionary
    pos = position
    attrs = Attributes()
    name = ""
    identity = ""
    for child in t.children:
        if child.data == "id":
            identity = str(child.children[1])

        elif child.data == 'pos':
            pos = (run_add_expr(child.children[2], dictionary), run_add_expr(child.children[4], dictionary))
        
        elif child.data == 'name':
            name = str(child.children[1])

        elif child.data == 'attrs':

            for i in range(1, len(child.children)-1,2):
                token = child.children[i]
                if token.data == "unnamed_attr":
                    val = str(' '.join(token.children))
                    attrs.addUnnamedAttribute(val)

                else:

                    key = str(' '.join(token.children[0:token.children.index('=')]))
                    
                    if token.data == 'num_attr':
                        val = token.children[token.children.index('=') + 1]
                        val = run_add_expr(val)
                    
                    elif token.data == 'str_attr':
                        val = str(' '.join(token.children[token.children.index('=') + 1:]))
                    
                    if key == "node contents":
                        name = val
                    else:
                        attrs.addNamedAttribute(key, val)
    
    new_node = Node(pos, attrs, name, identity)
    if identity != "":
        node_dictionary[identity] = new_node

    return new_node


def get_range(t):
    if t.data == "rangetype1":
        li = []
        first_node = t.children[0]
        if first_node.data == "var":
            li.append(str(first_node.children[0].children[1]))
        else:
            li.append(int(first_node.children[0]))

        last_node = t.children[-1]
        if last_node.data == "var":
            li.append(str(last_node.children[0].children[1]))
        else:
            li.append(int(last_node.children[0]))

        if type(li[0]) != type("a") and type(li[1]) != type("b"):
            li = range(li[0], li[1] + 1)

        return li

    elif t.data == "rangetype2":
        li = []
        for i in range(0, len(t.children), 2):
            li.append(int(t.children[i]))
        return li
    else:
        raise SyntaxError('Unknown rannge type: %s' % t.data)

def run_forloop(t):
    #update this step 
    variable = str(t.children[1].children[1])       
    loop_range = get_range(t.children[4])
    return [variable] + loop_range


def process_node_draw(t):
    if t.data == "typenode":
        position = (0, 0)

        try:
            position = (run_add_expr(t.children[0].children[1]), run_add_expr(t.children[0].children[3]))
        except Exception as e:
            pass
        
        return run_node(t.children[-1], position = position)

    elif t.data == "lookup":
        return node_dictionary[str(t.children[1])]

    else:
        raise SyntaxError('Unknown instruction: %s' % t.data)


def run_instruction(t):



    if t.data == "node_ins":

        foreach_list = []

        for i in range(1, len(t.children) - 1):
            foreach_list.append(run_forloop(t.children[i]))
        print foreach_list
        return run_node_loop(t.children[-1], foreach_list)

    elif t.data == "draw_ins":

        nodes = []
        edges = []

        for i in range(1, len(t.children)):
            print t.children[i].data
            if t.children[i].data != "edge_details":
                print "yes"
                nodes.append(process_node_draw(t.children[i]))

        

        for i in range(1, len(t.children)):
            if t.children[i].data == "edge_details":
                edges.append(source_node = nodes[i-1], dest_node = nodes[i+1])

        return nodes, edges
        
    else:
        raise SyntaxError('Unknown instruction: %s' % t.data)


def run_parser(program):
    instructions = []
    parse_tree = parser.parse(program)
    print (parse_tree.pretty(indent_str='  '))
    #exit()
    for i in range(1,len(parse_tree.children)-1,2):
        instruction = parse_tree.children[i]
        instruction.children.pop(0)
        instructions.extend( run_instruction(instruction))
    return instructions

def main():
    instructions = []
    code = input('> ').replace('\\', '$')
    print code
    try:
        instructions = run_parser(code)
    except Exception as e:
        print(e)
    return instructions


node_dictionary = {}

instructions = main()
for instruction in instructions:
    instruction.show()
