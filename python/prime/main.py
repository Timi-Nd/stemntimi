import math


def equation(n):
    return (1 << n) - 1


def is_prime(num):
    """Deterministic primality test for small integers."""
    if num < 2:
        return "composite"
    if num in (2, 3):
        return "prime"
    if num % 2 == 0 or num % 3 == 0:
        return "composite"
    limit = math.isqrt(num)
    i = 5
    while i <= limit:
        if num % i == 0 or num % (i + 2) == 0:
            return "composite"
        i += 6
    return "prime"


def is_mersenne_prime(p):
    if is_prime(p) != "prime":
        return "composite"
    if p == 2:
        return "prime"
    m = equation(p)
    s = 4
    for _ in range(p - 2):
        s = ((s * s) - 2) % m
    return "prime" if s == 0 else "composite"


def proof_equation(n, num_group="prime"):
    for i in range(1, n + 1):
        eq_result = equation(i)
        is_n_prime = is_prime(i)
        is_prime_result = is_mersenne_prime(i) if is_n_prime == "prime" else "composite"

        if num_group == "prime":
            if is_n_prime == "prime":
                print(f"(n) = {i}, ({is_n_prime}) |(2^{i} - 1) = {eq_result}, ({is_prime_result})")
            if is_n_prime != is_prime_result:
                print(f"Counterexample found: n = {i}, (2^{i} - 1) = {eq_result} is not prime.")

        if num_group == "composite" and is_n_prime == "composite":
            print(f"(n) = {i}, ({is_n_prime}) |(2^{i} - 1) = {eq_result}, ({is_prime_result})")
            if is_n_prime != is_prime_result:
                print(f"Counterexample found: n = {i}, (2^{i} - 1) = {eq_result} is not prime.")


def main():
    while True:
        try:
            n = int(input("Enter the range for the proof: "))
            options = {
                1: "prime",
                2: "composite"
            }
            
            num_group = options.get(int(input("Enter 1 for prime or 2 for composite: ")), "prime")
            
        except Exception as e:
            print("Invalid input.")
            continue
        proof_equation(n, num_group)
        break


if __name__ == "__main__":
    main()
