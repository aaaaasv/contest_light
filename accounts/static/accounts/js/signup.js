$(window).on('load', function () {


    $('.btn-email').on('click', function () {
        if (!$('.form-one input').val()) {
            alert('Будь ласка, заповніть усі поля');
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