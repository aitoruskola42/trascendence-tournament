console.log('Security.js loaded');

async function makeAuthenticatedRequest(url, method = 'GET', body = null) {
    let token = localStorage.getItem('accessToken');
    if (!token) {
        console.error('No access token found');
//        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch(url, {
            method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: body ? JSON.stringify(body) : null,
        });

        if (response.status === 401) {
            // Token expired, attempt to refresh
            token = await refreshToken();
            if (token) {
                return makeAuthenticatedRequest(url, method, body);
            } else {
                throw new Error('Unable to refresh token');
            }
        }

        return response;
    } catch (error) {
        console.error('Error in makeAuthenticatedRequest:', error);
        throw error;
    }
}

// Make sure to expose this function globally
window.makeAuthenticatedRequest = makeAuthenticatedRequest;

// Don't forget to expose this function globally
window.makeAuthenticatedRequest = makeAuthenticatedRequest;

// Don't forget to expose this function globally
window.makeAuthenticatedRequest = makeAuthenticatedRequest;

window.handleSignIn = async function({ username, password }) {
    console.log('HandleSignIn function called from Security.js');

    try {
        const response = await fetch('http://localhost:60000/api/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({username, password}),
        });
        
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data recv:', data);

        if (response.ok) {
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);
            
            // Store user data
            const userData = {
                user_id: data.user_id,
                username: data.username
            };
            localStorage.setItem('userData', JSON.stringify(userData));
            
            console.log('Login successful. Tokens and user data stored in localStorage:', userData);
            
            // Navigate to the profile page
    //        window.history.pushState({}, "", "/Profile");
            window.dispatchEvent(new PopStateEvent('popstate'));
        } else {
            console.error('Login failed', data);
            alert('Login failed: ' + (data.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during login');
    }
};

async function refreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
        console.error('No refresh token found');
        return null;
    }

    try {
        const response = await fetch('http://localhost:60000/api/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({refresh: refreshToken}),
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('accessToken', data.access);
            return data.access;
        } else {
            console.error('Failed to refresh token');
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
//            window.location.href = '/login';
            return null;
        }
    } catch (error) {
        console.error('Error refreshing token:', error);
        return null;
    }
}

async function makeApiRequest(url, method = 'GET', body = null) {
    let token = localStorage.getItem('accessToken');
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };

    try {
        let response = await fetch(url, {method, headers, body: body ? JSON.stringify(body) : null});
        
        if (response.status === 401) {
            token = await refreshToken();
            headers.Authorization = `Bearer ${token}`;
            response = await fetch(url, {method, headers, body: body ? JSON.stringify(body) : null});
        }
        
        if (!response.ok) throw new Error('API request failed');
        
        return await response.json();
    } catch (error) {
        console.error('API request error:', error);
    }
}

// Exportar las funciones que necesitas usar en otros archivos
window.makeAuthenticatedRequest = makeAuthenticatedRequest;
window.makeApiRequest = makeApiRequest;