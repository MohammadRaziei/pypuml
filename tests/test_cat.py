from pypuml import cat


def test_cat_concatenates_sequences():
    assert cat([1, 2], [3, 4]) == [1, 2, 3, 4]
