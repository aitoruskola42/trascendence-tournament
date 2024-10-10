// Friends.js

function initFriendsWait() {
    console.log("Initializing Friends Wait page");

    // Usar let en lugar de const para permitir reasignación
    let resultsContainer = document.getElementById('results-list');

    async function fetchFriends() {
        const token = localStorage.getItem("accessToken");
        console.log("Access Token:", token); // Log the token
        
        try {
            const response = await fetch('http://localhost:60000/api/friends/get_friends_wait/', {
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

    async function removeFriendWait(friendId) {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`http://localhost:60000/api/friends/remove-wait/${friendId}/`, {
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
            listItem.classList.add('list-group-item', 'd-flex', 'justify-content-center', 'align-items-center');

            // Parte izquierda con el botón de eliminar y el nombre del amigo
            const leftDiv = document.createElement('div');
            leftDiv.classList.add('d-flex', 'justify-content-center');

            const friendName = document.createElement('p');
            friendName.classList.add('mb-0', 'text-center',);
            friendName.textContent = friend.username;

            leftDiv.appendChild(friendName);

            

            // Añadir las dos partes al list item
            listItem.appendChild(leftDiv);
          

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
window.initFriendsWait = initFriendsWait;