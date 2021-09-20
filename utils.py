def fibonacci(n: int) -> int:
    results = {0: 0, 1: 1, 2: 1}

    def fibonacci0(n : int) -> int:
        if n not in results.keys():
            results[n] = fibonacci0(n - 1) + fibonacci0(n - 2)
        return results[n]

    return fibonacci0(n)