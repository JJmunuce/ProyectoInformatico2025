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