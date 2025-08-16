def test_equal_or_not():
    """Test if two values are equal."""
    assert 1 == 1, "Values should be equal"
    assert "hello" == "hello", "Strings should be equal"
    assert [1, 2, 3] == [1, 2, 3], "Lists should be equal"
    assert (1, 2) == (1, 2), "Tuples should be equal"
    assert {1, 2} == {2, 1}, "Sets should be equal regardless of order"