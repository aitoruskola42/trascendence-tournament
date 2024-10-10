
function loadAvatar(userId) {
    const avatarImage = document.getElementById('avatarImage');
    const avatarUrl = `http://localhost:60000/api/users/avatar/${userId}/?${new Date().getTime()}`;
    console.log('Loading avatar from:', avatarUrl);
    
    avatarImage.src = avatarUrl;
    avatarImage.onerror = function() {
        console.error('Error loading avatar, using default');
        this.src = 'img/avatar.jpg';
        this.onerror = null;  // Previene bucle infinito si la imagen por defecto también falla
    };
}

function initProfile() {
    console.log('Initializing Profile');
    loadProfileData();

    async function loadProfileData() {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            console.error('No access token found');
            return;
        }
    
        try {
            // Asegúrate de que esta URL apunte a tu backend, no al frontend
            const response = await fetch('http://localhost:60000/api/users/profile/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const profileData = await response.json();
                updateProfileUI(profileData);
            } else {
                console.error('Failed to fetch profile data');
            }
        } catch (error) {
            console.error('Error fetching profile data:', error);
        }
    }

    function updateTwoFAStatus(isEnabled) {
        const statusElement = document.getElementById('twoFAStatus');
        const toggleButton = document.getElementById('toggle2FA');
        
        statusElement.textContent = isEnabled ? '2FA is currently enabled.' : '2FA is currently disabled.';
        toggleButton.textContent = isEnabled ? 'Disable 2FA' : 'Enable 2FA';
    }

function setup2FAHandlers() {
    const toggleButton = document.getElementById('toggle2FA');
    toggleButton.addEventListener('click', async () => {
        const isCurrentlyEnabled = toggleButton.textContent === 'Disable 2FA';
        
        try {
            const response = await fetch('http://localhost:60000/api/' + (isCurrentlyEnabled ? 'disable-2fa/' : 'enable-2fa/'), {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('accessToken'),
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                if (!isCurrentlyEnabled && result.qr_code) {
                    // Mostrar el código QR
                    const qrCodeContainer = document.getElementById('qrCodeContainer');
                    qrCodeContainer.innerHTML = `
                        <img src="data:image/png;base64,${result.qr_code}" alt="2FA QR Code">
                        <p>Scan this QR code with Google Authenticator app</p>
                        <input type="text" id="verificationCode" placeholder="Enter verification code">
                        <button id="verifyCode">Verify</button>
                    `;
                    qrCodeContainer.style.display = 'block';

                    // Configurar el manejador para verificar el código
                    document.getElementById('verifyCode').addEventListener('click', async () => {
                        const code = document.getElementById('verificationCode').value;
                        const verifyResponse = await fetch('http://localhost:60000/api/verify-2fa/', {
                            method: 'POST',
                            headers: {
                                'Authorization': 'Bearer ' + localStorage.getItem('accessToken'),
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ code })
                        });

                        if (verifyResponse.ok) {
                            alert('2FA verified successfully!');
                            updateTwoFAStatus(true);
                            qrCodeContainer.style.display = 'none';
                        } else {
                            alert('Invalid verification code. Please try again.');
                        }
                    });
                } else {
                    // Ocultar el código QR si se está desactivando
                    document.getElementById('qrCodeContainer').style.display = 'none';
                    updateTwoFAStatus(false);
                }
            } else {
                throw new Error('Failed to toggle 2FA');
            }
        } catch (error) {
            console.error('Error toggling 2FA:', error);
            alert('There was an error toggling 2FA. Please try again.');
        }
    });
}
    // Llamar a setup2FAHandlers al final de initProfile
    setup2FAHandlers();
}


    function updateProfileUI(profileData) {
        const usernameField = document.getElementById('username');
        if (usernameField) {
            usernameField.textContent = profileData.username;
        } else {
            console.error('Username field not found');
        }
    
        const joinedField = document.getElementById('date_joined');
        if (joinedField) {
            joinedField.textContent = profileData.date_joined || '';
        } else {
            console.error('date_joined field not found');
        }
    
        // Añadir botones para 2FA
        const twoFAContainer = document.createElement('div');
        twoFAContainer.id = 'two-fa-container';
        
        const enable2FABtn = document.createElement('button');
        enable2FABtn.textContent = 'Enable 2FA';
        enable2FABtn.classList.add('btn', 'btn-primary', 'mr-2');
        enable2FABtn.addEventListener('click', enable2FA);
        
        const disable2FABtn = document.createElement('button');
        disable2FABtn.textContent = 'Disable 2FA';
        disable2FABtn.classList.add('btn', 'btn-danger');
        disable2FABtn.addEventListener('click', disable2FA);

        
        const profileContainer = document.querySelector('#profile-container');
        if (profileContainer) {
            profileContainer.appendChild(twoFAContainer);
        } else {
            console.error('Profile container not found');
        }
    }

    // Cambiar el avatar cuando se selecciona una imagen
    const changeAvatarBtn = document.getElementById('changeAvatarBtn');

    const avatarInput = document.getElementById('avatarInput');
    const avatarImage = document.getElementById('avatarImage');

    if (changeAvatarBtn && avatarInput && avatarImage) {
        changeAvatarBtn.addEventListener('click', function () {
            avatarInput.click();
        });

        avatarInput.addEventListener('change', function () {
            const file = avatarInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    avatarImage.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

 
    // Manejadores para mostrar/ocultar formularios de cambio de contraseña y correo electrónico
    const changePasswordBtn = document.getElementById('changePasswordBtn');
    const changePasswordForm = document.getElementById('changePasswordForm');
    const changeEmailBtn = document.getElementById('changeEmailBtn');
    const changeEmailForm = document.getElementById('changeEmailForm');

    if (changePasswordBtn && changePasswordForm) {
        changePasswordBtn.addEventListener('click', function() {
            changePasswordForm.classList.toggle('collapse');
        });
    }

    if (changeEmailBtn && changeEmailForm) {
        changeEmailBtn.addEventListener('click', function() {
            changeEmailForm.classList.toggle('collapse');
        });
    }

    // Manejar el evento de envío del formulario de cambio de contraseña
    const submitPasswordChange = document.getElementById('submitPasswordChange');
    if (submitPasswordChange) {
        submitPasswordChange.addEventListener('click', function() {
            const currentPassword = document.getElementById('currentPassword').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmNewPassword = document.getElementById('confirmNewPassword').value;

            if (newPassword !== confirmNewPassword) {
                alert('New passwords do not match!');
                return;
            }

            // Aquí deberías implementar la lógica para cambiar la contraseña
            alert('Password changed successfully!');
        });
    }

    // Manejar el evento de envío del formulario de cambio de correo electrónico
    const submitEmailChange = document.getElementById('submitEmailChange');
    if (submitEmailChange) {
        submitEmailChange.addEventListener('click', function() {
            const currentEmail = document.getElementById('currentEmail').value;
            const newEmail = document.getElementById('newEmail').value;
            const confirmNewEmail = document.getElementById('confirmNewEmail').value;

            if (newEmail !== confirmNewEmail) {
                alert('New emails do not match!');
                return;
            }

            // Aquí deberías implementar la lógica para cambiar el correo electrónico
            alert('Email changed successfully!');
        });
    }

    async function enable2FA() {
        try {
            const response = await fetch('http://localhost:60000/api/enable-2fa/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                    'Content-Type': 'application/json'
                }
            });
    
            if (response.ok) {
                const data = await response.json();
                // Muestra el código QR al usuario
                const qrCode = document.createElement('img');
                qrCode.src = `data:image/png;base64,${data.qr_code}`;
                const twoFAContainer = document.getElementById('two-fa-container');
                if (twoFAContainer) {
                    twoFAContainer.appendChild(qrCode);
                }
                alert('Scan the QR code with your authenticator app');
            } else {
                alert('Failed to enable 2FA');
            }
        } catch (error) {
            console.error('Error enabling 2FA:', error);
            alert('An error occurred while enabling 2FA');
        }
    }

    async function disable2FA() {
        try {
            const response = await fetch('http://localhost:60000/api/disable-2fa/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                alert('2FA has been disabled');
                const twoFAContainer = document.getElementById('two-fa-container');
                if (twoFAContainer) {
                    const qrCode = twoFAContainer.querySelector('img');
                    if (qrCode) {
                        qrCode.remove();
                    }
                }
            } else {
                alert('Failed to disable 2FA');
            }
        } catch (error) {
            console.error('Error disabling 2FA:', error);
            alert('An error occurred while disabling 2FA');
        }
    }


// Exponer la función de inicialización globalmente
window.initProfile = initProfile;

console.log('Profile script loaded');

