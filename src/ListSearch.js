function initListSearch() {
    const searchInput = document.getElementById('search-username');
    const buttonInput = document.getElementById('search-user-form');
    const resultsContainer = document.getElementById('results-list');

    async function fetchUsers() {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch('http://localhost:60000/api/users/list/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const users = await response.json();
            return users;
        } catch (error) {
            console.error('Error al obtener usuarios:', error);
            return [];
        }
    }

    async function searchUsers(query) {
        const users = await fetchUsers();
        const matches = users.filter(user => 
            user.user__username.toLowerCase().includes(query.toLowerCase())
        );
        displayResults(matches);
    }


   function setFriend(userId, user__username) {

        localStorage.setItem('selectedUser', user__username);
        localStorage.setItem('selectedID', userId);
    }


    function displayResults(matches) {
        resultsContainer.innerHTML = '';

        matches.forEach(match => {
            const item = document.createElement('li');
            item.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
            item.textContent = match.user__username;

            const addButton = document.createElement('button');
            addButton.classList.add('btn', 'btn-success', 'btn-sm', 'spa-route');
            addButton.setAttribute('data-path', '/FriendRequest');
            addButton.style.border = '2px solid black'; 
            addButton.style.fontWeight = 'bold';  
            addButton.textContent = 'ADD';
 
            addButton.addEventListener('click', () => setFriend(match.user__id, match.user__username));

             
            item.appendChild(addButton);
            resultsContainer.appendChild(item);
        });
    }

    buttonInput.addEventListener('submit', (event) => {
        event.preventDefault();
        const query = searchInput.value.trim();
        if (query.length > 1) {
            searchUsers(query);
        } else {
            resultsContainer.innerHTML = '';
        }
    });

    searchInput.addEventListener('input', (event) => {
        const query = event.target.value.trim();
        if (query.length > 1) {
            searchUsers(query);
        } else {
            resultsContainer.innerHTML = '';
        }
    });
}

// Asegurarse de que la función de inicialización se ejecute cuando se cargue la página
window.initListSearch = initListSearch;
