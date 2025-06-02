from .Coblex import lex, create_token
from .LL1ParsingTableMaker import process_grammar_file, EGrammarToken
from .LL1TokenDef import token_value, is_token_of_kind, token_line, _KINDS
class RecDParser:

    S = 0
    A = 1
    B = 2
    C = 3
    D = 4
    E = 5
    F = 6
    SYMBOL = _KINDS[2]
    def peek(self):
        return self.stack[len(self.stack)-1]
    def pop(self):
        return self.stack.pop()
    def add(self, el):
        self.stack.append(el)

    def __init__(self, tokens = []):
        self.tokens = tokens 
        self.current = None
        self.table = [
            {
                "ID": [self.fA, ".", "DIVISION", "ID"],
                "IDENTIFICATION": [self.fA, ".", "DIVISION", "IDENTIFICATION"]
            },
            {
                "PROGRAM-ID": [self.fH, self.fB, "PROGRAM-ID"]
            },
            {
                ".": ["."],
                self.SYMBOL: ""
            },
            {
                self.SYMBOL: ""
            }
        ]
        self.stack = ["$EOF$", self.source]
    def fH(self):
        print("expecting a user defined name")
        if is_token_of_kind(self.current, "SYMBOL"):
            print("success")
        else: print("fail")
    def fB(self):
        print("Parsing optional rule B")
        derivation = self.table[self.B].get(token_value(self.current), None)
        if derivation is None:
            print('error')
            return None
        print("Create . ast node")
        for tok in derivation:
            self.add(tok) 
    def fA(self):
        print("parsing A rule")
        derivation = self.table[self.A].get(token_value(self.current), None)
        if derivation is None:
            print('error')
            return None
        print("Create program id ast node")
        for tok in derivation:
            self.add(tok)
    def source(self):
        print("parsing source")
        derivation = self.table[self.S].get(token_value(self.current), None)
        if derivation is None:
            print('error')
            return None
        print("Create Cobol source program ast node")
        for tok in derivation:
            self.add(tok)
        

    def start(self):
        self.nextToken()
        while len(self.stack) > 0 and len(self.tokens) > 0 and token_value(self.current) != "$EOF$":
            peek = self.peek()
            if isinstance(peek, str):
                if peek == token_value(self.current):
                    res = self.pop()
                    self.nextToken()
                    print("Node create/append :", res)
                else:
                    print("error 2")
                    return
            else:
                parsing_function = self.pop()
                parsing_function()

    
         
    def nextToken(self):
        if len(self.tokens) > 0:
            self.current = self.tokens.pop(0)
        else:
            self.current = None

    def skipXtoken(self, x):
        for i in range(x):
            if i == x-1:
                self.nextToken()
            else:
                self.tokens.pop(0)

    def matchTokenWithAny(self, token, *others):
        for other in others:
            if other == token_value(token):
                self.nextToken()
                return True
        self.syntax_error(token, [el for el in others])
        return False
    
    def matchLookAheadWith(self, la_offset, other):
        return token_value(self.tokens[la_offset]) == other

    def syntax_error(self, token, expected):
        print("ERROR invalid token", token_value(token), "on line", token_line(token), f"expected any of [{ ','.join(expected) }]" )
        
    def Optional_dot(self):
        if token_value(self.current) == ".":
            self.nextToken()
    
    def program_id_cobol_source_program(self) :
        def Optional2():
            if Optional3() and not token_value(self.current) == "INITIAL":
                self.syntax_error(self.current, ["INITIAL"])
                return None
            self.nextToken()
    
            Optional4()
        def Optional3():
            if token_value(self.current) == "IS":
                self.nextToken()
                return True
            return False
        def Optional4():
            if token_value(self.current) == "PROGRAM":
                self.nextToken()

        ############ START ###################       
        # progid = ASTser.ProgramID()
        if not self.matchTokenWithAny(self.current, "PROGRAM-ID"):
            return None
        self.Optional_dot()
        if is_token_of_kind(self.current, "SYMBOL"):
            # progid.ID = token_value(self.current)
            self.nextToken()
        Optional2()
        self.Optional_dot()
        

    def cobol_source_program(self):
        self.nextToken()
        if not self.matchTokenWithAny(self.current, "ID", "IDENTIFICATION"):
            return
        if not self.matchTokenWithAny(self.current, "DIVISION"):
            return
        if not self.matchTokenWithAny(self.current, "."):
            return
        programid = self.program_id_cobol_source_program()
        if programid != None:
            print(programid.ID, programid.initial)
        
class LL1Parser:
    def __init__(self, tokens, start_rule_name="S"):
        tokens.append(create_token("$", 3, -1))
        self.inputs = tokens
        self.inputs_ptr = 0
        self.current_rule = ""
        self.userdef_map = {}
        self.current_usrdef_match = None
        self.starting_rule = start_rule_name
    
    def setup_userdef(self, func_map):
        for x in func_map:
            if not isinstance(func_map[x], tuple) or len(func_map[x]) != 2:
                print("Error: Map format is incorrect!\nMake sure each entry in the map is in this format Key:(function, priority)")
                print(f"Error occured on entry: {x}")
                exit(1)
        self.userdef_map = func_map
    
    def compute_lookup_table(self, grammar):
        self.parse_table = process_grammar_file(grammar,self.starting_rule)

    def compute_usrdefs(self):
        priority = 0
        if self.inputs_ptr > len(self.inputs)-1:
            return
        for userdef_key in self.userdef_map:
            userdef = self.userdef_map[userdef_key]
            res = userdef[0](self.get_input(), self.current_rule)
            if res and userdef[1] >= priority:
                self.current_usrdef_match = userdef_key
                priority = userdef[1]
                return
            self.current_usrdef_match = None

    def get_input(self):
        return self.inputs[self.inputs_ptr]
    def move_ptr_next(self):
        self.inputs_ptr += 1
        self.compute_usrdefs()

    def parse_terminal(self, production, current_token, is_delay_error_log=False):
        if production != token_value(current_token):
            if not is_delay_error_log:
                print(f"Error invalid terminal!\nExpected {production} but got {token_value(current_token)}")
            return False
        self.move_ptr_next()
        return True

    def parse_non_terminal(self, production, current_token, stack, is_delay_error_log=False):
        self.current_rule = production
        derivation = self.parse_table.get(self.current_rule, {}).get((EGrammarToken.TERMINAL, token_value(current_token)), False)
        if not derivation:
            derivation = self.parse_table.get(self.current_rule, {}).get((EGrammarToken.PUNCTUATION, token_value(current_token)), False)
            if not derivation:
                # derivation = self.parse_table.get(self.current_rule, {}).get(EGrammarToken.USRDEF, {}).get(self.current_usrdef_match, False)
                derivation = self.parse_table.get(self.current_rule, {}).get((EGrammarToken.USRDEF, self.current_usrdef_match), False)
                if not derivation:
                    if is_delay_error_log:
                        return False
                    print(f"Error in parsing token {token_value(current_token)} with rule {production}.\nThis rule cannot produce this token")
                    expected = self.parse_table.get(production, {})
                    msg = f"Expected any of these tokens: '{"','".join([e[1] for e in expected if e[0] != EGrammarToken.USRDEF])}'."
                    if entries:=[k[1] for k in expected if k[0] == EGrammarToken.USRDEF]:
                        msg +=  f"\nOr any of these user defined conditions entry: '{"','".join(entries)}'."
                    print(msg)
                    return False
        for el in derivation[::-1]:
            stack.append(el)
        return True
    
    def start(self):

        def sort_any_order_element(element):
            return isinstance(element[1], str) and "optional_" in str(element[1]) and str(element[1]).split("_")[-1].isdigit()

        stack = [(EGrammarToken.PUNCTUATION, "$"), (EGrammarToken.NON_TERMINAL, self.starting_rule)]
        parse_token_map = {
            EGrammarToken.NON_TERMINAL: self.parse_non_terminal,
            EGrammarToken.TERMINAL: self.parse_terminal
        }
        self.compute_usrdefs()
        while stack and self.inputs_ptr <= len(self.inputs):
            current_production = stack.pop()
            current_token = self.get_input()
            match current_production[0]:
                case EGrammarToken.TERMINAL | EGrammarToken.PUNCTUATION:
                    if not self.parse_terminal(current_production[1], current_token):
                        return False
                    continue
                case EGrammarToken.NON_TERMINAL:
                    if not self.parse_non_terminal(current_production[1], current_token, stack):
                        return False
                    continue
                case EGrammarToken.EPSILON:
                    continue
                case EGrammarToken.USRDEF:
                    if self.current_usrdef_match != None:
                        self.move_ptr_next()
                    else:
                        #shouldnt be able to reach there, as the current match will have already been evaluated before reaching the usrdef rule
                        print(f"Error: User definied behaviour '{current_production[1]}' isn't valid for current token: {token_value(current_token)} !")
                        return False
                    continue
                case EGrammarToken.ANY_ORDER:
                    any_array = [x for x in current_production[1]]
                    any_array_firsts = [x for x in any_array]
                    # put optionals at the end of array as their priority are less than any other element
                    any_array_firsts.sort(key=sort_any_order_element)
                    i = 0
                    eps_ctr = 0
                    while True:
                        if i >= len(any_array):
                            expected = []
                            for e in any_array_firsts:
                                expected += self.parse_table.get(e[1], {}).keys()
                            print(f"Expected any of '{"','".join(set([x[1] for x in expected]))}'.")
                            return False
                        if any_array_firsts[i][0] == EGrammarToken.TERMINAL or any_array_firsts[i][0] == EGrammarToken.NON_TERMINAL:
                            derivation_result = []
                            if parse_token_map.get(any_array_firsts[i][0])(any_array_firsts[i][1], current_token, derivation_result, len(any_array) > 1):
                                # if any array have still possible path to explore next, add them back on the stack
                                if len(any_array) > 1:
                                    if (len(derivation_result) > 1 or derivation_result[0] != (EGrammarToken.EPSILON, None)) or eps_ctr >= len(any_array)-1:
                                        stack.append((EGrammarToken.ANY_ORDER, any_array[0:i] + any_array[i+1:]))
                                    else:
                                        eps_ctr += 1
                                        i+=1
                                        continue
                                #special treatment to add the full array of the group instead of just its first element. It will then be unpacked next iteration
                                if any_array[i][0] == EGrammarToken.GROUP:
                                    stack.append(any_array[i])
                                #Finally add the current matching derivation to the stack to be parsed
                                else:
                                    stack = stack + derivation_result
                                break
                        else:
                            #Get first non terminal / terminal from group or other special rule, keep the resort the array
                            any_array_firsts[i] = any_array_firsts[i][1][0]
                            any_array_firsts.sort(key=sort_any_order_element)
                            continue
                        i += 1            
                case _:
                    for element in current_production[1][::-1]:
                        stack.append(element)
        print("PARSING ENDED SUCCESSFULLY !")
        return True




def main():
    
    in_path = r'./src/parsing/EBSGINA1.cbl'
    in_test = r'./src/parsing/test.txt'
    tokens = lex(in_path)
    # parser  = RecDParser(tokens)
    parser = LL1Parser(tokens, "cobol_source_program")
    userdef = {
        _KINDS[2]: (lambda x,_: is_token_of_kind(x, _KINDS[2]), 0),
        _KINDS[5]: (lambda x,_: is_token_of_kind(x, _KINDS[5]), 0),
        "PNUMBER": (lambda x,_: len(token_value(x)) > 2 and (token_value(x)[0].isdigit() and (len(token_value(x)) < 2 ) or token_value(x)[1].isdigit()), 0)
        }
    parser.setup_userdef(userdef)
    parser.compute_lookup_table(r"./src/grammar_cobol.conf")
    parser.start()

    

if __name__ == "__main__":
    main()