'use strict'

import { initializeGame, terminateGame } from "./LocalMultiplayer.js"
import { initializeGameIA, terminateGameIA } from "./SinglePlayerIA.js"
import { initSignIn } from './SignIn.js';


function isUserLoggedIn() {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        return false;
    }

    // Decodificar el token
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3) {
        return false; // Token inválido
    }

    try {
        const payload = JSON.parse(atob(tokenParts[1]));
        const expirationTime = payload.exp * 1000; // Convertir a milisegundos
        const currentTime = Date.now();

        if (currentTime >= expirationTime) {
            // Token expirado
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            return false;
        }

        return true; // Token válido y no expirado
    } catch (error) {
        console.error('Error al decodificar el token:', error);
        return false;
    }
}

const DEFAULT_PAGE_TITLE = "JS SPA Router";

const ROUTES = {
    404: {
        template: "../templates/404.html",
        title: "404 | " + DEFAULT_PAGE_TITLE,
        description: "Page not found",
    },
    "/Login": {
        template: "../templates/Login.html",
        title: "Sign In | " + DEFAULT_PAGE_TITLE,
        description: "This is the Sign In page",
    },
    "/Logged": {
        template: "../templates/home.html",
        title: "Home logged | " + DEFAULT_PAGE_TITLE,
        description: "This is the logged home page",
    },
    "/Register": {
        template: "../templates/Register.html",
        title: "Sign Up | " + DEFAULT_PAGE_TITLE,
        description: "This is the Sign Up page",
    },
    "/": {
        template: "../templates/NoLogHome.html",
        title: "Home | " + DEFAULT_PAGE_TITLE,
        description: "This is the home page",
    },
    "/Profile": {
        template: "../templates/Profile.html",
        title: "Profile | " + DEFAULT_PAGE_TITLE,
        description: "This is the Profile page",
        script: "./src/Profile.js"
    },
    "/SignOut": {
        template: "../templates/SignOut.html",
        title: "Sign Out | " + DEFAULT_PAGE_TITLE,
        description: "This is the Sign Out page",
        script: "./src/SignOut.js"
    },
    "/LocalMultiplayer": {
        template: "../templates/localGame.html",
        title: "Local Game | " + DEFAULT_PAGE_TITLE,
        description: "This is the Pong Local Multiplayer Game",
    },
    "/Tournament": {
        template: "../templates/Tournament.html",
        title: "Tournament | " + DEFAULT_PAGE_TITLE,
        description: "This is the Tournament page for the Pong Game",
    },
    "/TournamentInterface": {
        template: "../templates/TournamentInterface.html",
        title: "Tournaments | " + DEFAULT_PAGE_TITLE,
        description: "This is the Tournaments page for the Pong Game",
    },
    "/SinglePlayerIA": {
        template: "../templates/localGame.html",
        title: "Single Game | " + DEFAULT_PAGE_TITLE,
        description: "This is the Single Game page for the Pong Game",
    },
    "/Friends": {
        template: "../templates/Friends.html",
        title: "Friends | " + DEFAULT_PAGE_TITLE,
        description: "This is the Friends page for the Pong Game",
        script: "./src/Friends.js"  // Añade esta línea
    },
    "/FriendsWait": {
        template: "../templates/FriendsWait.html",
        title: "Friends Waiting | " + DEFAULT_PAGE_TITLE,
        description: "This is the Friends Waiting page for the Pong Game",
        script: "./src/FriendsWait.js"  // Añade esta línea

    },    
    "/FriendsBlocked": {
        template: "../templates/FriendsBlocked.html",
        title: "Friends Blocked | " + DEFAULT_PAGE_TITLE,
        description: "This is the Friends Blocked page for the Pong Game",
        script: "./src/FriendsBlocked.js"  // Añade esta línea

    },    
    "/FriendsRequest": {
        template: "../templates/FriendsRequest.html",
        title: "Friends Request | " + DEFAULT_PAGE_TITLE,
        description: "This is the Friends request for the Pong Game",
        script: "./src/FriendsRequest.js"  // Añade esta línea

    },    
    "/FriendRequest": {
        template: "../templates/FriendRequest.html",
        title: "FriendRequest | " + DEFAULT_PAGE_TITLE,
        description: "This is the FriendRequest page for the Pong Game",
    },
    "/DeleteFriend": {
        template: "../templates/DeleteFriend.html",
        title: "Delete Friends | " + DEFAULT_PAGE_TITLE,
        description: "This is the Delete Friends page for the Pong Game",
    },
    "/DeleteFriendBlocked": {
        template: "../templates/DeleteFriendBlocked.html",
        title: "Delete Friends | " + DEFAULT_PAGE_TITLE,
        description: "This is the Delete Friends Blocked page for the Pong Game",
    },
    "/DeleteFriendRequest": {
        template: "../templates/DeleteFriendRequest.html",
        title: "Delete Friends | " + DEFAULT_PAGE_TITLE,
        description: "This is the Delete Friends Request page for the Pong Game",
    },
    "/DeleteFriendWaiting": {
        template: "../templates/DeleteFriendRequest.html",
        title: "Delete Friends | " + DEFAULT_PAGE_TITLE,
        description: "This is the Delete Friends Waiting page for the Pong Game",
    },
    "/ListSearch": {
        template: "../templates/ListSearch.html",
        title: "ListSearch | " + DEFAULT_PAGE_TITLE,
        description: "This is the ListSearch page for the Pong Game",
    },
    "/Chat": {
        template: "../templates/Chat.html",
        title: "Chat | " + DEFAULT_PAGE_TITLE,
        description: "This is the Chat page for the Pong Game",
    },
    "/MatchHistory": {
        template: "../templates/MatchHistory.html",
        title: "Match History | " + DEFAULT_PAGE_TITLE,
        description: "This is the Match History page for the Pong Game",
    },
    "/RequestPending": {
        template: "../templates/RequestPending.html",
        title: "Request Pending | " + DEFAULT_PAGE_TITLE,
        description: "This is the Request Pending page for the Pong Game",
    }
};

window.onpopstate = () => {
    handleQueryParams();
    loadWindowLocation();
};

window.onload = () => {
    handleQueryParams();
    loadWindowLocation();
};
document.addEventListener("click", (event) => {
    if (!event.target.matches(".spa-route"))
        return;
    navigationEventHandler(event);
});


function navigationEventHandler(event) {
    event.preventDefault();
    const path = event.target.dataset.path || event.target.href;
    window.history.pushState({}, "", path);
    loadWindowLocation();
}

function handleOAuthRedirect() {
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    const accessToken = params.get('access');
    const refreshToken = params.get('refresh');
    const userData = params.get('user');
    const oauth2fa = params.get('oauth2fa');

    if (oauth2fa) {
        showOAuth2FAVerification(oauth2fa);
    } else if (accessToken && refreshToken && userData) {
        localStorage.setItem('accessToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);
        localStorage.setItem('userData', userData);
//        window.location.href = '/profile';
    } else {
//        console.error('Missing OAuth data in URL');
    }
}

function showOAuth2FAVerification(userId) {
    console.log("Showing 2FA verification for user:", userId);
    const verificationForm = `
        <div class="container mt-5">
            <div class="card mx-auto mb-4 border-dark" style="max-width: 500px;">
                <div class="card-header text-center bg-dark" style="color: #f6f8fa;">
                    <h5><b>Two-Factor Authentication</b></h5>
                </div>
                <div class="card-body">
                    <form id="oauth2faForm">
                        <div class="mb-3">
                            <label for="twoFACode" class="form-label">Enter 2FA Code</label>
                            <input type="text" class="form-control" id="twoFACode" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Verify</button>
                    </form>
                </div>
            </div>
        </div>
    `;
    document.getElementById('spa-template-content').innerHTML = verificationForm;

    document.getElementById('oauth2faForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const code = document.getElementById('twoFACode').value;
        console.log("Submitting 2FA code:", code);
        try {
            const response = await fetch('http://localhost:60000/api/oauth-2fa-verify/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code, user_id: userId }),
            });
            console.log("2FA verification response:", response);
            const data = await response.json();
            console.log("2FA verification data:", data);

            if (response.ok) {
                localStorage.setItem('accessToken', data.access);
                localStorage.setItem('refreshToken', data.refresh);

                // Almacenar la información del usuario
                localStorage.setItem('user', JSON.stringify(data.user));

                // Redirigir al usuario a la página principal o al dashboard
//                window.location.href = '/profile';
            } else {
                alert('Invalid 2FA code: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error during 2FA verification:', error);
            alert('An error occurred during 2FA verification');
        }
    });
}

// Asegúrate de que esta función se ejecute cuando la página se cargue
window.onload = function() {
    handleOAuthRedirect();
    loadWindowLocation();
};


async function makeAuthenticatedRequest(url, method = 'GET', body = null) {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    const response = await fetch(url, {
        method,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : null,
    });

    if (response.status === 401) {
        // Token expirado, intentar refrescar
        const refreshed = await refreshToken();
        if (refreshed) {
            return makeAuthenticatedRequest(url, method, body);
        } else {
            window.location.href = '/login';
        }
    }

    return response;
}

async function refreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) return false;

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
        return true;
    }

    return false;
}

function handleQueryParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const oauth2fa = urlParams.get('oauth2fa');
    
    // También revisar el hash por si el parámetro viene ahí
    const hashParams = new URLSearchParams(window.location.hash.slice(1));
    const oauth2faHash = hashParams.get('oauth2fa');

    if (oauth2fa || oauth2faHash) {
        const userId = oauth2fa || oauth2faHash;
        console.log("2FA required for user:", userId);
        showOAuth2FAVerification(userId);
        // Limpiar los parámetros de la URL
        window.history.replaceState({}, document.title, window.location.pathname);
        return true; // Indica que se manejó el 2FA
    }
    return false; // Indica que no se manejó el 2FA
}

window.addEventListener('load', handleQueryParams);
window.addEventListener('popstate', handleQueryParams);



async function loadWindowLocation() {

    if (handleQueryParams()) {
        return;
    }
    handleQueryParams();
    const location = window.location;
    const locationPath = (location.length === 0) ? "/" : location.pathname;
    const route = ROUTES[locationPath] || ROUTES["404"];
    
    try {
        const response = await fetch(route.template);
        if (!response.ok) throw new Error('Network response was not ok');
        const html = await response.text();
    
        document.getElementById("spa-template-content").innerHTML = html;
        document.title = route.title;
        document.querySelector('meta[name="description"]').setAttribute("content", route.description);
    
        terminateGame();
        terminateGameIA();

        if (locationPath === "/LocalMultiplayer") {
            initializeGame();
        }

        if (locationPath === "/") {
            if (isUserLoggedIn()) {
                window.history.replaceState({}, "", "/Logged");
                loadWindowLocation();
                return; // Importante: salir de la función después de la redirección
            } 
        }        

		if (locationPath === "/Profile") {
			const script = document.createElement('script');
			script.src = './src/Profile.js';
			script.onload = function() {
				if (typeof window.initProfile === 'function') {
					window.initProfile();
				} else {
					console.error('initProfile function not found');
				}
			};
			document.body.appendChild(script);
		}	

        if (locationPath === "/Register") {
            const script = document.createElement('script');
            script.src = './src/Register.js';
            document.body.appendChild(script);
        }
        if (locationPath === "/Login") {
            initSignIn();
        }

        if (locationPath === "/ListSearch") {
            const script = document.createElement('script');
            script.src = './src/ListSearch.js';
            script.onload = function() {
                if (typeof window.initListSearch === 'function') {
                    window.initListSearch();
                }
            };
            document.body.appendChild(script);
        }

        if (locationPath === "/Friends") {
            const script = document.createElement('script');
            script.src = './src/Friends.js';
            script.onload = function() {
                // Asegurarse de que la función de inicialización de friends se ejecuta
                if (typeof window.initFriends === 'function') {
                    window.initFriends();
                }
            };
            document.body.appendChild(script);
        }
        if (locationPath === "/FriendsWait") {
            const script = document.createElement('script');
            script.src = './src/FriendsWait.js';
            script.onload = function() {
                // Asegurarse de que la función de inicialización de friends se ejecuta
                if (typeof window.initFriendsWait === 'function') {
                    window.initFriendsWait();
                }
            };
            document.body.appendChild(script);
        }
        if (locationPath === "/FriendsWait") {
            const script = document.createElement('script');
            script.src = './src/FriendsWait.js';
            script.onload = function() {
                // Asegurarse de que la función de inicialización de friends se ejecuta
                if (typeof window.initFriendsWait === 'function') {
                    window.initFriendsWait();
                }
            };
            document.body.appendChild(script);
        }
        if (locationPath === "/FriendsBlocked") {
            const script = document.createElement('script');
            script.src = './src/FriendsBlocked.js';
            script.onload = function() {
                // Asegurarse de que la función de inicialización de friends se ejecuta
                if (typeof window.initFriendsBlocked === 'function') {
                    window.initFriendsBlocked();
                }
            };
            document.body.appendChild(script);
        }
        if (locationPath === "/FriendsRequest") {
            const script = document.createElement('script');
            script.src = './src/FriendsRequest.js';
            script.onload = function() {
                // Asegurarse de que la función de inicialización de friends se ejecuta
                if (typeof window.initFriendsRequest === 'function') {
                    window.initFriendsRequest();
                }
            };
            document.body.appendChild(script);
        }
        if (locationPath === "/FriendRequest") {
            const script = document.createElement('script');
            script.src = './src/ScriptFriendRequest.js';
            script.onload = function() {
                // Asegurarse de que la función de inicialización de friends se ejecuta
                if (typeof window.initScriptFriendRequest === 'function') {
                    window.initScriptFriendRequest();
                }
            };
            document.body.appendChild(script);
        }
        if (locationPath === "/RequestPending") {
            const script = document.createElement('script');
            script.src = './src/RequestPending.js';
            document.body.appendChild(script);
        }        

        if (locationPath === "/SignOut") {
            const script = document.createElement('script');
            script.src = './src/SignOut.js';
            script.onload = function() {
                if (typeof window.initSignOut === 'function') {
                    window.initSignOut(loadWindowLocation);
                }
            };
            document.body.appendChild(script);
        }
        if (route.script) {
            const script = document.createElement('script');
            script.src = route.script;
            script.onload = function() {
                if (typeof window.initProfile === 'function') {
                    window.initProfile();
                }
                else if (typeof window[`init${route.title.split(' | ')[0]}`] === 'function') {
                    window[`init${route.title.split(' | ')[0]}`]();
                }
            };
            document.body.appendChild(script);
        }
        if (locationPath === "/SinglePlayerIA") {
            initializeGameIA();
        }
        const loginLink = document.getElementById("login-link");
        const registerLink = document.getElementById("register-link");
        const profileLink = document.getElementById("profile-link");
        const signoutLink = document.getElementById("signout-link");
        const friendsLink = document.getElementById("friends-link"); // Añadido
        const ListSearchLink = document.getElementById("ListSearch-link"); // Añadido

		const retrievedToken = localStorage.getItem("accessToken");
        // Lógica para mostrar u ocultar elementos del menú
        if (/*Navbar === 1*/ retrievedToken) {
            // Mostrar Login y Register, ocultar Profile y Sign Out
            if (loginLink) loginLink.parentElement.style.display = 'none';
            if (registerLink) registerLink.parentElement.style.display = 'none';
            if (profileLink) profileLink.parentElement.style.display = '';
            if (signoutLink) signoutLink.parentElement.style.display = '';
            if (friendsLink) friendsLink.style.display = ''; // Añadido
            if (ListSearchLink) ListSearchLink.style.display = ''; // Añadido

        } else if (/*Navbar === 0*/!retrievedToken) {
            // Mostrar Profile y Sign Out, ocultar Login y Register
            if (loginLink) loginLink.parentElement.style.display = '';
            if (registerLink) registerLink.parentElement.style.display = '';
            if (profileLink) profileLink.parentElement.style.display = 'none';
            if (signoutLink) signoutLink.parentElement.style.display = 'none';
            if (friendsLink) friendsLink.style.display = 'none'; // Añadido
            if (ListSearchLink) ListSearchLink.style.display = 'none'; // Añadido
        }

    } catch (error) {
        console.error('Error fetching template:', error);
    }
}