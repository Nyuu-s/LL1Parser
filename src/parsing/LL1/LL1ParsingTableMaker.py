from enum import Enum
import copy

class EGrammarToken(int, Enum):
    TERMINAL = 0
    NON_TERMINAL = 1
    RULE_NAME = 2
    PUNCTUATION = 3
    GROUP = 4
    OPTIONAL = 5
    ANY_ORDER = 6
    XOR = 7
    EPSILON = 8
    REPETITION = 9
    REP_MODE = 10
    USRDEF=11

def debug_print_firsts(map):
    import re
    s = re.sub(r"\<(.*?):\s+\d+\>", r"\1", str(map))
    print(s)
    
    

# use this to cross confirm that you got all rules at the end
def get_rulenames(content:str, indexes):
    flag = False
    names = []
    current = ""
    for cursor in indexes:
        while cursor > 0 and cursor <= len(content):
            cursor -= 1
            if content[cursor].isalnum() or content[cursor] == "-":
                current += content[cursor]
                flag = True
            else:
                if flag:
                    break
        names.append(current[-1::-1])
        current = ""
        flag = False
    return names

def tokenize(content:str):    
    punct_list = ["|", "[", "(", ")", "]" , "{", "}", "*", "+"]
    tokens = []
    fp = 0
    token = ""
    while fp < len(content):
        if content[fp] == " ":
            fp += 1
            continue
        
        if content[fp] == '"':
            fp += 1 #skip quote
            while fp < len(content) and (content[fp].isalnum() or content[fp].isascii()) and not content[fp] == '"':
                token += content[fp]
                fp += 1
            fp += 1
            tokens.append((EGrammarToken.TERMINAL, token))
            token = ""
            continue
        
        if content[fp].isalnum():
            while fp < len(content) and (content[fp].isalnum() or content[fp] == "-"):
                token += content[fp]
                fp += 1
            tokens.append((EGrammarToken.NON_TERMINAL, token))
            token = ""
            continue
        if content[fp] == "=":
            prev = tokens.pop()
            tokens.append((EGrammarToken.RULE_NAME, prev[1]))
            fp += 1
            if fp > 0 and content[fp-2] == "?":
                while fp < len(content) and content[fp].isspace():
                    fp+=1
                while fp < len(content) and content[fp].isalnum():
                    token += content[fp]
                    fp += 1
                tokens.append((EGrammarToken.USRDEF, token))
                token = ""
            continue
            
        
        if content[fp] in punct_list:
            while fp < len(content) and content[fp] in punct_list:
                token += content[fp]
                fp += 1
                if fp < len(content) and content[fp] != "|":
                    break
            tokens.append((EGrammarToken.PUNCTUATION, token))
            token = "" 
            continue
        fp += 1
    tokens.append((EGrammarToken.PUNCTUATION, "@EOF@"))
    return tokens


def build_neighbours_set(rule_name, rule_content): 
    rule_content.append((EGrammarToken.PUNCTUATION, "$"))
    main_stack = [(rule_name, rule_content)]
    pair_stack = []
    bottom_pointer = 0
    follows = set() # TODO: change this to a dict directly here to avoid building it in build_follow_set from NEIGHBOURS
    # FIRST PHASE FILL PAIR STACK BY PROCESSING ALL RECURSIVE STRUCTURES
    while main_stack:
        node = main_stack.pop()
        # Case when right most item is the result of a xor i.e [A, B]
        if isinstance(node, list):
            if len(pair_stack) > bottom_pointer:
                next = pair_stack.pop()
                next = [next] if not isinstance(next, list) else next
                for cur_el in node:
                    for nex_el in next:
                        follows.add((cur_el, nex_el))
            pair_stack.append(node)
            continue
        
        match node[0]:
            case EGrammarToken.NON_TERMINAL | EGrammarToken.TERMINAL | EGrammarToken.PUNCTUATION | EGrammarToken.USRDEF:
                if len(pair_stack) > bottom_pointer:
                    next = pair_stack.pop()
                    next = [next] if not isinstance(next, list) else next
                    for nex_el in next:
                        follows.add((node, nex_el))
                pair_stack.append(node)
                continue
            case EGrammarToken.XOR:
                main_stack.append(("END XOR", 0))
                main_stack.append(("XOR BRA", -1))
                main_stack.append(node[1][0])
                main_stack.append(pair_stack[len(pair_stack)-1])
                main_stack.append(("XOR BRA", 1))
                main_stack.append(node[1][1])
            case EGrammarToken.ANY_ORDER:
                # Add for each token in any_order array all order possibility within the array + the last case
                # [A, B, C] E => for A, it can be A then B or A then C + the case where A is at the end so A then E
                # return the array of all the left element possible so here [A,B,C] to bind with what is on the left of any order if there is something
                # Not optimal for groups as they will be placed mutiple times on the stack for each possibility and it will re-traverse them fully each time
                # not an issue because the final result is a set so no duplicate pairs but could be optimized in the future
                right_most = pair_stack[len(pair_stack)-1]
                main_stack.append(("END ANY", len(node[1])))
                for i,current in enumerate(node[1]):
                    for other in node[1][:i] + node[1][i+1:]:
                        main_stack.append(("ANY OPT", 0))
                        main_stack.append(current)
                        main_stack.append(other)
                    main_stack.append(("ANY OPT", 0))
                    main_stack.append(current)
                    if i != len(node[1])-1:
                        main_stack.append(right_most)
                
            case "ANY OPT":
                bottom_pointer += 1
            case "END ANY":
                i = node[1]
                arr = []
                while len(arr) < i:
                    current = pair_stack.pop()
                    bottom_pointer -= 1
                    # remove all duplicate possibilities of an element of the pair stack, if any is [ A, B, C], at end pair stack will be AAABBBCCC
                    while pair_stack and current == pair_stack[len(pair_stack)-1]:
                        pair_stack.pop()
                        bottom_pointer -= 1
                    arr.append(current)
                main_stack.append(arr)
                
            case "XOR BRA":
                bottom_pointer += node[1]
            case "END XOR":
                cur = pair_stack.pop()
                cur = [cur] if not isinstance(cur, list) else cur
                next = pair_stack.pop()
                next = [next] if not isinstance(next, list) else next
                merge = cur + next
                pair_stack.append(merge)
            case _:
                for x in node[1]:
                    main_stack.append(x)
    # At end
    if len(pair_stack) != 1:
        print("Something went wrong during initial firsts follows computation")
        exit(1)
    return follows
        
def build_nt_occurences(rules_map):
    stack = []
    nt_occ = {}
    for rule in rules_map:
        for x in rules_map[rule]:
            stack.append(x)
        while stack:
            current = stack.pop()
            match current[0]:
                case EGrammarToken.NON_TERMINAL:
                    nt_occ.setdefault(current[1], set()).add(rule)
                case EGrammarToken.GROUP | EGrammarToken.ANY_ORDER | EGrammarToken.XOR | EGrammarToken.OPTIONAL:
                    for x in current[1]:
                        stack.append(x)
    return nt_occ

#COBOL grammar parsing
def parse_grammar(tokens):
    BINARY_OPERATORS = [EGrammarToken.ANY_ORDER, EGrammarToken.XOR]
    TOKEN_COUNTERS = [0 for _ in range(len(EGrammarToken._member_names_))] # count each token type per rule
    NEIGHBOURS = {}
    terminal_set = set()
    rules_map = {} #Output map of rules (name, content)
    stack = [] # Handle recursive thingies like (), [], and so on
    opt_stack = [] # Track optinals ID in a given rule to add the content to the correect subrule
    rep_stack = [] # Track repetitions subrules recursion
    def prepare_stack():
        # Behaviour when new rule detected / EOF
        if len(stack) <= 0:
            return
        for _ in range(1,len(stack)):
            stack[0][1].append(stack.pop(1))
        prev_rule = stack.pop()
        TOKEN_COUNTERS[EGrammarToken.NON_TERMINAL.value] = 0
        NEIGHBOURS[prev_rule[0]] = build_neighbours_set(prev_rule[0], prev_rule[1])
        
    def process_terminal_and_non_terminals():
        # common behaviours for terminals & non terminals
        # ended up with only one thing lol top notch reseuability   
        stack.append(tokTup)
    
    def process_punctuation(PUNCT:EGrammarToken):
        # Common behaviour for ending recursive punctuations
        tmp = []
        while len(stack) > 1:
            if stack[len(stack)-1][0] == PUNCT and len(stack[len(stack)-1][1]) <= 0: # pop stack until optional which is empty encountered
                break
            tmp.append(stack.pop())
        for x in tmp[-1::-1]:
            stack[len(stack)-1][1].append(x)
    on_the_right_of_binary_op = False
    has_optionals = False
    punct_context = []
    for tokTup in tokens:
        tokenType, tokenVal = tokTup
        if not on_the_right_of_binary_op and punct_context and punct_context[len(punct_context)-1] == EGrammarToken.ANY_ORDER:
            if len(stack[len(stack)-1][1]) > 1 and tokTup not in [(EGrammarToken.PUNCTUATION, "||"), (EGrammarToken.PUNCTUATION, '*'), (EGrammarToken.PUNCTUATION, '+') ]:
                punct_context.pop()
                subrule = f"{current_rule}_anyorder_{TOKEN_COUNTERS[EGrammarToken.ANY_ORDER.value]}"
                rules_map[subrule] = [stack.pop()]
                stack.append((EGrammarToken.NON_TERMINAL, subrule))
                NEIGHBOURS[subrule] = build_neighbours_set(subrule, rules_map[subrule])
        match tokenType:
            case EGrammarToken.RULE_NAME: 
                # print("Rule name: \t", tokenVal)
                prepare_stack()
                current_rule = tokenVal
                TOKEN_COUNTERS[EGrammarToken.OPTIONAL.value] = 0
                TOKEN_COUNTERS[EGrammarToken.XOR.value] = 0
                TOKEN_COUNTERS[EGrammarToken.ANY_ORDER.value] = 0
                if current_rule in rules_map.keys():
                    print(f"ERROR: {current_rule} is defined more than once !")
                    print(f"Overriding rules is not allowed in this version !")
                    exit(1)
                rules_map[current_rule] = []
                stack.append((current_rule, rules_map[current_rule]))
                continue

            case EGrammarToken.TERMINAL: 
                # print("Terminal: \t", tokenVal)
                if tokenVal not in terminal_set:
                    TOKEN_COUNTERS[EGrammarToken.TERMINAL.value] += 1
                    terminal_set.add(tokenVal)
                process_terminal_and_non_terminals()

            case EGrammarToken.NON_TERMINAL: 
                # print("Non-terminal: \t", tokenVal)
                TOKEN_COUNTERS[EGrammarToken.NON_TERMINAL.value] += 1
                process_terminal_and_non_terminals()
            case EGrammarToken.USRDEF:
                # FIRSTS[current_rule] = [tokTup]
                process_terminal_and_non_terminals()
            case EGrammarToken.PUNCTUATION: 
                # print("Punctuation: \t", tokenVal)
                match tokenVal:
                    case "(": 
                        stack.append((EGrammarToken.GROUP, []))
                        continue
                    case "[":
                        has_optionals = True
                        punct_context.append(EGrammarToken.OPTIONAL)
                        # create a subrule rulename_optional_X to add to rule_map
                        # in the current rule parsed, add (EgrammarToken.non_terminal, subrule_name)
                        TOKEN_COUNTERS[EGrammarToken.OPTIONAL.value] += 1
                        opt_stack.append(TOKEN_COUNTERS[EGrammarToken.OPTIONAL.value])
                        rules_map[f"{current_rule}_optional_{TOKEN_COUNTERS[EGrammarToken.OPTIONAL.value]}"] = []

                        stack.append((EGrammarToken.NON_TERMINAL, f"{current_rule}_optional_{TOKEN_COUNTERS[EGrammarToken.OPTIONAL.value]}"))
                        stack.append((EGrammarToken.OPTIONAL, []))
                        continue
                        
                    case "{":
                        has_optionals = True
                        punct_context.append(EGrammarToken.REPETITION)
                        TOKEN_COUNTERS[EGrammarToken.REPETITION.value] += 1
                        rep_stack.append(TOKEN_COUNTERS[EGrammarToken.REPETITION.value])
                        rules_map[f"{current_rule}_repetition_{TOKEN_COUNTERS[EGrammarToken.REPETITION.value]}"] = []
                        stack.append((EGrammarToken.NON_TERMINAL, f"{current_rule}_repetition_{TOKEN_COUNTERS[EGrammarToken.REPETITION.value]}"))
                        stack.append((EGrammarToken.REPETITION, []))
                        continue

                    case "|": 
                        stack.append((EGrammarToken.XOR, [stack.pop()]))
                        continue

                    case "||":
                        if stack[len(stack)-1][0] != EGrammarToken.ANY_ORDER:
                            punct_context.append(EGrammarToken.ANY_ORDER)
                            TOKEN_COUNTERS[EGrammarToken.ANY_ORDER.value] += 1
                            stack.append((EGrammarToken.ANY_ORDER, [stack.pop()]))
                            subrule = f"{current_rule}_anyorder_{TOKEN_COUNTERS[EGrammarToken.ANY_ORDER.value]}"
                        else:
                            on_the_right_of_binary_op = True
                        continue

                    case ")": 
                        process_punctuation(EGrammarToken.GROUP)

                    case "]": 
                        process_punctuation(EGrammarToken.OPTIONAL)
                        punct_context.pop()
                        # Add the whole content of the optional to the correct sub rule
                        subrule = f"{current_rule}_optional_{opt_stack.pop()}"
                        rules_map[subrule].append(stack.pop())
                        # FIRSTS[subrule] = find_firsts((subrule, rules_map[subrule]))
                        NEIGHBOURS[subrule] = build_neighbours_set(subrule, rules_map[subrule])
                    case "}":
                        process_punctuation(EGrammarToken.REPETITION)
                        punct_context.pop()
                        subrule = f"{current_rule}_repetition_{rep_stack.pop()}"
                        rules_map[subrule].append(stack.pop())
                        continue
                    case "*":
                        # Replace rule with [ Rep-rule-content Rep-rule-self-name ]
                        # S = A B --> S = [ A B S ]
                        ref_rep_rule = stack[len(stack)-1]
                        opt_name =  f"{ref_rep_rule[1]}_optional_{TOKEN_COUNTERS[EGrammarToken.OPTIONAL.value]+1}"
                        opt = (EGrammarToken.NON_TERMINAL,opt_name)
                        rep_content = rules_map[ref_rep_rule[1]].pop(0)[1]
                        rules_map[ref_rep_rule[1]] = [opt]
                        rules_map[opt_name] = [(EGrammarToken.OPTIONAL, [*rep_content, opt])]
                        NEIGHBOURS[ref_rep_rule[1]]  =   build_neighbours_set(ref_rep_rule[1], rules_map[ref_rep_rule[1]])
                        NEIGHBOURS[opt_name]         =   build_neighbours_set(opt_name, rules_map[opt_name])
                      
                    case "+":
                         # Replace rule with Rep-rule-content [Rep-rule-self-name]
                         # S = A B --> S = A B [ S ]
                        ref_rep_rule = stack[len(stack)-1]
                        opt_name =  f"{ref_rep_rule[1]}_optional_{TOKEN_COUNTERS[EGrammarToken.OPTIONAL.value]+1}"
                        opt = (EGrammarToken.NON_TERMINAL,opt_name)
                        rules_map[ref_rep_rule[1]] = [*rules_map[ref_rep_rule[1]].pop(0)[1], opt]
                        rules_map[opt_name] = [(EGrammarToken.OPTIONAL, [(ref_rep_rule)])]
                        NEIGHBOURS[ref_rep_rule[1]]  =   build_neighbours_set(ref_rep_rule[1], rules_map[ref_rep_rule[1]])
                        NEIGHBOURS[opt_name]         =   build_neighbours_set(opt_name, rules_map[opt_name])
                    case "@EOF@":
                        prepare_stack()
                        break
                    
        
        # Add right part of Binary op to its parent
        if stack[len(stack)-2][0] in BINARY_OPERATORS and (len(stack[len(stack)-2][1]) < 2 or on_the_right_of_binary_op):
            stack[len(stack)-2][1].append(stack.pop())
            on_the_right_of_binary_op = False

            # Step 1
            #     Create a subrule rulename_choice_X add to rule map
            #     in the current rule parsed, add (non_terminal, subrule_name)
            # Step 2
            #     Add subrule to final rule map and
            #     replace previous xor with sub rule in the stack
            # Step 3
            #     Set non terminal occurences so current rule refer to subrule
            #     finally Process first of new subrule
            if stack[len(stack)-1][0] == EGrammarToken.XOR:
                TOKEN_COUNTERS[EGrammarToken.XOR.value] += 1
                subrule = f"{current_rule}_choice_{TOKEN_COUNTERS[EGrammarToken.XOR.value]}"
                
                rules_map[subrule] = [stack.pop()]
                stack.append((EGrammarToken.NON_TERMINAL, subrule))
                NEIGHBOURS[subrule] = build_neighbours_set(subrule, rules_map[subrule])
    
    return (rules_map,  NEIGHBOURS, has_optionals )

def dict_diff(dict1:dict, dict2:dict):
    if dict1 == dict2:
        return
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    common = keys1 & keys2

    only1 = keys1 - keys2
    only2 = keys2 - keys1
    
    for key in only1:
        print(f"Key {key} only in dict1:  {dict1:[key]}")

    for key in only2:
        print(f"Key {key} only in dict2:  {dict1:[key]}")

    for key in common:
        if dict1[key] != dict2[key]:
            print(f"Key {key} differs: \ndict1={dict1[key]} \ndict2={dict2[key]}")

def build_follow_set(start, rules_map, NEIGHBOURS, NT_OCCURENCES, IN_FIRSTS):
    follows = {start: set([(EGrammarToken.PUNCTUATION, "$")])} 
    out_cpy = {}
    nexts_map = {}
    for r in NEIGHBOURS:
        for pair in NEIGHBOURS[r]:
            nexts_map.setdefault(r, {}).setdefault(pair[0][1], []).append(pair[1])
    while out_cpy != follows:
        out_cpy = copy.deepcopy(follows)
        for rule in rules_map:
            for ref_rule in NT_OCCURENCES.get(rule, []):
                if rules_map[ref_rule][0][0] == EGrammarToken.ANY_ORDER:
                    if (EGrammarToken.EPSILON, None) in IN_FIRSTS[ref_rule]:
                        for x in follows.get(ref_rule, []):
                            follows.setdefault(rule, set()).add(x)
                    for x in IN_FIRSTS[ref_rule]:
                        if x != (EGrammarToken.EPSILON, None) and x not in IN_FIRSTS[rule]:
                            follows.setdefault(rule, set()).add(x)
                else:
                    addParent = True
                    current_symbol = (None, rule)
                    while addParent and current_symbol != (EGrammarToken.PUNCTUATION, "$"):
                        next = nexts_map.get(ref_rule).get(current_symbol[1], (EGrammarToken.PUNCTUATION, "$"))[0]
                        firsts_of_next = IN_FIRSTS.get(next[1] , [])
                        if next != (EGrammarToken.PUNCTUATION, "$") and (EGrammarToken.EPSILON, None) not in firsts_of_next:
                            addParent = False
                        if next[0] == EGrammarToken.TERMINAL:
                            follows.setdefault(rule, set()).add(next)                   
                        for y in firsts_of_next:
                            if y != (EGrammarToken.EPSILON, None):
                                follows.setdefault(rule, set()).add(y)
                        current_symbol = next
                    if addParent:
                        for x in follows.get(ref_rule, []):
                            follows.setdefault(rule, set()).add(x)
    return follows

def get_leaf(element, rules_map):
    stack = [element]
    res = []
    while stack:
        current = stack.pop()
        match current[0]:
            case EGrammarToken.TERMINAL | EGrammarToken.NON_TERMINAL | EGrammarToken.USRDEF | EGrammarToken.EPSILON:
                res.append(current)
            case EGrammarToken.OPTIONAL:
                for opt_element in current[1]:
                    stack.append(opt_element)
                    if opt_element[0] != EGrammarToken.NON_TERMINAL:
                        break
                    is_child_optional = True
                    search = opt_element
                    while True:
                        if rules_map[search[1]][0][0] == EGrammarToken.NON_TERMINAL:
                            search = rules_map[search[1]][0]
                            continue
                        if rules_map[search[1]][0][0] == EGrammarToken.OPTIONAL:
                            break
                        is_child_optional = False
                        break
                    if not is_child_optional:
                        break
            case EGrammarToken.GROUP:
                stack.append(current[1][0])
            case _:
                for x in current[1]:
                    stack.append(x)
    return res

def build_firsts_set2(rules_map):
    firsts = {}
    out_cpy = None
    rules = []
    for rule in rules_map:
        firsts[rule] = set()
        rules.append(rule)

    while out_cpy != firsts:
        out_cpy = copy.deepcopy(firsts)
        for rule in rules[::-1]:
            rule_content = rules_map[rule] 
            i = 0
            eps = True
            nxt_grp = False
            while eps or nxt_grp:
                eps = False
                if not nxt_grp:
                    current = rule_content[i]
                nxt_grp = False
                match current[0]:
                    case EGrammarToken.TERMINAL | EGrammarToken.USRDEF:
                        firsts[rule].add(current)
                    case EGrammarToken.NON_TERMINAL:
                        for x in firsts[current[1]]:
                            if x != (EGrammarToken.EPSILON, None):
                                firsts[rule].add(x)
                        if (EGrammarToken.EPSILON, None) in firsts[current[1]]:
                            eps = True
                    case EGrammarToken.OPTIONAL:
                        eps = True
                        leaves = get_leaf(current, rules_map)
                        for x in leaves:
                            if x[0] == EGrammarToken.NON_TERMINAL:
                                firsts[rule] = firsts[rule].union(firsts[x[1]])
                            else:
                                firsts[rule].add(x)
                    case EGrammarToken.XOR:
                        leaves = get_leaf(current, rules_map)
                        for x in leaves:
                            if x[0] == EGrammarToken.NON_TERMINAL:
                                for y in firsts[x[1]]:
                                    if y[0] != EGrammarToken.EPSILON:
                                        firsts[rule].add(y)
                                    else:
                                        eps = True
                            else:
                                firsts[rule].add(x)
                    case EGrammarToken.ANY_ORDER:
                        leaves = get_leaf(current, rules_map)
                        count = 0
                        for x in leaves:
                            if x[0] == EGrammarToken.NON_TERMINAL:
                                for y in firsts[x[1]]:
                                    if y[0] != EGrammarToken.EPSILON:
                                        firsts[rule].add(y)
                                    else:
                                        count += 1
                            else:
                                firsts[rule].add(x)
                        if count == len(current[1]):
                            eps = True
                    case EGrammarToken.GROUP:
                        current = current[1][0]
                        nxt_grp = True
                        continue
                    case EGrammarToken.PUNCTUATION:
                        firsts[rule].add((EGrammarToken.EPSILON, None))
                        break  
                i += 1     
    return firsts

  

            


    pass


def build_firsts_set(rules_map, OUT_FIRSTS):
    # Firsts resolving section
    for rule in rules_map:
        derivation_path = []
        derivation_path.append((EGrammarToken.NON_TERMINAL, rule,0))
        while derivation_path:
            local_first = derivation_path[len(derivation_path)-1]
            firsts_array = OUT_FIRSTS.get(local_first[1], None) 
            if firsts_array is None:
                print(f"Error: rule {local_first[1]} do not have a proper definition")
                exit(1)
            
            nt_ctr = 0
            for idx, el in enumerate(firsts_array):
                # idx = firsts_array.index(el,rsv_idx)
                if el[0] == EGrammarToken.NON_TERMINAL:
                    if el in [(x,y) for x,y,_ in derivation_path]:
                        print(f"Error: Grammar is left recursive {el[1]} can be derived in {local_first[1]}\nBut {el[1]} is already in the derivation path for rule {derivation_path[0][1]}")
                        print("Full derivation: ")
                        print(" --> ".join([x[1] for x in derivation_path]) + " --> " + el[1] )
                        exit(1)
                    derivation_path.append((el[0], el[1], idx))
                    nt_ctr += 1
                    break
            if nt_ctr <= 0:
                #reached end of path no more non terminal in firsts
                if len(derivation_path) <= 1:
                    # Resolved all non terminals in current path go to next rule
                    break
                # remove top of stack as top is already in local_first
                derivation_path.pop()
                #replace in first of next rule by firsts of current local_rule
                # A -> B
                # B -> "hi" | "hello"
                # replace B in first of A with "hi" and "hello"
                next_rule = derivation_path[len(derivation_path)-1]
                OUT_FIRSTS[next_rule[1]].pop(local_first[2])
                for x in firsts_array:
                    if x in OUT_FIRSTS[next_rule[1]]:
                        if x == (EGrammarToken.EPSILON, None):
                            continue
                        print(f"Error: Grammar is ambigious\nTrying to derive {local_first[1]}\n'{x[1]}' already in firsts of {next_rule[1]}")
                        exit(1)
                    OUT_FIRSTS[next_rule[1]].insert(local_first[2], x)
    
def build_table(rule_map:dict, firsts_and_follows:tuple[dict, dict, dict]):
    FIRSTS, FOLLOWS, _ = firsts_and_follows
    TABLE = {}
    for rule in rule_map:
        TABLE[rule] = {}
        for first in FIRSTS[rule]:
            if first != (EGrammarToken.EPSILON, None):
                tmp = rule_map[rule][0]
                match tmp[0]:
                    case EGrammarToken.OPTIONAL:
                        TABLE[rule][first] = rule_map[rule][0][1]
                    case EGrammarToken.XOR:
                        for bra in tmp[1]:
                            leaves = get_leaf(bra, rule_map)
                            for leaf in leaves:
                                if leaf[0] == EGrammarToken.NON_TERMINAL and first in FIRSTS[leaf[1]]:
                                    TABLE[rule][first] = [bra]
                                    break
                                elif first == leaf:
                                    TABLE[rule][first] = [bra]
                                    break
                    case _:
                        TABLE[rule][first] = rule_map[rule][:-1]
                    
            else:
                for follow in FOLLOWS[rule]:
                    TABLE[rule].setdefault(follow, []).append((EGrammarToken.EPSILON, None))
    return TABLE
                
    
def preprocess_tokens(tokens) -> list:
    for idx, token in enumerate(tokens):
        match token[0]:
            case EGrammarToken.NON_TERMINAL | EGrammarToken.RULE_NAME:
                tokens[idx] = (token[0], token[1].replace("-", "_"))

    
def sanity_check_rules(start_rname, rules_map, NT_OCCURENCE):
    # check1: All rules appearing in RHS must be defined as a LHS
    if len(rdiff := set(NT_OCCURENCE.keys()).difference(rules_map.keys())) > 0:
        for r in rdiff:
            print(f"SANITY ERROR: Rule {r.replace("_", "-")} is not defined !")
        exit(1)
     
    # check2: All rules that have a LHS but no RHS are deleted, unused rules
    if len(rdiff := set(rules_map.keys()).difference(NT_OCCURENCE.keys())) > 0:
        for r in rdiff:
            if r != start_rname:
                print(f"SANITY WARNING: Rule {r.replace("_", "-")} is never used and will be ignored (deleted internally) !")
                rules_map.pop(r)
                #TODO Clean NT_OCCURENCES for follows aswell


    # Pre-Follow sanity check: Ensure no rules is define twice 

def sanity_check_firsts(FIRSTS):
    # Firsts sanity: All rules must have at least a first even if its $
    is_there_empty_firsts = False
    for r in FIRSTS:
        if len(FIRSTS[r]) <= 0:
            print(f"SANITY ERROR: Couldn't compute any firsts for rule: {r.replace("_", "-")} ! ")
            is_there_empty_firsts = True
    if is_there_empty_firsts:
        exit(1)

def sanity_check_follows(FOLLOWS):
    pass

def process_grammar_file(fgammar, starting_rule):
    with open(fgammar, "r", encoding="utf-8") as file:
        grammar = file.read()
        tokens = tokenize(grammar)
        preprocess_tokens(tokens)
        # Actual parsing of grammar rules
        parsed_rules_map, NEIGBOURS, has_optionals = parse_grammar(tokens)
        # Buildings a set to map each appearence of a non terminal on the RHS with its LHS
        NT_OCCURENCE = build_nt_occurences(parsed_rules_map)
        sanity_check_rules(starting_rule,parsed_rules_map, NT_OCCURENCE)

        FIRSTS= build_firsts_set2(parsed_rules_map)
        sanity_check_firsts(FIRSTS)
        if has_optionals:
            FOLLOWS = build_follow_set( starting_rule,parsed_rules_map, NEIGBOURS, NT_OCCURENCE,FIRSTS)
            sanity_check_follows(FOLLOWS)

    return build_table(parsed_rules_map, (FIRSTS, FOLLOWS, NEIGBOURS))



        
    


if __name__ == "__main__":
    print("Do not call me directly, use me in other scripts")
    process_grammar_file(r"./grammar.conf")

  
else:
    pass