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