function navigateToSignIn() {
    const signInRoute = {
        template: "../templates/Login.html",
        title: "Sign In | JS SPA Router",
        description: "This is the Sign In page",
    };

    fetch(signInRoute.template)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.text();
        })
        .then(html => {
            document.getElementById("spa-template-content").innerHTML = html;
            document.title = signInRoute.title;
            document.querySelector('meta[name="description"]').setAttribute("content", signInRoute.description);
            window.history.pushState({}, "", "/Login");
        })
        .catch(error => {
            console.error('Error loading Sign In page:', error);
        });
}

document.getElementById('signupForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const first_name = document.getElementById('first_name').value;
    const last_name = document.getElementById('last_name').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }

    const signUpData = {
        username: username,
        email: email,
        password: password,
        first_name: first_name,
        last_name: last_name,
    };

    if (!username || !email || !password || !first_name || !last_name) {
        alert('Please fill in all required fields');
        return;
    }

    const dataJSON = JSON.stringify(signUpData);

    try {
        const response = await fetch('http://localhost:60000/api/users/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: dataJSON,
        });
        
        if (response.ok) {
            const result = await response.json();
            alert('Sign up successful!');
            console.log(result);
            navigateToSignIn();
            // Aquí puedes redirigir al usuario o actualizar la UI
        } else {
            const error = await response.json();
            alert('Error: ' + (error.message || 'Unknown error occurred'));
            console.error('Error response from API:', error);
        }
    } catch (error) {
        console.error('Error sending data:', error);
        alert('Error connecting to the server');
    }
});