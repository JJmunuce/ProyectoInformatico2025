document.addEventListener('DOMContentLoaded', () => {
    // Referencias al DOM
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    // --- LÓGICA DE LOGIN (CONECTADA AL BACKEND) ---
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const role = document.getElementById('role-select').value; // 'gestor' o 'cliente'

            if (!role) {
                alertModal("Por favor, selecciona tu rol.", 'error');
                return;
            }

            setLoading('login', true);

            try {
                // 1. Petición al Backend Real
                const response = await fetch('http://localhost:5000/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    // Tu backend espera 'username' y 'password'
                    body: JSON.stringify({ 
                        username: email, 
                        password: password 
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // 2. Guardar datos reales en LocalStorage
                    // El backend devuelve: id_usuario, nombre, correo, id_negocio, token
                    localStorage.setItem('activeUserId', data.id_usuario);
                    localStorage.setItem('activeUserName', data.nombre);
                    localStorage.setItem('activeUserToken', data.token); // IMPORTANTE: El Token JWT
                    localStorage.setItem('activeUserRole', role);
                    
                    // Guardamos el ID del negocio si existe (para gestores)
                    if (data.id_negocio) {
                        localStorage.setItem('activeBusinessId', data.id_negocio);
                    }

                    // 3. Redirección según el rol seleccionado
                    alertModal(`¡Bienvenido ${data.nombre}!`, 'success', () => {
                        if (role === 'gestor') {
                            window.location.href = 'panelNegocio.html';
                        } else {
                            window.location.href = 'citas.html';
                        }
                    });

                } else {
                    // Error devuelto por el backend (ej: "Usuario o contraseña incorrectos")
                    alertModal(data.message || "Error al iniciar sesión", 'error');
                }

            } catch (error) {
                console.error("Error de conexión:", error);
                alertModal("No se pudo conectar con el servidor. Asegúrate de que el backend esté corriendo.", 'error');
            } finally {
                setLoading('login', false);
            }
        });
    }

    // --- LÓGICA DE REGISTRO (CONECTADA AL BACKEND) ---
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const name = document.getElementById('reg-name').value.trim();
            const email = document.getElementById('reg-email').value.trim();
            const password = document.getElementById('reg-password').value;
            const confirmPassword = document.getElementById('reg-confirm-password').value;

            if (password !== confirmPassword) {
                alertModal("Las contraseñas no coinciden.", 'error');
                return;
            }

            setLoading('register', true);

            try {
                // 1. Petición de Registro al Backend
                const response = await fetch('http://localhost:5000/api/usuarios', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        nombre: name,
                        correo: email,
                        contraseña: password,
                        // Por defecto, al registrarse desde aquí, id_negocio es null (Cliente)
                        
                        id_negocio: null 
                    })
                });

                const data = await response.json();

                if (response.ok || response.status === 201) {
                    alertModal("¡Registro Exitoso! Ahora inicia sesión.", 'success', () => {
                        switchView('login-view');
                    });
                } else {
                    alertModal(data.error || "Error al registrarse", 'error');
                }

            } catch (error) {
                console.error("Error de registro:", error);
                alertModal("Error de conexión al intentar registrarse.", 'error');
            } finally {
                setLoading('register', false);
            }
        });
    }
});

// --- FUNCIONES AUXILIARES (Se mantienen igual que antes, pero asegúrate de tenerlas) ---
