import pytest

from src.logic import _make_change
from src.db.models import Card


@pytest.fixture
def denominations():
    return [
        (Card(amount=20),),
        (Card(amount=20),),
        (Card(amount=20),),
        (Card(amount=20),),
        #
        (Card(amount=50),),
        (Card(amount=50),),
        #
        (Card(amount=100),),
        (Card(amount=100),),
        #
        (Card(amount=150),),
        (Card(amount=150),),
        #
        (Card(amount=200),),
        (Card(amount=200),),
        #
        (Card(amount=250),),
        (Card(amount=250),),
        #
        (Card(amount=300),),
        (Card(amount=300),),
        #
        (Card(amount=350),),
        (Card(amount=350),),
        #
        (Card(amount=400),),
        (Card(amount=400),),
        #
        (Card(amount=450),),
        (Card(amount=450),),
        #
        (Card(amount=500),),
        (Card(amount=500),),
        #
        (Card(amount=600),),
        #
        (Card(amount=700),),
        #
        (Card(amount=800),),
        #
        (Card(amount=900),),
        #
        (Card(amount=1000),),
    ]


@pytest.mark.parametrize(
    "amount, expected_result, variants",
    [
        (20, 1, (20,)),
        (40, 2, (20,)),
        (50, 1, (50,)),
        (60, 3, (20,)),
        (70, 2, (50, 20)),
        (80, 4, (20,)),
        (90, 3, (50, 20)),
        (100, 1, (100,)),
        #
        (150, 1, (150,)),
        (200, 1, (200,)),
        (250, 1, (250,)),
        (300, 1, (300,)),
        (350, 1, (350,)),
        (400, 1, (400,)),
        (450, 1, (450,)),
        (500, 1, (500,)),
        (600, 1, (600,)),
        (700, 1, (700,)),
        (800, 1, (800,)),
        (900, 1, (900,)),
        (1000, 1, (1000,)),
    ],
)
def test_make_change_exact(amount, expected_result, variants, denominations):
    res = _make_change(amount, denominations)
    assert len(res) == expected_result
    for card in res:
        assert card.amount in variants


@pytest.fixture
def denominations_double():
    return [
        (Card(amount=20),),
        (Card(amount=20),),
        (Card(amount=20),),
        (Card(amount=20),),
        #
        (Card(amount=50),),
        (Card(amount=50),),
        #
        (Card(amount=100),),
        (Card(amount=100),),
        #
        (Card(amount=150),),
        (Card(amount=150),),
        #
        (Card(amount=200),),
        (Card(amount=200),),
        #
        (Card(amount=250),),
        (Card(amount=250),),
        #
        (Card(amount=300),),
        (Card(amount=300),),
        #
        (Card(amount=350),),
        (Card(amount=350),),
        #
        (Card(amount=400),),
        (Card(amount=400),),
        #
        (Card(amount=450),),
        (Card(amount=450),),
        #
        (Card(amount=500),),
        (Card(amount=500),),
    ]


@pytest.mark.parametrize(
    "amount, expected_result, variants",
    [
        (40, 2, (20,)),
        (70, 2, (50, 20)),
        (600, 2, (500, 100)),
        (700, 2, (500, 200)),
        (800, 2, (500, 300)),
        (900, 2, (500, 400)),
        (1000, 2, (500,)),
    ],
)
def test_make_change_with_two_nominals(amount, expected_result, variants, denominations_double):
    res = _make_change(amount, denominations_double)
    assert len(res) == expected_result
    for card in res:
        assert card.amount in variants


@pytest.fixture
def denominations_double_test():
    return [
        (Card(amount=50),),
        (Card(amount=50),),
        #
        (Card(amount=100),),
        (Card(amount=100),),
    ]


@pytest.mark.parametrize(
    "amount, expected_result, variants",
    [
        (150, 2, (100, 50)),
    ],
)
def test_make_change_with_two_nominals2(amount, expected_result, variants, denominations_double_test):
    print(f"\n{amount=} {denominations_double_test=}\n")
    res = _make_change(amount, denominations_double_test)
    print(f"\n{res[0].amount=}\n")
    print(f"\n{res[1].amount=}\n")
    assert len(res) == expected_result
    for card in res:
        assert card.amount in variants
