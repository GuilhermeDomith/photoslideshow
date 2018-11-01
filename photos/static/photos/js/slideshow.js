setTimeout(check_progress, 100);

function check_progress() {
    $.ajax({
        method: "GET",
        url: location.href+"check_progress",
        success: function (data) {
            let progresso = 0;
            path_video = '';

            if(typeof(data) == 'number')
                progresso = data;
            else{
                data = JSON.parse(data);
                progresso = data['status'];
                path_video = data['path'];
            }


            barra_prog = $('#progress_video');
            barra_prog.attr('aria-valuenow', progresso);
            barra_prog.css('width', progresso + '%');

            if (progresso === true) 
                setTimeout(inserir_video, 2000);
            else
                check_progress();
        }
    });
}

function inserir_video() {
    $('#painel-progresso').hide();
    $('#painel-video').show();

    $('#msg-status').html('Pronto! Você pode fazer o download do seu slideshow.'+
        ' Se quiser, pode voltar no menu de navegação para alterar configurações e fotos'+
        ' selecionadas.');
    $('#btn-download').attr('href', path_video);
    $('video').html('<source src="'+path_video+'" type="video/mp4">');

}