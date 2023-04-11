const togglePasswordVisibility = () => {
    let eye = document.getElementById('show-hide-password');
    let passwordInput = document.getElementById('password');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eye.src = '/static/images/eye.png'
    } else {
        passwordInput.type = 'password';
        eye.src = '/static/images/eye-crossed-out.png'
    }
}