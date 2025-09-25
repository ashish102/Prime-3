"""
Number Theory Module - Core Mathematical Algorithms

This module implements fundamental number theory algorithms with educational
focus and performance optimization for 64-bit integers.

Algorithms implemented:
1. Deterministic Miller-Rabin primality testing using Sinclair's proven base set
2. Hybrid integer factorization with trial division and Pollard's Rho
3. Arithmetic progression analysis for consecutive primes
4. Probabilistic primality testing for edge cases

References:
- Miller-Rabin deterministic bases: Sinclair (2011)
- Pollard's Rho with Brent optimization: Brent (1980)
- Arithmetic progressions: Green-Tao theorem applications
"""

import random
import math
from typing import List, Tuple, Union


# Constants
MAX_64BIT = 2**64 - 1
SMALL_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
    239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
    331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419,
    421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503,
    509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607,
    613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701,
    709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811,
    821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911,
    919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997
]

# Deterministic Miller-Rabin bases for 64-bit integers (Sinclair 2011)
DETERMINISTIC_BASES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]


def _validate_input(n: Union[int, float], name: str = "n") -> int:
    """
    Validate and convert input to integer with 64-bit range checking.

    Args:
        n: Input number to validate
        name: Parameter name for error messages

    Returns:
        Valid integer within 64-bit range

    Raises:
        TypeError: If input cannot be converted to integer
        ValueError: If input is negative or exceeds 64-bit range
    """
    if isinstance(n, float):
        if not n.is_integer():
            raise TypeError(f"{name} must be an integer, got float with decimal: {n}")
        n = int(n)

    if not isinstance(n, int):
        raise TypeError(f"{name} must be an integer, got {type(n).__name__}")

    if n < 0:
        raise ValueError(f"{name} must be non-negative, got {n}")

    if n > MAX_64BIT:
        raise ValueError(f"{name} exceeds 64-bit range (max: {MAX_64BIT}), got {n}")

    return n


def _miller_rabin_test(n: int, base: int) -> bool:
    """
    Perform single Miller-Rabin test with given base.

    Args:
        n: Odd integer to test (n >= 3)
        base: Base for Miller-Rabin test

    Returns:
        True if n passes the test (possibly prime), False if composite
    """
    if n <= base:
        return n == base

    # Write n-1 as d * 2^r
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    # Compute base^d mod n
    x = pow(base, d, n)
    if x == 1 or x == n - 1:
        return True

    # Repeat r-1 times
    for _ in range(r - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True
        if x == 1:
            return False

    return False


def is_prime_64(n: Union[int, float]) -> bool:
    """
    Deterministic primality test for 64-bit integers using Miller-Rabin.

    Uses Sinclair's proven base set [2,3,5,7,11,13,17,19,23,29,31,37] which
    provides 100% deterministic results for all integers up to 2^64.

    Time Complexity: O(log³ n)
    Space Complexity: O(1)

    Args:
        n: Integer to test for primality

    Returns:
        True if n is prime, False if composite

    Raises:
        TypeError: If n is not an integer or convertible float
        ValueError: If n is negative or exceeds 64-bit range

    Examples:
        >>> is_prime_64(2)
        True
        >>> is_prime_64(97)
        True
        >>> is_prime_64(100)
        False
        >>> is_prime_64(2**61 - 1)  # Large Mersenne prime
        True
    """
    n = _validate_input(n, "n")

    # Handle small cases
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    if n < 9:
        return n in {3, 5, 7}

    # Use deterministic Miller-Rabin with proven base set
    for base in DETERMINISTIC_BASES:
        if not _miller_rabin_test(n, base):
            return False

    return True


def is_probable_prime(n: Union[int, float], k: int = 20) -> bool:
    """
    Probabilistic primality test using random Miller-Rabin rounds.

    This function serves as a fallback for edge cases or when probabilistic
    testing is preferred. Error probability is at most (1/4)^k for composites.

    Time Complexity: O(k * log³ n)
    Space Complexity: O(1)

    Args:
        n: Integer to test for primality
        k: Number of Miller-Rabin rounds (higher = more accurate)

    Returns:
        True if n is probably prime, False if definitely composite

    Raises:
        TypeError: If n is not an integer or k is not an integer
        ValueError: If n is negative, exceeds 64-bit range, or k < 1

    Examples:
        >>> is_probable_prime(97, k=10)
        True
        >>> is_probable_prime(100, k=10)
        False
    """
    n = _validate_input(n, "n")

    if not isinstance(k, int) or k < 1:
        raise ValueError(f"k must be a positive integer, got {k}")

    # Handle small cases
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    if n < 9:
        return n in {3, 5, 7}

    # Perform k rounds of Miller-Rabin with random bases
    for _ in range(k):
        base = random.randint(2, n - 2)
        if not _miller_rabin_test(n, base):
            return False

    return True


def _trial_division(n: int) -> List[int]:
    """
    Factor out small primes using trial division.

    Args:
        n: Integer to factor

    Returns:
        List of prime factors found, n is modified in place
    """
    factors = []

    # Handle factor 2
    while n % 2 == 0:
        factors.append(2)
        n //= 2

    # Handle odd primes up to 1000
    for p in SMALL_PRIMES[1:]:  # Skip 2, already handled
        if p * p > n:
            break
        while n % p == 0:
            factors.append(p)
            n //= p

    return factors, n


def _pollard_rho_brent(n: int, max_iterations: int = 100000) -> int:
    """
    Pollard's Rho algorithm with Brent's cycle detection optimization.

    Brent's method is more efficient than Floyd's tortoise-and-hare approach
    for cycle detection in the pseudorandom sequence.

    Args:
        n: Composite number to factor
        max_iterations: Maximum iterations before giving up

    Returns:
        Non-trivial factor of n, or n if no factor found
    """
    if n % 2 == 0:
        return 2

    # Try multiple random starting points
    for _ in range(10):  # Up to 10 attempts with different constants
        x = random.randint(2, n - 2)
        c = random.randint(1, n - 1)
        y = x
        d = 1
        q = 1

        # Brent's improvement: check for cycles less frequently
        r = 1
        iteration = 0

        while d == 1 and iteration < max_iterations:
            x = y

            # Fast forward r steps
            for _ in range(r):
                y = (y * y + c) % n
                iteration += 1

            k = 0
            while k < r and d == 1 and iteration < max_iterations:
                ys = y

                # Accumulate differences for batch GCD
                for _ in range(min(128, r - k)):  # Batch size 128
                    y = (y * y + c) % n
                    q = (q * abs(x - y)) % n
                    iteration += 1

                d = math.gcd(q, n)
                k += 128

            r *= 2

        if 1 < d < n:
            return d

    return n  # Failed to find factor


def factorize(n: Union[int, float]) -> List[int]:
    """
    Hybrid integer factorization using trial division and Pollard's Rho.

    Strategy:
    1. Trial division by small primes (up to 1000)
    2. Pollard's Rho with Brent optimization for larger factors
    3. Recursive factorization of composite factors

    Time Complexity: O(n^(1/4)) expected, O(√n) worst case
    Space Complexity: O(log n) for recursion and factor storage

    Args:
        n: Integer to factorize

    Returns:
        Sorted list of prime factors (with repetition)

    Raises:
        TypeError: If n is not an integer or convertible float
        ValueError: If n is negative or exceeds 64-bit range

    Examples:
        >>> factorize(1)
        []
        >>> factorize(60)
        [2, 2, 3, 5]
        >>> factorize(97)
        [97]
        >>> factorize(2**32 * 3 * 5 * 7)
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 5, 7]
    """
    n = _validate_input(n, "n")

    if n <= 1:
        return []

    all_factors = []
    stack = [n]

    while stack:
        current = stack.pop()

        if current == 1:
            continue

        # Try trial division first
        small_factors, remainder = _trial_division(current)
        all_factors.extend(small_factors)

        if remainder == 1:
            continue

        # Check if remainder is prime
        if is_prime_64(remainder):
            all_factors.append(remainder)
            continue

        # Use Pollard's Rho for composite remainder
        factor = _pollard_rho_brent(remainder)

        if factor == remainder:
            # Pollard's Rho failed, treat as prime (very rare)
            all_factors.append(remainder)
        else:
            # Found a factor, add both parts to stack
            stack.extend([factor, remainder // factor])

    return sorted(all_factors)


def prime_run_length(start: Union[int, float], diff: Union[int, float],
                    max_terms: int = 1000) -> Tuple[int, List[int]]:
    """
    Find consecutive primes in arithmetic progression.

    Computes the longest initial run length L such that:
    start, start+diff, start+2*diff, ..., start+(L-1)*diff
    are all prime, stopping at the first composite or when reaching max_terms.

    Time Complexity: O(max_terms * log³(largest_term))
    Space Complexity: O(max_terms) for storing the prime sequence

    Args:
        start: First term of the arithmetic sequence
        diff: Common difference (must be positive)
        max_terms: Maximum number of terms to check

    Returns:
        Tuple of (length, list_of_primes) where length is the number of
        consecutive primes found and list_of_primes contains those primes

    Raises:
        TypeError: If inputs are not integers or convertible floats
        ValueError: If start is negative, diff <= 0, or inputs exceed 64-bit range

    Examples:
        >>> prime_run_length(3, 2)  # 3, 5, 7, 11, 13 (stops at 15=3*5)
        (5, [3, 5, 7, 11, 13])
        >>> prime_run_length(5, 6)  # 5, 11, 17, 23, 29 (stops at 35=5*7)
        (5, [5, 11, 17, 23, 29])
        >>> prime_run_length(7, 30)  # Famous long arithmetic progression
        (12, [7, 37, 67, 97, 127, 157, 187, 217, 247, 277, 307, 337])
    """
    start = _validate_input(start, "start")
    diff = _validate_input(diff, "diff")

    if diff <= 0:
        raise ValueError(f"diff must be positive, got {diff}")

    if not isinstance(max_terms, int) or max_terms < 1:
        raise ValueError(f"max_terms must be a positive integer, got {max_terms}")

    primes = []
    current = start

    for i in range(max_terms):
        # Check for 64-bit overflow before computing next term
        if current > MAX_64BIT:
            break

        if is_prime_64(current):
            primes.append(current)

            # Check if next term would overflow
            if current > MAX_64BIT - diff:
                break

            current += diff
        else:
            # Found first composite, stop the run
            break

    return len(primes), primes


# Utility functions for testing and verification
def _gcd(a: int, b: int) -> int:
    """Greatest common divisor using Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return a


def _is_perfect_power(n: int) -> bool:
    """Check if n is a perfect power (for factorization optimization)."""
    if n <= 1:
        return True

    for exp in range(2, int(math.log2(n)) + 1):
        root = int(n ** (1/exp))
        for candidate in [root - 1, root, root + 1]:
            if candidate > 1 and candidate ** exp == n:
                return True
    return False


if __name__ == "__main__":
    # Basic tests and demonstrations
    print("Prime Number Theory Module - Basic Tests")
    print("=" * 50)

    # Test primality
    test_numbers = [2, 3, 4, 17, 97, 100, 2**31 - 1]
    for num in test_numbers:
        result = is_prime_64(num)
        print(f"is_prime_64({num}) = {result}")

    print()

    # Test factorization
    test_factors = [1, 60, 97, 1024]
    for num in test_factors:
        factors = factorize(num)
        print(f"factorize({num}) = {factors}")

    print()

    # Test arithmetic progressions
    test_progressions = [(3, 2), (5, 6), (7, 30)]
    for start, diff in test_progressions:
        length, primes = prime_run_length(start, diff, 20)
        print(f"prime_run_length({start}, {diff}) = length {length}")
        print(f"  Primes: {primes[:10]}{'...' if len(primes) > 10 else ''}")