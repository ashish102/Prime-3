import pytest

from prime.nt import is_pseudoprime, is_prime_64


def test_pseudoprime_base2():
    # 341 = 11 * 31 is a Fermat pseudoprime to base 2
    n = 341
    assert not is_prime_64(n)
    assert is_pseudoprime(n, base=2)


def test_pseudoprime_carmichael_number_multiple_bases():
    # 561 is a Carmichael number; pseudoprime to several bases
    n = 561
    assert not is_prime_64(n)
    assert is_pseudoprime(n, base=2)
    assert is_pseudoprime(n, base=4)
    assert is_pseudoprime(n, base=5)


def test_pseudoprime_requires_coprime_base():
    # base sharing factor should not count as pseudoprime
    assert not is_pseudoprime(21, base=3)


def test_pseudoprime_detects_prime_numbers():
    assert not is_pseudoprime(97, base=2)


def test_pseudoprime_float_inputs():
    # Accept float inputs that are integer-valued
    assert is_pseudoprime(341.0, base=2.0)


def test_pseudoprime_invalid_base():
    with pytest.raises(ValueError):
        is_pseudoprime(341, base=1)
