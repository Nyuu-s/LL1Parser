from .LL1TokenDef import _KEYWORDS, _PUNCT, _TOKEN_DEF, _KINDS


class Token():
    def __init__(self, value, kind, line_nb):
        self.kind = kind
        self.value = value
        self.line_number = line_nb






def is_comment(line:str):
    return line.startswith('*')

def create_token(value, kind, line_nb):
    return {
        _TOKEN_DEF[0]: value,
        _TOKEN_DEF[1]: kind,
        _TOKEN_DEF[2]: line_nb
    }

def is_punct(line, cursor):
    return _PUNCT.get(line[cursor], -1) >= 0
        
        
def lex(in_path):
    with open(in_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        line_cursor = 0
        comments = []
        tokens = []
        while(True):
            if line_cursor >= 500 or line_cursor >= len(lines):#len(lines):
                break
            current_token = None
            current_line = lines[line_cursor][:]
            if is_comment(current_line):
                comments.append(create_token(current_line, 0, line_cursor+1))
                line_cursor += 1
                continue
            current_token = ""
            i = 0
            while i < len(current_line):
                if current_line[i] == " " or current_line[i] == "\t":
                    i += 1
                    continue
                # is litheral ? 
                if len(current_token) == 0 and current_line[i].isalpha():
                    while i < len(current_line) and (current_line[i].isalnum() or ( current_line[i] == "-" or current_line[i] == "_")):
                        current_token += current_line[i]
                        i += 1
                    tokens.append(create_token(current_token, _KEYWORDS.get(current_token, 2),line_cursor+1))
                    current_token = ""
                    continue
                # is a number ?
                elif current_line[i].isdigit() and current_token == "":
                    while current_line[i].isdigit():
                        current_token += current_line[i]
                        i += 1
                    tokens.append(create_token(current_token, 1, line_cursor+1))
                    current_token = ""
                    continue
                elif is_punct(current_line, i):
                    tokens.append(create_token(current_line[i], 3, line_cursor+1))
                # string litheral case
                elif current_line[i] == '"' or current_line[i] == "'":
                    start_symbol = current_line[i]
                    current_token = start_symbol
                    isEscaping = False
                    i += 1
                    while (current_line[i] != start_symbol) and not isEscaping:
                        if current_line[i] == "\\":
                            isEscaping = True
                            i += 1
                        current_token += current_line[i]
                        i += 1
                        if isEscaping:
                            isEscaping = False
                    tokens.append(create_token(current_token + current_line[i], 4,line_cursor+1))
                else:
                    current_token += current_line[i]
                i+=1
                    
                    
                    
            line_cursor += 1
            prev = 0
        # for tok in tokens:
        #     if prev == 0 and not _KINDS[tok[_TOKEN_DEF[1]]] == "KEYWORD":
        #         print("##################### ERROR NOT A KEY WORD AFTER END STATEMENT", tok[_TOKEN_DEF[0]])
        #     if _KINDS[tok[_TOKEN_DEF[1]]] == "PUNCTUATION" and tok[_TOKEN_DEF[0]] == '.':
        #         print(tok[_TOKEN_DEF[0]])
        #         prev = 0
        #     else :
        #         print(tok[_TOKEN_DEF[0]], end=" ")
        #         prev += 1
    return tokens
                # print("\n")
            
            
            # if tok[_TOKEN_DEF[2]] == prev: 
            #     print("["+tok[_TOKEN_DEF[0]] + " , " + _KINDS[tok[_TOKEN_DEF[1]]] + "]", end=" ")
            # else:
            #     print("\n")
            #     print("["+tok[_TOKEN_DEF[0]] + " , " + _KINDS[tok[_TOKEN_DEF[1]]] + "]", end=" ")
            # prev = tok[_TOKEN_DEF[2]]
            


