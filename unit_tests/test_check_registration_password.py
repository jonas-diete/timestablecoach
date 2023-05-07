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

def test_password_at_least_4_chars():
    message = "Password must be at least 4 characters long. Try again."
    assert check_registration_password("hi", "hi") == message
    assert check_registration_password("", "") == message
    assert check_registration_password("pas", "pas") == message
    assert check_registration_password("1", "1") == message