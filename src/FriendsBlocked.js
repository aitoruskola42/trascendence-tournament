// Friends.js

function initFriendsBlocked() {
    console.log("Initializing Friends Wait page");

    // Usar let en lugar de const para permitir reasignación
    let resultsContainer = document.getElementById('results-list');

    async function fetchFriends() {
        const token = localStorage.getItem("accessToken");
        console.log("Access Token:", token); // Log the token
        
        try {
            const response = await fetch('http://localhost:60000/api/friends/get_friends_blocked/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
            });
    
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Error response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }
    
            const data = await response.json();
            console.log("Received data:", data); // Log the received data
            return data.friends;
        } catch (error) {
            console.error('Error al obtener amigos:', error);
            return [];
        }
    }

    async function removeFriendBlocked(friendId) {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`http://localhost:60000/api/friends/remove-blocked/${friendId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return true;
        } catch (error) {
            console.error('Error al eliminar amigo:', error);
            return false;
        }
    }

    function displayResults(friends) {
        if (!resultsContainer) {
            console.error("Results container not found");
            return;
        }
        resultsContainer.innerHTML = '';

        friends.forEach(friend => {
            const listItem = document.createElement('li');
            listItem.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');

            // Parte izquierda con el botón de eliminar y el nombre del amigo
            const leftDiv = document.createElement('div');
            leftDiv.classList.add('d-flex', 'align-items-center');

            const friendName = document.createElement('p');
            friendName.classList.add('mb-0');
            friendName.textContent = friend.username;

            leftDiv.appendChild(friendName);

            // Parte derecha con los botones de "Chat" y "Match"
            const rightDiv = document.createElement('div');
            rightDiv.classList.add('d-flex', 'justify-content-end');

            const chatButton = document.createElement('button');
            chatButton.classList.add('btn', 'btn-success', 'btn-sm', 'me-2', 'spa-route');
            chatButton.setAttribute('data-path', '/Chat');
            chatButton.style.border = 'solid black';
            chatButton.style.width = '60px';
            chatButton.innerHTML = '<b class="spa-route" data-path="/Chat">Yes</b>';

            const matchButton = document.createElement('button');
            matchButton.classList.add('btn', 'btn-danger', 'btn-sm', 'text-white', 'spa-route');
            matchButton.setAttribute('data-path', '/LocalMultiplayer');
            matchButton.style.border = 'solid black';
            matchButton.style.width = '60px';
            matchButton.innerHTML = '<b class="spa-route" data-path="/Chat">No</b>';

            rightDiv.appendChild(chatButton);
            rightDiv.appendChild(matchButton);

            // Añadir las dos partes al list item
            listItem.appendChild(leftDiv);
            listItem.appendChild(rightDiv);

            // Añadir el list item al contenedor de resultados
            resultsContainer.appendChild(listItem);
        });
    }

    // Cargar amigos inmediatamente
    fetchFriends().then(friends => {
        console.log("Friends fetched:", friends);
        displayResults(friends);
    });
}

// Exponer la función de inicialización globalmente
window.initFriendsBlocked = initFriendsBlocked;