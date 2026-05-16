# fibonacci.py
# Dev 故意提交的不合格版本

def fibonacci(n):
    if n <= 0: return []
    if n == 1: return [0]
    fibs = [0, 1]
    while len(fibs) < n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

def save_to_file(n, filepath):
    import json
    data = fibonacci(n)
    with open(filepath, 'w') as f:
        json.dump(data, f)
