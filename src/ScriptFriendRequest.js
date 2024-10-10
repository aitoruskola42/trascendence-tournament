
function initScriptFriendRequest() {
    console.log("Initializing script Friends requests");

    const selectedUser = localStorage.getItem('selectedUser');
    const selectedId = localStorage.getItem('selectedID');
    document.getElementById('friend-name').textContent = selectedUser;
    const boton = document.getElementById('yes-botton');

    boton.addEventListener('click', function() {
        addFriendWaiting(selectedId);
        doFetchRequestPending(selectedId);
    });

    async function doFetchRequestPending(selectedId) {

        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch('http://localhost:60000/api/friends/add_friends_request/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ friend_id: selectedId })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result_do = await response.json();
            console.log("result_do", result_do);
            alert(result_do.message);
        } catch (error) {
            console.error('Error al añadir amigo:', error);
            alert('No se pudo añadir el amigo');
        } 
    }

    async function addFriendWaiting(selectedId) {

        const token = localStorage.getItem("accessToken");
        console.log(token);
        try {
            const response = await fetch('http://localhost:60000/api/friends/add_friends_wait/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ friend_id: selectedId })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            alert(result.message);

        } catch (error) {
            console.error('Error al añadir amigo:', error);
            alert('No se pudo añadir el amigo');
        }
    }
}

window.initScriptFriendRequest = initScriptFriendRequest;