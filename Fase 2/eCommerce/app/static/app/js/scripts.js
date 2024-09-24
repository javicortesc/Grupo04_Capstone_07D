//validadores de inicio de sesion
$("#mensajeError").hide();
$("#mensajeErrorPass").hide();
$("#loginBTN").click(function() {
    var correo = $("#userN").val();
    if (correo != "") {
        if ($("#pswrdN").val() != "") {
            $("#mensajeError").hide();
            $(location).prop('href', 'http://127.0.0.1:8000/Platos/')
        } else {
            $("#mensajeError").show();
        }
    } else {
        $("#mensajeError").show();
    }
});

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
