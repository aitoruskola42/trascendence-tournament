const resultsContainer = document.getElementById('result-list');

// Simulación de respuestas de usuarios para las solicitudes de amistad
async function fetchMatches() {
    const simulatedResponse = [
        { username: 'Ibantxo' },
        { username: 'Iñigo' },
        { username: 'Juan' },
        { username: 'JoseMari' }
    ];

    // Muestra los resultados simulados en el contenedor
    displayResults(simulatedResponse);
}

// Función para mostrar los resultados en el HTML
function displayResults(matches) {
    // Limpia el contenedor de resultados
    resultsContainer.innerHTML = '';

    // Itera sobre las coincidencias y crea un elemento HTML para cada una
    matches.forEach(match => {
        const item = document.createElement('li');
        item.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');

        // Añadir el nombre de usuario
        const username = document.createElement('p');
        username.classList.add('mb-0');
        username.textContent = match.username;

        // Crear botón "Accept"
        const acceptButton = document.createElement('button');
        acceptButton.classList.add('btn', 'btn-primary', 'btn-sm', 'spa-route');
        acceptButton.setAttribute('data-path', '/Friends');
        acceptButton.style.border = 'solid black'; 
        acceptButton.style.fontWeight = 'bold';  
        acceptButton.textContent = 'Accept';

        // Crear botón "Cancel"
        const cancelButton = document.createElement('button');
        cancelButton.classList.add('btn', 'btn-danger', 'btn-sm', 'spa-route');
        cancelButton.setAttribute('data-path', '/Friends');
        cancelButton.style.border = 'solid black'; 
        cancelButton.style.fontWeight = 'bold';  
        cancelButton.textContent = 'Cancel';

        // Contenedor de botones
        const buttonContainer = document.createElement('div');
        buttonContainer.classList.add('d-flex', 'gap-2'); // Para dar espacio entre los botones
        buttonContainer.appendChild(acceptButton);
        buttonContainer.appendChild(cancelButton);

        // Añadir nombre de usuario y botones al item
        item.appendChild(username);
        item.appendChild(buttonContainer);

        // Añadir el item a la lista de resultados
        resultsContainer.appendChild(item);
    });
}

// Llamar a la función para mostrar los resultados simulados
fetchMatches();
