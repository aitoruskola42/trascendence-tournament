function initProfile() {
    async function loadProfileData() {
        const token = localStorage.getItem('accessToken');
        const userData = JSON.parse(localStorage.getItem('userData'));

        if (!token || !userData) {
            console.error('No token or user data found');
            return;
        }

        try {
            const response = await fetch(`http://localhost:60000/api/users/profile/${userData.user_id}/`, {
                headers: {
                    'Authorization': `Token ${token}`
                }
            });

            if (response.ok) {
                const profileData = await response.json();
                console.log('Profile data:', profileData);

                // Rellenar los campos del formulario
                const usernameField = document.getElementById('username');

                if (usernameField) {
                    usernameField.textContent = profileData.username;
                } else {
                    console.error('Username field not found');
                }


                const joinedField = document.getElementById('date_joined');
                if (joinedField) {
                    joinedField.textContent = profileData.date_joined || ''; // Usa '' si age es null o undefined
                } else {
                    console.error('date_joined field not found');
                }


                /*              const ageField = document.getElementById('age');
                if (ageField) {
                    ageField.value = profileData.age || ''; // Usa '' si age es null o undefined
                } else {
                    console.error('Age field not found');
                } */
                // Añade más campos aquí según tu formulario
            } else {
                console.error('Failed to fetch profile data');
            }
        } catch (error) {
            console.error('Error fetching profile data:', error);
        }
    }

    // Intentar cargar los datos inmediatamente
    loadProfileData();

    // También añadir el listener por si acaso
    document.addEventListener('DOMContentLoaded', loadProfileData);
}

// Exponer la función de inicialización globalmente
window.initProfile = initProfile;

console.log('Profile script loaded');