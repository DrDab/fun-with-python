"""
RPN

Description:
"""
stack = []
def push(num):
    stack.append(num)
    
def pop():
    pos = len(stack)-1
    toReturn = stack[pos]
    stack.remove(toReturn)
    return toReturn

def peek():
    pos = len(stack)-1
    toReturn = stack[pos]
    return toReturn

def isEmpty():
    return len(stack) == 0

def clear():
    global stack
    stack = []

print("\"quit\" to quit.")
isRunning = True
while isRunning:
    clear()
    print("Please enter an RPN formula.")
    formula = input()
    if formula == "quit":
        isRunning = False
        break
    tokens = formula.split()
    for token in tokens:
        if token == "+":
            num1 = pop()
            num2 = pop()
            push(num2+num1)
        elif token == "-":
            num1 = pop()
            num2 = pop()
            push(num2-num1)
        elif token == "*":
            num1 = pop()
            num2 = pop()
            push(num2*num1)
        elif token == "/":
            num1 = pop()
            num2 = pop()
            push(num2/num1)
        elif token == "^":
            num1 = pop()
            num2 = pop()
            push(num2**num1)
        elif token == "%":
            num1 = pop()
            num2 = pop()
            push(num2%num1)
        else:
            push(float(token))
    print(stack[0])
