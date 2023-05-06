from app import convert_number_to_timestable

def test_2_should_return_twos():
    assert convert_number_to_timestable("2") == "twos"

def test_7_should_return_sevens():
    assert convert_number_to_timestable("7") == "sevens"

def test_4_should_return_fours():
    assert convert_number_to_timestable("4") == "fours"

def test_other_strings_should_return_none():
    assert convert_number_to_timestable("1") == None
    assert convert_number_to_timestable("0") == None
    assert convert_number_to_timestable("13") == None
    assert convert_number_to_timestable("twos") == None
    assert convert_number_to_timestable("-2") == None
    assert convert_number_to_timestable("something_else") == None