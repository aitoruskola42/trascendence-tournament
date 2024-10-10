console.log('SignIn.js loaded');

export function initSignIn() {
    console.log('Initializing SignIn');
    const signInForm = document.getElementById('signInForm');
    if (signInForm) {
        console.log('Sign in form found, adding event listener');
        signInForm.addEventListener('submit', handleSignIn);
    } else {
        console.error('Sign in form not found. DOM structure:', document.body.innerHTML);
    }
}

async function handleSignIn(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;


    if (!username || !password) {
        alert('Please fill in all fields');
        return;
    }


    try {
        const response = await fetch('http://localhost:60000/api/users/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            const data = await response.json();

            if (data.require_2fa) {
                const twoFactorCode = prompt('Enter your 2FA code:');
                if (twoFactorCode) {
                    const twoFactorResponse = await fetch('http://localhost:60000/api/users/login/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ username, password, two_factor_code: twoFactorCode }),
                    });

                    if (twoFactorResponse.ok) {
                        const twoFactorData = await twoFactorResponse.json();
                        localStorage.setItem('accessToken', twoFactorData.access);
                        localStorage.setItem('refreshToken', twoFactorData.refresh);
                        window.history.pushState({}, "", "/Profile");
                        window.dispatchEvent(new PopStateEvent('popstate'));
                    } else {
                        alert('Invalid 2FA code');
                    }
                }
            } else {
                localStorage.setItem('accessToken', data.access);
                localStorage.setItem('refreshToken', data.refresh);
                window.history.pushState({}, "", "/Profile");
                window.dispatchEvent(new PopStateEvent('popstate'));
                window.dispatchEvent(new Event('locationchange'));
            }
        } else {
            const error = await response.json();
            alert('Error: ' + (error.message || 'Invalid credentials'));
            console.error('Error response from API:', error);
        }
    } catch (error) {
        console.error('Error sending data:', error);
        alert('Error connecting to the server');
    }
}
