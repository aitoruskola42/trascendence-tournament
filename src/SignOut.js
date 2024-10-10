console.log('SignOUT.js loaded');

window.initSignOut = function(loadWindowLocationFunc) {
    const signOutButton = document.getElementById('signOutButton');
    if (signOutButton) {
        signOutButton.addEventListener('click', function(event) {
            event.preventDefault();
            handleSignOut(loadWindowLocationFunc);
        });
    } else {
        console.error('Sign Out button not found');
    }
}

async function handleSignOut(loadWindowLocationFunc) {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
        console.error('No refresh token found');
        alert('You are not logged in.');
        return;
    }

    try {
        const response = await fetch('http://localhost:60000/api/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            },
            body: JSON.stringify({ refresh_token: refreshToken })
        });

        if (response.ok) {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            alert('You have been successfully logged out.');
            window.history.pushState({}, "", "/Login");
            if (typeof loadWindowLocationFunc === 'function') {
                loadWindowLocationFunc();
            } else {
                window.location.reload();
            }
        } else {
            const errorData = await response.json();
            console.error('Signout failed:', errorData);
            alert('Sign out failed. Please try again.');
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            window.history.pushState({}, "", "/Login");
            if (typeof loadWindowLocationFunc === 'function') {
                loadWindowLocationFunc();
            } else {
                window.location.reload();
            }            
        }
    } catch (error) {
        console.error('Error during signout:', error);
        alert('An error occurred during sign out. Please try again.');
    }
}

// Esperar a que el DOM esté completamente cargado antes de inicializar
document.addEventListener('DOMContentLoaded', function() {
    initSignOut(window.loadWindowLocation);
});

console.log('Signout end'); 