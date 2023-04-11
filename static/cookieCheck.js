const cookieCheck = (cookies) => {
    // if cookies had already been accepted before
    if (cookies == 'yes') {
        // Hiding cookie notification
        document.getElementById('cookie_consent').style.display='none';
        
    } else {
        document.getElementById('accept_button').addEventListener('click', () => {
        
            // Hiding cookie notification
            document.getElementById('cookie_consent').style.display='none';

            // Sending data that cookies have been accepted
            var data = new FormData();
            data.append('accepted', 'yes');
            var request = new XMLHttpRequest();
            request.open('POST', '/login');
            request.send(data);
        })
    }
}