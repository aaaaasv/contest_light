$(window).on('load', function () {

    function validateEmail(email) {
        const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }


    $('.btn-email').on('click', function () {
        let isEmail = validateEmail($('.email-input').val())
        if (!$('.form-one input').val() || !isEmail || $('.password-input-one').val() !== $('.password-input-two').val()) {
            alert('Будь ласка, заповніть усі поля коректно');
        } else {
            $('.form-one').hide();
            $('.form-two').css('display', 'flex');
            sendActivationCode($('.form-one .email-input').val())

        }
    })
    $('.btn-activation').on('click', function () {
            if ($(this).text() === 'Далі') {
                $('.form-two').hide();
                $('.form-three').show();
                $('.card-form').css('min-height', '100%');
            }
            if (!$('.form-two input').val()) {
                alert('Будь ласка, спочатку введіть код');
            } else {
                let userCode = ''
                for (let i = 0; i <= 3; i++) {
                    let code_number = $('.form-two input').eq(i).val();
                    userCode += code_number
                }
                checkActivationCode(userCode)
            }
        }
    )
})