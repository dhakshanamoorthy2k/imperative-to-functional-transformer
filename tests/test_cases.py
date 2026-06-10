# Test 1 - straight line assignment
test1 = """
def f():
    x = 1
    y = x + 2
    return y
"""

# Test 2 - if/else
test2 = """
def f(x):
    if x > 0:
        y = x + 1
    else:
        y = 0
    return y
"""

# Test 3 - while loop
test3 = """
def f(n):
    total = 0
    i = 0
    while i < n:
        total = total + i
        i = i + 1
    return total
"""

# Test 4 - for loop
test4 = """
def f(n):
    total = 0
    for i in range(n):
        total = total + i
    return total
"""

# Test 5 - nested if
test5 = """
def f(x, y):
    if x > 0:
        if y > 0:
            z = x + y
        else:
            z = x
    else:
        z = 0
    return z
"""

# Test 6 - map pattern
# for loop that transforms every element
test6 = """
def f(items):
    result = []
    for x in items:
        result.append(x * 2)
    return result
"""

# Test 7 - filter pattern
# for loop that collects elements matching a condition
test7 = """
def f(items):
    result = []
    for x in items:
        if x > 0:
            result.append(x)
    return result
"""

# Test 8 - reduce pattern
# for loop that accumulates a single value
test8 = """
def f(items):
    total = 0
    for x in items:
        total = total + x
    return total
"""

# Test 9 - zip pattern
# combining two lists together
test9 = """
def f(items_a, items_b):
    result = []
    for i in range(len(items_a)):
        result.append(items_a[i] + items_b[i])
    return result
"""