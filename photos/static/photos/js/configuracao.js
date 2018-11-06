$('#segundos_foto').on('input', (e) => {
    $('#seg_span').text($('#segundos_foto').val());
});

$('#btn-salvar').on('click', (e)=>{
    setTimeout(()=>{
        $('#btn-salvar').hide();
        $('#loader-imagens').show();
    }, 2000);
});