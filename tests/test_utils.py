from cmcb import utils


def test_string_from_countable():
    some_seconds = utils.get_string_from_countable('second', 5)
    assert some_seconds == '5 seconds'
