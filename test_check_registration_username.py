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

def test_too_short_usernames_return_correct_error_message():
    message = "Please enter a longer username."
    assert check_registration_username("L") == message
    assert check_registration_username("a") == message
    assert check_registration_username("9") == message
    assert check_registration_username("0") == message

def test_too_long_usernames_return_correct_error_message():
    message = "Please enter a shorter username."
    assert check_registration_username("MarielouiseSmith") == message
    assert check_registration_username("0123456789012345") == message
    assert check_registration_username("WhatA5illyNam3Th1s1s") == message

def test_usernames_with_special_chars_return_correct_error_message():
    message = "Only letters or numbers allowed for username. Try again."
    assert check_registration_username("James!") == message
    assert check_registration_username("-Julie-") == message
    assert check_registration_username("Bad_Actor") == message
    assert check_registration_username("Rich13(ruler)") == message
    assert check_registration_username("Lisa,Frank") == message
    assert check_registration_username("<script>something</script>") == message