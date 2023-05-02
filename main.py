from sys import argv
from dataclasses import dataclass

enum: int = 0
def iota(reset = False) -> int:
    global enum
    if reset:
        enum = 0
    result: int = enum
    enum += 1
    return result

stack: list[int or str] = []

SYMBOL = iota()
NUMBER = iota()
STRING = iota()
UNKNOWN = iota()
SPACE = iota()
NEWLINE = iota()

QUOTATION = iota()

PLUS = iota()
MINUS = iota()
TIMES = iota()
DIVIDE = iota()

GREATER = iota()
LESS = iota()

GREATEREQUAL = iota()
LESSEQUAL = iota()

EQUALS = iota()

IF = iota()
ELSE = iota()

OVER = iota()
DUPLICATE = iota()

BANG = iota()

END = iota()

PRINTABLE_TOKENS: list = ["SYMBOL", "NUMBER", "STRING", "UNKNOWN", "SPACE", "NEWLINE", "QUOTATION", "PLUS", "MINUS", "TIMES", "DIVIDE", "GREATER", "LESS", "GREATEREQUALS", "LESSEQUALS", "IF", "ELSE", "OVER", "DUPLICATE", "BANG", "END"]

@dataclass
class Position:
    line: int
    col: int

LINE = iota(True)
COL = iota()


@dataclass
class Token:
    type: int
    position: Position
    value: any

TYPE = iota(True)
POSITION = iota()
VALUE = iota()


def printError(token: Token, text: str, inputFile, filePath: str, specific: bool = True) -> None:
    print(f"\n{filePath}:{token[POSITION].line}:{token[POSITION].col}: error: {text}")
    inputFile.seek(0)

    for i, line in enumerate(inputFile):
        if i == token[POSITION].line - 1:
            print(f" {token[POSITION].line} | {line.rstrip()}")

    inputFile.close()
    buffer: str = " "
    whiteSpace: str = len(str(token[POSITION].line))
    for i in range(whiteSpace):
        buffer += " "
    print(f"{buffer} | ", end="")

    for i in range(token[POSITION].col - whiteSpace):
        print(" ", end="")
    for i in range(len(str(token[VALUE]))):
        print("~", end="")
    print("\n")
    exit(1)


def characterToToken(char: str) -> int:
    if char.isdigit():
        return NUMBER
    elif char.isalpha():
        return SYMBOL
    elif char == ' ':
        return SPACE
    elif char == '\n':
        return NEWLINE
    elif char == '+':
        return PLUS
    elif char == '-':
        return MINUS
    elif char == '*':
        return TIMES
    elif char == '/':
        return DIVIDE
    elif char == '^':
        return OVER
    elif char == '&':
        return DUPLICATE
    elif char == '!':
        return BANG
    elif char == '=':
        return EQUALS
    elif char == '>':
        return GREATER
    elif char == '<':
        return LESS
    elif char == '"':
        return QUOTATION
    else:
        return UNKNOWN


def tokenize(inputFile, filePath) -> list[Token]:
    tmpTokens: list[Token()] = []
    tokens: list [Token()] = []

    lines: list = [line for line in inputFile]
    index: int = 0

    lineNo: int = 1
    col: int = 1
    for line in lines:
        for char in line:
            tmpTokens.insert(index, (characterToToken(char), Position(lineNo, col), char))
            index += 1
            col += 1
        lineNo += 1
        col = 1

    tmpTokens = [token for token in tmpTokens if token[0] != NEWLINE]

    index = 0
    while index < len(tmpTokens) - 1:
        currentTokenType: int = tmpTokens[index][TYPE]
        tokenPosition: str = tmpTokens[index][POSITION]
        token: str = tmpTokens[index][VALUE]

        if currentTokenType == SPACE:
            index += 1
            continue

        if currentTokenType == NUMBER and tmpTokens[index + 1][TYPE] == NUMBER:
            buffer = token + tmpTokens[index + 1][VALUE]
            index += 1

            while index + 1 < len(tmpTokens) and tmpTokens[index + 1][TYPE] == currentTokenType:
                buffer += tmpTokens[index + 1][VALUE]
                index += 1

            tokens.append((currentTokenType, tokenPosition, int(buffer)))
        elif currentTokenType != tmpTokens[index + 1][TYPE] and currentTokenType == NUMBER:
            tokens.append((currentTokenType, tokenPosition, int(tmpTokens[index][VALUE])))
        elif currentTokenType == QUOTATION and tmpTokens[index + 1][TYPE] == SYMBOL:
            buffer =  tmpTokens[index + 1][VALUE]
            index += 1

            try:
                while tmpTokens[index + 1][TYPE] != QUOTATION:
                    buffer += tmpTokens[index + 1][VALUE]
                    index += 1
            except IndexError:
                printError((STRING, tokenPosition, buffer), "expected a closing quotation mark", inputFile, filePath, False)
            except Exception as Error:
                print(Error)

            index += 1
            tokens.append((STRING, tokenPosition, buffer))
        elif currentTokenType == tmpTokens[index + 1][TYPE] and currentTokenType == SYMBOL:
            buffer = token + tmpTokens[index + 1][VALUE]
            index += 1

            while index + 1 < len(tmpTokens) and tmpTokens[index + 1][TYPE] == currentTokenType:
                buffer += tmpTokens[index + 1][VALUE]
                index += 1

            if buffer == "if":
                tokens.append((IF, tokenPosition, buffer))
            elif buffer == "else":
                tokens.append((ELSE, tokenPosition, buffer))
            elif buffer == "end":
                tokens.append((END, tokenPosition, buffer))
            else:
                tokens.append((currentTokenType, tokenPosition, buffer))
        elif currentTokenType == LESS and tmpTokens[index + 1][TYPE] == EQUALS:
            tokens.append((LESSEQUAL, tokenPosition, token))
            index += 1
        elif currentTokenType == GREATER and tmpTokens[index + 1][TYPE] == EQUALS:
            tokens.append((GREATEREQUAL, tokenPosition, token))
            index += 1
        else:
            tokens.append((currentTokenType, tokenPosition, token))
        index += 1

    try:
        currentTokenType: int = tmpTokens[index][TYPE]
        tokenPosition: str = tmpTokens[index][POSITION]
        token: str = tmpTokens[index][VALUE]

        if currentTokenType == NUMBER:
            tokens.append((currentTokenType, tokenPosition, int(token)))
        else:
            tokens.append((currentTokenType, tokenPosition, token))
    except IndexError:
        pass

    return tokens


def parse(tokens: list[Token], inputFile, filePath: str, index: int = 0) -> int:
    while index < len(tokens):
        type: int = tokens[index][TYPE]
        position: Position = tokens[index][POSITION]
        value: str or int = tokens[index][VALUE]

        if type == NUMBER:
            stack.append(value)
            index += 1
            continue

        if type == STRING:
            stack.append(value)
            index += 1
            continue

        if type == SPACE:
            index += 1
            continue

        if type == PLUS:
            try:
                x = stack.pop()
                y = stack.pop()
                stack.append(int(x) + int(y))
            except IndexError:
                printError((type, position, value), "stack does not have enough values to perform this operation", inputFile, filePath)
            except ValueError:
                printError((type, position, value), f"cannot add '{x}' and '{y}': incompatible types for plus operand ", inputFile, filePath)
            except Exception as Error:
                printError((type, position, value), Error, inputFile, filePath)
        elif type == MINUS:
            try:
                x = int(stack.pop())
                y = int(stack.pop())
                stack.append(x - y)
            except IndexError:
                printError((type, position, value), "stack does not have enough values to perform this operation", inputFile, filePath)
            except Exception as Error:
                printError((type, position, value), Error, inputFile, filePath)
        elif type == TIMES:
            try:
                x = int(stack.pop())
                y = int(stack.pop())
                stack.append(x * y)
            except IndexError:
                printError((type, position, value), "stack does not have enough values to perform this operation", inputFile, filePath)
            except Exception as Error:
                printError((type, position, value), Error, inputFile, filePath)
        elif type == DIVIDE:
            try:
                x = int(stack.pop())
                y = int(stack.pop())
                stack.append(x / y)
            except IndexError:
                printError((type, position, value), "stack does not have enough values to perform this operation", filePath)
            except ZeroDivisionError:
                printError((type, position, value), "cannot divide a number by zero", filePath)
            except Exception as Error:
                printError((type, position, value), Error, inputFile, filePath)
        elif type == DUPLICATE:
            try:
                x = int(stack.pop())
                stack.append(x)
                stack.append(x)
            except IndexError:
                printError((type, position, value), "no value to duplicate", inputFile, filePath)
            except Exception as Error:
                print(Error)
        elif type == OVER:
            try:
                x = int(stack.pop())
                y = int(stack.pop())
                stack.append(y)
                stack.append(x)
                stack.append(y)
            except IndexError:
                printError((type, position, value), "no value to the left of to push", inputFile, filePath)
            except Exception as Error:
                print(Error)
        elif type == EQUALS:
            try:
                x = stack.pop()
                y = stack.pop()

                if x == y:
                    stack.append(y)
                    stack.append(x)
                    stack.append(1)
                else:
                    stack.append(y)
                    stack.append(x)
                    stack.append(0)
            except IndexError:
                printError((type, position, value), "stack does not have enough values to compare", inputFile, filePath)
            except Exception as Error:
                print(Error)
        elif type == GREATER:
            try:
                x = stack.pop()
                y = stack.pop()

                if x > y:
                    stack.append(y)
                    stack.append(x)
                    stack.append(1)
                else:
                    stack.append(y)
                    stack.append(x)
                    stack.append(0)
            except IndexError:
                printError((type, position, value), "stack does not have enough values to compare", inputFile, filePath)
            except Exception as Error:
                print(Error)
        elif type == LESS:
            try:
                x = stack.pop()
                y = stack.pop()

                if x < y:
                    stack.append(y)
                    stack.append(x)
                    stack.append(1)
                else:
                    stack.append(y)
                    stack.append(x)
                    stack.append(0)
            except IndexError:
                printError((type, position, value), "stack does not have enough values to compare", inputFile, filePath)
            except Exception as Error:
                print(Error)
        elif type == LESSEQUAL:
            try:
                x = stack.pop()
                y = stack.pop()

                if x <= y:
                    stack.append(y)
                    stack.append(x)
                    stack.append(1)
                else:
                    stack.append(y)
                    stack.append(x)
                    stack.append(0)
            except IndexError:
                printError((type, position, value), "stack does not have enough values to compare", inputFile, filePath)
            except Exception as Error:
                print(Error)
        elif type == GREATEREQUAL:
            try:
                x = stack.pop()
                y = stack.pop()

                if x >= y:
                    stack.append(y)
                    stack.append(x)
                    stack.append(1)
                else:
                    stack.append(y)
                    stack.append(x)
                    stack.append(0)
            except IndexError:
                printError((type, position, value), "stack does not have enough values to compare", inputFile, filePath)
            except Exception as Error:
                print(Error)
        elif type == BANG:
            try:
                print(stack.pop())
            except IndexError:
                printError((type, position, value), "stack does not have any value to print", inputFile, filePath)
            except Exception as Error:
                print(Error)
        elif type == IF:
            try:
                value: bool = int(stack.pop())
                index += 1
                offset: int = 0

                elseBlockIndex: None or int = None
                endBlockIndex: int = 0

                while tokens[index + endBlockIndex][TYPE] != END:
                    if tokens[index + endBlockIndex][TYPE] == ELSE:
                        elseBlockIndex = index + endBlockIndex
                    endBlockIndex += 1

                endBlockIndex = index + endBlockIndex
                if value and elseBlockIndex == None:
                    tokesnBetweenIfAndEnd: list[Token] = tokens[index:endBlockIndex]
                    index += parse(tokesnBetweenIfAndEnd, inputFile, filePath)
                elif value and elseBlockIndex:
                    tokensBetweenIfAndElse: list[Token] = tokens[index:elseBlockIndex]
                    parse(tokensBetweenIfAndElse, inputFile, filePath)
                elif not(value) and elseBlockIndex:
                    tokensBetweenElseAndEnd: list[Token] = tokens[elseBlockIndex + 1: endBlockIndex]
                    parse(tokensBetweenElseAndEnd, inputFile, filePath)

                index = endBlockIndex

            except IndexError:
                printError((type, position, value), "expected an else or end block", inputFile, filePath)
            except ValueError:
                printError((type, position, value), "expected a prior condition", inputFile, filePath)
            except Exception as Error:
                print(Error)
        else:
            printError((type, position, value), "unknown operation or symbol", inputFile, filePath)

        index += 1
    return index


def main():
    if len(argv) < 2:
        print("error: expected an input file")
        print("usage: python3 main.py file.kag")
        exit(1)

    filePath: str = argv[1]
    if ".kag" not in filePath:
        print("error: expected an input file with the .kag extension")
        print("usage: python3 main.py file.kag")
        exit(1)

    try:
        inputFile: file = open(filePath)
    except Exception as error:
        print(f"error: no such file or directory: {filePath}")
        exit(1)


    tokens: list[Token()] = tokenize(inputFile, filePath)
    parse(tokens, inputFile, filePath)

    inputFile.close()

#    if stack:
#        word: str = "value" if len(stack) == 1 else "values"
#        printError((type, position, value), f"unhandled stack {word}: {stack}", inputFile, filePath)


if __name__ == '__main__':
    main()
else:
    exit(1)
