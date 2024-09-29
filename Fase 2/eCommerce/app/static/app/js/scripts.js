$("#mensajeError").hide();
$("#mensajeErrorPass").hide();

//validador de creacion de usuarios
$("#crearUsr").click(function() {
    var correo = $("#newcorreo").val();

    if (IsEmail(correo) && correo != "") {
        $("mensajeError1").hide();
        if (($("#clave1").val() != "")) {
            if (($("#clave2").val()) == ($("#clave1").val())) {
                $("#mensajeError1").hide();
                $("#mensajeErrorPass").hide();
                alert("Nuevo usuario creado");
                $(location).prop('href', 'http://127.0.0.1:8000/Registrar/')
            } else {
                $("#mensajeErrorPass").show();
            }
        }
    } else {
        $("mensajeError1").show();
    }
})




//validacion de correo de recuperacion
$("#mensajeErrorMail").hide()
$("#Recuperar").click(function() {
    if (IsEmail($("#recupEmail").val())) {
        $("#mensajeErrorMail").hide();
    } else {
        $("#mensajeErrorMail").show();
    }
})



//se encarga de validar correo, obtener info de textfield y enviar correo.
formulario.addEventListener('submit', (e) => {
    e.preventDefault();
    var email = document.getElementById("EntradaMail").value;
    var mensaje = document.getElementById("infoBox").value;

    if (IsEmail(email)) {
        console.log("Se aprueba correo")
        if (mensaje != null) {
            console.log("Se aprueba mensaje")
            sendEmail(email, mensaje);
            console.log("Mensaje enviado")
            return true;
        }
    } else {
        alert("Correo Incorrecto")
        return false;
    }
});
$("#loginBTN").click(function() {
    var username = $("#userN").val();
    var password = $("#pswrdN").val();

    if (username && password) {
        $.ajax({
            url: '/api/token/',
            type: 'POST',
            data: { username: username, password: password },
            success: function(response) {
                var access_token = response.access_token;
                // Guarda el token en el almacenamiento local (localStorage) o como prefieras.
                // Redirige a la página de inicio.
                window.location.href = '/home/';
            },
            error: function(xhr, status, error) {
                // Maneja el error de autenticación.
                console.error(error);
                $("#mensajeError").show();
            }
        });
    }
});
