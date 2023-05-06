from app import check_registration_username

def test_valid_usernames_return_none():
    # testing for names that are very unlikely to exist already in database to make tests pass
    assert check_registration_username("Jales") == None
    assert check_registration_username("jales") == None
    assert check_registration_username("JALES") == None
    assert check_registration_username("ROLERT183") == None
    assert check_registration_username("1531") == None
    assert check_registration_username("Little13Mice") == None
    assert check_registration_username("Pi") == None

def test_too_short_usernames_return_correct_message():
    message = "Please enter a longer username."
    assert check_registration_username("L") == message
    assert check_registration_username("a") == message
    assert check_registration_username("9") == message
    assert check_registration_username("0") == message