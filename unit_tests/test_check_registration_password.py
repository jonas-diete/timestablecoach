from app import check_registration_password

def test_non_matching_passwords_return_correct_error_message():
    message = "Passwords don't match. Try again."
    assert check_registration_password("password", "pasword") == message
    assert check_registration_password("Tester", "tester") == message
    assert check_registration_password("Pass_word", "Password") == message
    assert check_registration_password("PASS", "pass") == message

def test_spaces_in_password_return_correct_error_message():
    message = "No spaces allowed in password. Try again."
    assert check_registration_password("pass word", "pass word") == message
    assert check_registration_password("Tester 1", "Tester 1") == message
    assert check_registration_password("  Password", "  Password") == message
    assert check_registration_password("pass word ", "pass word ") == message

def test_too_short_passwords_return_correct_error_message():
    message = "Password must be at least 4 characters long. Try again."
    assert check_registration_password("hi", "hi") == message
    assert check_registration_password("", "") == message
    assert check_registration_password("pas", "pas") == message
    assert check_registration_password("1", "1") == message

def test_too_long_passwords_return_correct_error_message():
    message = "Password cannot be longer than 20 characters. Try again."
    assert check_registration_password("012345678901234567890", "012345678901234567890") == message
    assert check_registration_password("ThisIsMySuper333LongMegaPassword", "ThisIsMySuper333LongMegaPassword") == message

def test_certain_special_characters_return_correct_error_message():
    message = "Password cannot contain any of these characters: <>();"
    assert check_registration_password("<script>hi</script>", "<script>hi</script>") == message
    assert check_registration_password("alert('Boo')", "alert('Boo')") == message
    assert check_registration_password("Not;allowed", "Not;allowed") == message

def test_valid_passwords_return_none():
    assert check_registration_password("AVALIDPASSWORD", "AVALIDPASSWORD") == None
    assert check_registration_password("avalidpassword", "avalidpassword") == None
    assert check_registration_password("aValidPassword", "aValidPassword") == None
    assert check_registration_password("!a_valid--pas$word%", "!a_valid--pas$word%") == None
    assert check_registration_password("1234", "1234") == None
    assert check_registration_password("my_n3w_pa55w0rd", "my_n3w_pa55w0rd") == None