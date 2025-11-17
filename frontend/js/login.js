// Este evento se asegura de que el script se ejecute
// solo después de que todo el HTML se haya cargado.
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Leemos los parámetros de la URL (ej. ?rol=paciente)
    const params = new URLSearchParams(window.location.search);
    const rol = params.get('rol'); // 'paciente' o 'medico'

    // 2. Referencias a los elementos que queremos cambiar
    const title = document.getElementById('login-title');
    const rolInput = document.getElementById('rol-input');

    // 3. Actualizamos la página dinámicamente
    //    Usamos "else if" para ser más robustos.
    if (rol === 'paciente') {
        title.textContent = 'Login de Paciente';
        rolInput.value = 'paciente';
    } else if (rol === 'medico') {
        title.textContent = 'Login de Profesional';
        rolInput.value = 'medico';
    } else {
        // Un valor por defecto si alguien entra a login.html sin parámetro
        title.textContent = 'Iniciar Sesión'; 
    }
});

function login(event) {
    
    //Evito que se recargue la página
    event.preventDefault();

    // Obtener valores de usuario y contraseña
    var username = document.getElementById('email').value;
    var password = document.getElementById('password').value;

    // URL de la API para iniciar sesión
    var apiUrl = 'http://127.0.0.1:5000/login';

    // Datos de la solicitud
    var data = {
        username: email,
        password: password
    };

    // Configuración de la solicitud
    var requestOptions = {
        method: 'POST',
        headers: {
            // Aquí se agrega otro contenido de acuerdo a la necesidad de la API
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' +  btoa(username + ':' + password)
        },
        body: JSON.stringify(data)
    };

    function handleResponse(response)  {
        if (!response.ok){
            return Promise.reject(response);
        }
        else{
            return response.json();
        }
    }

    // Hacer la solicitud fetch y guardo en el sessionStorage
    fetch(apiUrl, requestOptions)
        .then(response => handleResponse(response))
        .then(userData => {
            sessionStorage.setItem("id_usuario", userData.id_usuario);
            sessionStorage.setItem("nombre", userData.nombre);
            sessionStorage.setItem("apellido", userData.apellido);
            sessionStorage.setItem("token", userData.token);

            window.location.href = "dashboard.html";

        })
        .catch(error => {
            error.json().then(data => 
                Swal.fire({
                    icon: "error",
                    text: data.message
                  })
            );
        })
        .finally( () => { 
            console.log("Promesa finalizada (resuelta o rechazada)");
        })
};