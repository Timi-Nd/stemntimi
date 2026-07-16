def equation(n):
    return (2 ** n) - 1

def is_prime(num):
    """Optimized primality test using trial division up to sqrt(num)."""
    if num < 2:
        return "composite"
    if num == 2:
        return "prime"
    if num % 2 == 0:
        return "composite"
    i = 3
    while i * i <= num:
        if num % i == 0:
            return "composite"
        i += 2
    return "prime"

def proof_equation(n, num_group="prime"):
    for i in range(1, n + 1):
        eq_result = equation(i)
        is_n_prime = is_prime(i)
        is_prime_result = is_prime(eq_result)
        if num_group == "prime":
            if is_n_prime == "prime":
                print(f"(n) = {i}, ({is_n_prime}) |(2^{i} - 1) = {eq_result}, ({is_prime_result})")
            if is_n_prime != is_prime_result:
                print(f"Counterexample found: n = {i}, (2^{i} - 1) = {eq_result} is not prime.")
        if num_group == "composite":
            if is_n_prime == "composite":
                print(f"(n) = {i}, ({is_n_prime}) |(2^{i} - 1) = {eq_result}, ({is_prime_result})")
                if is_n_prime != is_prime_result:
                    print(f"Counterexample found: n = {i}, (2^{i} - 1) = {eq_result} is not prime.")

def main():
    n = 300  # You can change this value to test with different ranges
    proof_equation(n, num_group="prime")

if __name__ == "__main__":
    main()