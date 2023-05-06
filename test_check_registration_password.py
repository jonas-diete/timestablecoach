from app import check_registration_password

def test_non_matching_passwords_return_correct_error_message():
    message = "Passwords don't match. Try again."
    assert check_registration_password("password", "pasword") == message