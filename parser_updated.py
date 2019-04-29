# yellow!80
# variable get range 
# make changes here for which nodes the edge belongs to
# find a name for rangetype1

try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass


from class_objects import *

from lark import Lark
import math


#how to write grammar for node_draw (conflict issues)

calc_grammar = """    start: (BACKSLASH TIKZ)? LBRACE (instruction SEMICOLON)+ RBRACE

    instruction: BACKSLASH NODE for_each* node_prop                     -> node_ins
                |BACKSLASH DRAW node_draw (edge_details? node_draw)*    -> draw_ins
                |(BACKSLASH for_each)* instruction                         -> loop_ins

    node_draw:    position? NODE node_prop              -> newnode
                | LPARAN STR_CONST RPARAN               -> lookup
                | LPARAN variable RPARAN                -> variable



    edge_details: EDGE edge_attrs?

    edge_attrs: LBOX shape RBOX

    shape: LARROW
            | RARROW
            | DASH

    for_each: FOREACH variables IN LBRACE range RBRACE

    variable: BACKSLASH STR_CONST
    variables: variable (SLASH variable)*


    range: numvar COMMA DOT DOT DOT COMMA numvar        -> rangetype1 
            | numvar (COMMA numvar)*                        -> discrete

    numvar: expr                                        -> number
            | variables                                 -> var
            | values                                    -> vals

    values: STR_CONST (SLASH STR_CONST)*

    node_prop: id? pos? attrs? name?

    id: LPARAN STR_CONST RPARAN                        

    pos: AT position

    position: LPARAN expr UNIT? COMMA expr UNIT? RPARAN             -> cartesian
            | LPARAN expr UNIT? COLON expr UNIT? RPARAN             -> polar

    attrs: LBOX attr (COMMA attr)* RBOX
    
    attr: STR_CONST+                         -> unnamed_attr
        | STR_CONST+ EQUALS STR_CONST+       -> str_attr
        | STR_CONST+ EQUALS expr             -> num_attr
        | FILL EQUALS STR_CONST EXCLAMATION expr -> fill
    
    name: LBRACE alphanum RBRACE

    LCASE_LETTER: "a".."z"
    UCASE_LETTER: "A".."Z"
    DIGIT: "0".."9"

    LETTER: UCASE_LETTER | LCASE_LETTER

    alphanum: ("_"|LETTER|DIGIT)+

    expr:   expr PLUS expr                  -> add
            | expr SUB expr                 -> sub
            | mul_expr                      -> expr2


    mul_expr: mul_expr STAR mul_expr        -> mul
            | mul_expr DIVIDE mul_expr      -> div
            | INT_CONST                     -> num
            | variable                      -> lookup


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
    LARROW: "<-"
    RARROW: "->"
    DASH: SUB
    COLON: ":"
    SLASH: "/"
    EXCLAMATION: "!"
    UNIT: "cm" | "m"
   
    NODE: "node"
    DRAW: "draw"
    EDGE: "edge"
    AT: "at"
    IN: "in"
    FOREACH: "foreach"
    FILL : "fill"
    TIKZ:"tikz"
    %import common.ESCAPED_STRING   -> STRING
    %import common.CNAME -> NAME
    %import common.INT -> NUMBER
    %import common.WS
    %import common.NEWLINE
    %ignore WS
    %ignore NEWLINE
"""

parser = Lark(calc_grammar)

def process_mult_expr(t, dictionary = None):
    if t.data == 'mul':
        return process_mult_expr(t.children[0], dictionary)*process_mult_expr(t.children[2], dictionary)
    if t.data == 'div':
        numerator = process_mult_expr(t.children[0], dictionary)
        denominator = process_mult_expr(t.children[2], dictionary)
        if denominator == 0:
            raise SyntaxError('Divison by Zero: %s' % t.data)
        return numerator/denominator
    elif t.data == 'num':
        return (float)(t.children[0])
    elif t.data == 'lookup':
        var_name = str(t.children[0].children[1])
        if var_name in dictionary:
            return dictionary[var_name]
        else:
            raise SyntaxError('Variable not found: %s' % var_name)
    else:
        raise SyntaxError('Unknown expression: %s' % t.data)


def process_add_expr(t, dictionary = None):
    if t.data == 'add':
        return process_add_expr(t.children[0], dictionary)+process_add_expr(t.children[2], dictionary)
    elif t.data == 'sub':
        return process_add_expr(t.children[0], dictionary)-process_add_expr(t.children[2], dictionary)
    elif t.data == 'expr2':
        return process_mult_expr(t.children[0], dictionary)
    else:
        raise SyntaxError('Unknown expression: %s' % t.data)


def process_loop(t, foreach_list, loopnumber, dictionary, ins = False):
    if loopnumber == len(foreach_list):
        if not ins:
            return [generate_node(t, dictionary)]
        else:
            if t.children[0] == "$":
                t.children.pop(0)
            process_instruction(t, dictionary)
    else:
        nodes = []
        looprange = []

        start_range = foreach_list[loopnumber][1]
        end_range = foreach_list[loopnumber][-2]
        
        if type(start_range) == "str":
            start_range = dictionary[start_range]

        if type(end_range) == "str":
            end_range = dictionary[end_range]

        looprange = range((int)(start_range), (int)(end_range) + 1)
        # print start_range, end_range
        # print looprange

        for i in range(len(looprange)):
            dictionary[foreach_list[loopnumber][0]] = looprange[i]
            if not ins:
                nodes.extend(process_loop(t, foreach_list, loopnumber + 1, dictionary))
            else:
                process_loop(t, foreach_list, loopnumber + 1, dictionary)

        return nodes

def process_alphanum(t):
    output = ""
    for children in t.children:
        output+=(str)(children)
    return output
    
def generate_node(t, dictionary = None, position = (0,0)):
    global count
    pos = position
    attrs = Attributes()
    name = ""
    identity = ""

    for child in t.children:
        if child.data == "id":
            identity = str(child.children[1])

        elif child.data == 'pos':
            #pos = (process_add_expr(child.children[2], dictionary), process_add_expr(child.children[4], dictionary))
            position = child.children[1]
            expr1 = position.children[1]
            for  i in range(3,min(6, len(position.children))):
                if token.children[i].data == 'expr':
                    expr2 = token.children[i]

            x, y = process_add_expr(expr1, dictionary), process_add_expr(expr2, dictionary)  

            if position.data == "polar":
                theta =  (x * math.pi) / 180.0
                x, y = y * math.cos(theta), y * math.sin(theta)

            pos = (x, y)
        
        elif child.data == 'name':
            name = str(process_alphanum(child.children[1]))

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
                        val = process_add_expr(val, dictionary)
                    
                    elif token.data == 'str_attr':
                        val = str(' '.join(token.children[token.children.index('=') + 1:]))
                    elif token.data == 'fill':
                        attrs.addNamedAttribute('fill',str(token.children[2]))
                        attrs.addNamedAttribute('intensity',process_add_expr(token.children[4], dictionary))
                        continue

                    
                    if key == "node contents":
                        name = val
                    else:
                        attrs.addNamedAttribute(key, val)
    if identity == "":
        identity = "default"+str(count)
        count += 1

    new_node = Node(pos, attrs, name, identity)

    if identity != "":
        node_dictionary[identity] = new_node

    return new_node


def process_foreach(t, foreach_list):
    nodes = []
    print foreach_list

    first_loop = foreach_list[0]
    loop_vars = first_loop[0]
    if first_loop[-1] == 'range':
        values = range((int)(first_loop[1]), (int)(first_loop[2])+1)
    else:
        values = first_loop[1:-1]


    for value in values:
        dictionary = {}

        i = 0
        for loop_var in loop_vars:
            try:
                dictionary[loop_var] = value[i]
            except Exception as e:
                dictionary[loop_var] = value
            i += 1

        if t.data == "loop_ins":
            process_loop(t.children[-1], foreach_list, 1, dictionary, ins=True)
        else:
            nodes.extend(process_loop(t, foreach_list, 1, dictionary))
    
    return nodes


def get_range(t):
    if t.data == "rangetype1":
        values = []
        # range: numvar COMMA DOT DOT DOT COMMA numvar
        start_range = t.children[0]

        if start_range.data == "var":

            # numvar = variable
            variable = start_range.children[0]

            # variable = BACKSLASH var_name
            values.append(str(variable.children[1]))

        elif start_range.data == "number":
            values.append(process_add_expr(start_range.children[0]))
        else:
            raise SyntaxError('Unknown rannge type: %s' % start_range.data) 

        end_range = t.children[-1]
        if end_range.data == "var":

            # numvar = variable
            variable = end_range.children[0]

            # variable = BACKSLASH var_name
            values.append(str(variable.children[1]))
        elif end_range.data == "number":
            values.append(process_add_expr(end_range.children[0]))
        else:
            raise SyntaxError('Unknown rannge type: %s' % end_range.data)

        return values, "range"

    elif t.data == "discrete":
        #t = numvar (COMMA numvar)*
        values = []

        # discrete_range = num (COMMA num)*
        for i in range(0, len(t.children), 2):
            if t.children[i].data == "number":
                values.append(process_add_expr(t.children[i].children[0]))
            elif t.children[i].data == "vals":
                values.append(getValues(t.children[i].children[0]))

        return values, "discrete"
    else:
        raise SyntaxError('Unknown range type: %s' % t.data)    


def process_node_instruction(t, dictionary = None):

    # NODE for_each* node_prop

    foreach_list = []

    # node_ins = NODE foreach* node_props
    for i in range(1, len(t.children) - 1):
        foreach_ins = t.children[i]

        # foreach_ins = FOREACH variable IN LBRACE range RBRACE
        variables = foreach_ins.children[1]
        
        # variables : variable (SLASH variable)*
        var_name = getVariables(variables)[0]

        loop_range, range_type = get_range(foreach_ins.children[4])
        # foreach_list.append([var_name] + loop_range )
        foreach_list.append([var_name] + loop_range + [range_type])

    if foreach_list == []:
        return [generate_node(t.children[1], dictionary)]
    else:
        return process_foreach(t.children[-1], foreach_list)

"""
Input : The Subtree of one instruction
Output: -
Action:
    1) Parses which type of instruction it is. 
    2) Updates the list of nodes and edges.
"""
def process_instruction(t, dictionary = None):
    global graph_nodes, graph_edges
    if t.data == "node_ins":
        graph_nodes.extend(process_node_instruction(t, dictionary))

    elif t.data == "draw_ins":

        node_ids = []
        for i in range(1, len(t.children)):
            if t.children[i].data != "edge_details":
                node_draw = t.children[i]

                identity = ""
                if node_draw.data == "newnode":
                    if node_draw.children[0].data in ["polar", "cartesian"]:
                        position = node_draw.children[0]
                        x = process_add_expr(position.children[1])
                        y = process_add_expr(position.children[3])

                        if position.data == "polar":
                            theta =  (x * math.pi) / 180.0
                            x, y = y * math.cos(theta), y * math.sin(theta)

                        graph_nodes.append(generate_node(node_draw.children[2], position = (x,y) ))
                       
                    else:
                        graph_nodes.extend(generate_node(node_draw.children[1]))
                    identity = graph_nodes[-1].id
                
                elif node_draw.data == "lookup":
                    identity = node_draw.children[1]

                elif node_draw.data == "variable":
                    identity = dictionary[node_draw.children[1].children[1]]

                # t.children[i] = identity
                node_ids.append(identity)
            else:
                node_ids.append(None)

        for i in range(1, len(t.children)):
            # print type(t.children[i])
            # continue
            if t.children[i].data == "edge_details":

                edge_details = t.children[i]
                edge_type = 0
                if len(edge_details.children)>1:
                    edge_attr = edge_details.children[1]

                    if edge_attr.children[1] == "LARROW":
                        edge_type = -1
                    elif edge_attr.children[1] == "RARROW":
                        edge_type = 1
                
                source = node_ids[i-2]
                destination = node_ids[i]

                if edge_type ==-1:
                    graph_edges.append(Edge(destination, source, edge_type))
                else:
                    graph_edges.append(Edge(source, destination, edge_type))  

    #t.children = (backslash foreach)*
    #foreach = foreach variables in { range }
    elif t.data == "loop_ins":

        foreach_list = []
        for i in range(0, len(t.children) - 1, 2):
            foreach_ins = t.children[i]

            variable = foreach_ins.children[1]
            var_names = getVariables(variable)
            loop_range, range_type = get_range(foreach_ins.children[4])
            foreach_list.append([var_names] + loop_range + [range_type])


        process_foreach(t, foreach_list)

    else:
        raise SyntaxError('Unknown instruction: %s' % t.data)

"""
Input : The code that has been provided as input by the user
Output: -
Action:
    1) Generates a Parse tree for the input code. 
    2) Executes each instruction and updates the list of nodes and edges.
"""
def run_parser(program):
    parse_tree = parser.parse(program)
    # print (parse_tree.pretty(indent_str='  '))
    # exit()

    # code = LBRACE (instruction SEMICOLON)+ RBRACE
    for i in range(1, len(parse_tree.children)-1, 2):
        instruction = parse_tree.children[i]

        # Removing BackSlash
        instruction.children.pop(0)
        process_instruction(instruction)


"""
Input : -
Output: -
Action:
    1) Takes input from the user
    2) Replaces Backslash with Dollar (Temporary)
    3) Runs the parser
"""
def main():
    # Not able to parse '//' at the moment
    code = input().replace('\\', '$')
    try:
        run_parser(code)
    except Exception as e:
        print(e)


def export():
    output = { "Nodes": graph_nodes, "Edges": graph_edges}
    return output

def reset():
    global graph_edges, graph_nodes, node_dictionary
    node_dictionary = {}
    graph_edges = []
    graph_nodes = []


def getVariables(t):
    #t = variable (SLASH variable)*
    variables = []
    for i in range(0, len(t.children), 2):
        variables.append(str(t.children[i].children[1]))
    return variables


def getValues(t):
    values = []
    for i in range(0, len(t.children), 2):
        values.append(str(t.children[i]))
    return values

node_dictionary = {}
graph_edges = []
graph_nodes = []
count = 0

if __name__ == '__main__':
    main()
    output = { "Nodes": graph_nodes, "Edges": graph_edges}
    import json
    print json.dumps(output, default=lambda o: o.__dict__)
    # for node in graph_nodes:
    #     # node.show()
    #     print node.toJSON()
    # print "\n\nEdges"
    # for edge in graph_edges:
    #     print edge.toJSON()
