use num_bigint::BigUint;
use num_traits::{One, Zero};

fn equation(n: u64) -> BigUint {
    (BigUint::one() << n) - BigUint::one()
}

fn is_prime_u64(n: u64) -> bool {
    if n < 2 {
        return false;
    }
    if n == 2 {
        return true;
    }
    if n % 2 == 0 {
        return false;
    }

    let mut i = 3;
    while i * i <= n {
        if n % i == 0 {
            return false;
        }
        i += 2;
    }
    true
}

fn is_mersenne_prime(p: u64) -> bool {
    if p == 2 {
        return true;
    }
    if !is_prime_u64(p) {
        return false;
    }

    let mut s = BigUint::from(4u8);
    let m = equation(p);
    for _ in 0..(p - 2) {
        s = (&s * &s) - BigUint::from(2u8);
        s %= &m;
    }

    s.is_zero()
}

fn proof_equation(n: u64, num_group: &str) {
    let want_prime = num_group == "prime";

    for i in 1..=n {
        let is_n_prime = is_prime_u64(i);
        if is_n_prime != want_prime {
            continue;
        }

        let eq_result = equation(i);
        let is_n_prime_str = if is_n_prime { "prime" } else { "composite" };
        let is_prime_result = if is_n_prime {
            if is_mersenne_prime(i) {
                "prime"
            } else {
                "composite"
            }
        } else {
            "composite"
        };

        println!(
            "For n = {0}({1}), 2^{0} - 1 = {2}({3})",
            i, is_n_prime_str, eq_result, is_prime_result
        );

        if is_n_prime_str != is_prime_result {
            println!("Counterexample: n = {0}, 2^{0} - 1 = {1}", i, eq_result);
        }
    }
}

fn main() {
    let n = 300;
    proof_equation(n, "prime");
}
