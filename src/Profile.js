function loadAvatar(userId) {
    const avatarImage = document.getElementById('avatarImage');
    const avatarUrl = `http://localhost:60000/api/users/avatar/${userId}/?${new Date().getTime()}`;
    console.log('Loading avatar from:', avatarUrl);
    
    avatarImage.src = avatarUrl;
    avatarImage.onerror = function() {
        console.error('Error loading avatar, using default');
        this.src = 'img/avatar.jpg';
        this.onerror = null;
    };
}

async function loadProfileData() {
    console.log('loadProfileData called');
    const token = localStorage.getItem('accessToken');
    if (!token) {
        console.error('No access token found');
        return;
    }

    try {
        const response = await fetch('http://localhost:60000/api/users/profile/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            const profileData = await response.json();
            console.log('Profile data fetched successfully');
            updateProfileUI(profileData);
        } else {
            const errorData = await response.json();
            console.error('Failed to fetch profile data:', errorData);
        }
    } catch (error) {
        console.error('Error fetching profile data:', error);
    } finally {
        console.log('loadProfileData finished');
    }
}

function updateProfileUI(profileData) {

    const avatarImage = document.getElementById('avatarImage');
    if (avatarImage && profileData.avatar_image) {
        avatarImage.src = `http://localhost:60000${profileData.avatar_image}`;
    }

    const usernameField = document.getElementById('username');
    if (usernameField) {
        usernameField.textContent = profileData.username;
    }

    const displayField = document.getElementById('display_name');
    if (displayField) {
        displayField.value = profileData.display_name || '';
    }



    const joinedField = document.getElementById('date_joined');
    if (joinedField) {
        const date = new Date(profileData.date_joined);
        const formattedDate = date.toLocaleString();
        joinedField.textContent = formattedDate;
    }

    const friendField = document.getElementById('friends');
    if (friendField) {
        friendField.value = profileData.friends || '';
    }

    const firstNameField = document.getElementById('first_name');
    if (firstNameField) {
        firstNameField.value = profileData.first_name || '';
    }

    const lastNameField = document.getElementById('last_name');
    if (lastNameField) {
        lastNameField.value = profileData.last_name || '';
    }

    updateTwoFAStatus(profileData.two_factor_enabled);
}

function updateTwoFAStatus(isEnabled) {
    const statusElement = document.getElementById('twoFAStatus');
    const toggleButton = document.getElementById('toggle2FA');
    
    if (statusElement) {
        statusElement.textContent = isEnabled ? '2FA is currently enabled.' : '2FA is currently disabled.';
    }
    if (toggleButton) {
        toggleButton.textContent = isEnabled ? 'Disable 2FA' : 'Enable 2FA';
    }
}

function initProfile() {
    console.log('Initializing Profile');
    const userData = JSON.parse(localStorage.getItem('userData'));
    if (userData && userData.user_id) {
        loadAvatar(userData.user_id);
    }

    loadProfileData();

 



    // Configurar manejadores de eventos
    setup2FAHandlers();
    setupAvatarHandlers(loadProfileData);
    setupFormHandlers();

}

function setup2FAHandlers() {
    const toggleButton = document.getElementById('toggle2FA');
    if (toggleButton) {
        toggleButton.addEventListener('click', async () => {
            const isCurrentlyEnabled = toggleButton.textContent === 'Disable 2FA';
            const url = isCurrentlyEnabled ? 'disable-2fa/' : 'enable-2fa/';
            
            try {
                const response = await fetch(`http://localhost:60000/api/${url}`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const result = await response.json();
                    if (!isCurrentlyEnabled && result.qr_code) {
                        showQRCode(result.qr_code);
                    } else {
                        updateTwoFAStatus(!isCurrentlyEnabled);
                        document.getElementById('qrCodeContainer').style.display = 'none';
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
}

function showQRCode(qrCode) {
    const qrCodeContainer = document.getElementById('qrCodeContainer');
    qrCodeContainer.innerHTML = `
        <img src="data:image/png;base64,${qrCode}" alt="2FA QR Code">
        <p>Scan this QR code with Google Authenticator app</p>
        <input type="text" id="verificationCode" placeholder="Enter verification code">
        <button id="verifyCode">Verify</button>
    `;
    qrCodeContainer.style.display = 'block';

    document.getElementById('verifyCode').addEventListener('click', verify2FA);
}

async function verify2FA() {
    const code = document.getElementById('verificationCode').value;
    console.log('Attempting to verify 2FA code:', code);  // Añade este log
    try {
        const response = await fetch('http://localhost:60000/api/verify-2fa/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code })
        });

        console.log('2FA verification response status:', response.status);  // Añade este log

        if (response.ok) {
            alert('2FA verified successfully!');
            updateTwoFAStatus(true);
            document.getElementById('qrCodeContainer').style.display = 'none';
        } else {
            const errorData = await response.json();
            console.error('2FA verification failed:', errorData);  // Añade este log
            alert('Invalid verification code. Please try again.');
        }
    } catch (error) {
        console.error('Error verifying 2FA:', error);
        alert('An error occurred while verifying 2FA. Please try again.');
    }
}

function setupAvatarHandlers(loadProfileDataCallback) {
    const changeAvatarBtn = document.getElementById('changeAvatarBtn');
    const avatarInput = document.getElementById('avatarInput');

    if (changeAvatarBtn && avatarInput) {
        if (!changeAvatarBtn.hasAttribute('data-listener-attached')) {
            changeAvatarBtn.addEventListener('click', () => avatarInput.click());
            changeAvatarBtn.setAttribute('data-listener-attached', 'true');
        }

        if (!avatarInput.hasAttribute('data-listener-attached')) {
            avatarInput.addEventListener('change', function(event) {
                uploadAvatar.call(this, loadProfileDataCallback);
            });
            avatarInput.setAttribute('data-listener-attached', 'true');
        }
    }
}

async function uploadAvatar(onSuccessCallback) {
    console.log('uploadAvatar called');

    const file = this.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('avatar_image', file);

        try {
            const response = await fetch('http://localhost:60000/api/users/upload-avatar/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                },
                body: formData
            });

            if (response.ok) {
                console.log('Avatar uploaded successfully');
                if (typeof onSuccessCallback === 'function') {
                    onSuccessCallback();
                }
            } else {
                console.error('Failed to upload avatar:', await response.text());
            }
        } catch (error) {
            console.error('Error uploading avatar:', error);
        }
    }
}

function setupFormHandlers() {
    const changePasswordBtn = document.getElementById('changePasswordBtn');
    const changeProfileBtn = document.getElementById('changeProfilelBtn');
    const submitPasswordChange = document.getElementById('submitPasswordChange');
    const submitProfileChange = document.getElementById('submitProfileChange');

    // Remover los listeners existentes antes de agregar nuevos
    changePasswordBtn.removeEventListener('click', toggleForm);
    changeProfileBtn.removeEventListener('click', toggleForm);
    submitPasswordChange.removeEventListener('click', changePassword);
    submitProfileChange.removeEventListener('click', updateProfile);

    // Agregar nuevos listeners
    changePasswordBtn.addEventListener('click', toggleForm);
    changeProfileBtn.addEventListener('click', toggleForm);
    submitPasswordChange.addEventListener('click', changePassword);
    submitProfileChange.addEventListener('click', updateProfile);
}

function toggleForm(event) {
    event.preventDefault();
    event.stopPropagation();
    
    const passwordForm = document.getElementById('changePasswordForm');
    const profileForm = document.getElementById('changeProfileForm');
    const passwordBtn = document.getElementById('changePasswordBtn');
    const profileBtn = document.getElementById('changeProfilelBtn');

    // Determinar qué botón se pulsó
    const clickedButton = event.currentTarget;
    const isPasswordBtn = clickedButton.id === 'changePasswordBtn';

    console.log('Button clicked:', clickedButton.id);

    // Ocultar ambos formularios
    passwordForm.style.display = 'none';
    profileForm.style.display = 'none';

    // Mostrar el formulario correspondiente
    if (isPasswordBtn) {
        passwordForm.style.display = 'block';
        passwordBtn.classList.add('active');
        profileBtn.classList.remove('active');
        console.log('Showing password form');
    } else {
        profileForm.style.display = 'block';
        profileBtn.classList.add('active');
        passwordBtn.classList.remove('active');
        console.log('Showing profile form');
    }

    console.log('Toggled form:', isPasswordBtn ? 'Password' : 'Profile');
}

async function changePassword(event) {
    event.preventDefault();
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmNewPassword = document.getElementById('confirmNewPassword').value;

    if (newPassword !== confirmNewPassword) {
        alert('New passwords do not match!');
        return;
    }

    try {
        const response = await fetch('http://localhost:60000/api/users/change-password/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });

        if (response.ok) {
            alert('Password changed successfully!');
            document.getElementById('changePasswordForm').reset();
        } else {
            const errorData = await response.json();
            alert(`Failed to change password: ${errorData.error}`);
        }
    } catch (error) {
        console.error('Error changing password:', error);
        alert('An error occurred while changing the password.');
    }
}

async function updateProfile(event) {
    event.preventDefault();
    
    // Desactivar el botón para evitar múltiples clics
    const submitButton = event.target;
    submitButton.disabled = true;

    const first_name = document.getElementById('first_name').value;
    const last_name = document.getElementById('last_name').value;
    const friends = document.getElementById('friends').value;
    const display_name = document.getElementById('display_name').value;

    try {
        const response = await fetch('http://localhost:60000/api/users/update-profile/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            },
            body: JSON.stringify({
                first_name,
                last_name,
                friends,
                display_name
            })
        });

        if (response.ok) {
            const updatedData = await response.json();
            console.log('Profile updated successfully:', updatedData);
            alert('Profile updated successfully!');
            loadProfileData();
        } else {
            console.error('Failed to update profile:', await response.text());
            alert('Failed to update profile. Please try again.');
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        alert('An error occurred while updating the profile.');
    } finally {
        // Reactivar el botón
        submitButton.disabled = false;
    }
}

// Exponer la función de inicialización globalmente
window.initProfile = initProfile;

