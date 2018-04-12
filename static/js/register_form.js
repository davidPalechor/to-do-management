$(function() {
    $('form.js-register-form').validate({
        submitHandler: function(form) {
            var data = {
                'username': $('#id_username').val(),
                'password': $('#id_password').val()
            }
            $.ajax({
                type: 'POST',
                url: '/register',
                data: JSON.stringify(data),
                contentType: 'application/json;charset=UTF-8',
                success: function(response) {
                    if (response.ok) {
                        window.location.replace('/')
                    } else {
                        $(".form-error").text(response.error)
                    }
                }
            })
        }
    })
});