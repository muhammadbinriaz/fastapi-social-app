import pytest
from app.test_calculations import add

@pytest.mark.parametrize("num1, num2, expected", [
  (3, 2, 5),
  (7, 1, 8),
  (12, 4, 16)
])

def testing_add(num1, num2, expected):
  assert add(num1, num2) == expected


  pass