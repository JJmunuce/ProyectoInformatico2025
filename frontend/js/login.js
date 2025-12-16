// frontend/js/login.js
// Lógica reducida: login y toggle de contraseña

(function () {
    const API_BASE = "http://127.0.0.1:5000";

    const EYE_OPEN_SVG = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
</svg>`;

    const EYE_CLOSED_SVG = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
  <path stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18"/>
  <path stroke-linecap="round" stroke-linejoin="round" d="M9.88 9.88A3 3 0 0114.12 14.12"/>
  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c1.3 0 2.544.27 3.667.75"/>
</svg>`;

    function alertModal(message, type = 'info', callback = null) {
        const container = document.getElementById('alert-modal-container');
        container.innerHTML = '';
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-gray-900 bg-opacity-80 flex items-center justify-center z-50';
        let color = type === 'error' ? 'text-red-500' : type === 'success' ? 'text-blue-600' : 'text-orange-500';
        let btnColor = type === 'error' ? 'bg-red-500 hover:bg-red-600' : type === 'success' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-orange-500 hover:bg-orange-600';

        modal.innerHTML = `
            <div class="bg-white p-6 sm:p-8 rounded-2xl shadow-2xl max-w-sm mx-4 border border-gray-100">
                <h5 class="text-2xl font-bold mb-4 ${color}">${type === 'error' ? 'Error' : '¡Éxito!'}</h5>
                <p class="text-gray-600 mb-6">${message}</p>
                <button id="close-modal" class="w-full px-4 py-3 ${btnColor} text-white rounded-xl font-bold transition">Aceptar</button>
            </div>
        `;
        container.appendChild(modal);
        document.getElementById('close-modal').onclick = () => {
            container.innerHTML = '';
            if (callback) callback();
        };
    }

    function setLoading(formId, isLoading) {
        const btn = document.querySelector(`#${formId}-form button`);
        if (!btn) return;
        if (isLoading) {
            btn.disabled = true;
            btn.textContent = 'Cargando...';
            btn.classList.add('opacity-70', 'cursor-not-allowed');
        } else {
            btn.disabled = false;
            btn.textContent = 'Iniciar Sesión';
            btn.classList.remove('opacity-70', 'cursor-not-allowed');
        }
    }

    function setupPasswordToggle(inputId, btnId, iconId) {
        const input = document.getElementById(inputId);
        const btn = document.getElementById(btnId);
        const icon = document.getElementById(iconId);
        if (!input || !btn || !icon) return;

        btn.addEventListener('click', (e) => {
            e.preventDefault();
            if (input.type === 'password') {
                input.type = 'text';
                btn.setAttribute('aria-pressed', 'true');
                btn.innerHTML = EYE_OPEN_SVG;
            } else {
                input.type = 'password';
                btn.setAttribute('aria-pressed', 'false');
                btn.innerHTML = EYE_CLOSED_SVG;
            }
        });
    }

    async function safeJson(resp) {
        try {
            return await resp.json();
        } catch (_) {
            return null;
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        // Setup password toggle for login only
        setupPasswordToggle('password', 'toggle-password', 'icon-password');

        // Login handler
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('email').value.trim();
                const password = document.getElementById('password').value;
                if (!email || !password) {
                    alertModal("Completa usuario y contraseña.", 'error');
                    return;
                }

                setLoading('login', true);
                try {
                    const resp = await fetch(`${API_BASE}/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username: email, password: password })
                    });

                    const data = await safeJson(resp);

                    if (resp.ok) {
                        if (data.id_usuario) localStorage.setItem('activeUserId', data.id_usuario);
                        if (data.nombre) localStorage.setItem('activeUserName', data.nombre);
                        if (data.token) localStorage.setItem('activeUserToken', data.token);

                        if (data.id_negocio) {
                            localStorage.setItem('activeUserRole', 'gestor');
                            if (data.id_negocio) localStorage.setItem('activeBusinessId', data.id_negocio);
                            alertModal(`¡Bienvenido ${data.nombre || ''}!`, 'success', () => {
                                window.location.href = 'panelNegocio.html';
                            });
                        } else {
                            localStorage.setItem('activeUserRole', 'cliente');
                            alertModal(`¡Bienvenido ${data.nombre || ''}!`, 'success', () => {
                                window.location.href = 'citas.html';
                            });
                        }
                    } else {
                        const message = (data && (data.message || data.error)) || `Error: ${resp.status}`;
                        alertModal(message, 'error');
                    }
                } catch (err) {
                    console.error("Error de conexión:", err);
                    alertModal("No se pudo conectar con el servidor. Asegúrate de que el backend esté corriendo.", 'error');
                } finally {
                    setLoading('login', false);
                }
            });
        }
    });
})();