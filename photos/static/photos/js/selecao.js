$(document).ready(function () {

    let maximo_check = parseInt($('#maximo_fotos').html());

    $('#btn-marcar').on('click', function (e) {
        $('input[type="checkbox"]').slice(0, maximo_check).each(function (i, elem) {
            elem.checked = true;
        });
    })

    $('#btn-desmarcar').on('click', function (e) {
        $("input:checked").each(function (i, elem) {
            elem.checked = false;
        });
    })

    $('input[type="checkbox"]').change(function (e) {
        if(this.checked == true)
            if($("input:checked").length == maximo_check + 1)
                this.checked = false;
    });

    // Converte a data de criação das fotos.
    for (let i = 1; true; i++) {
        p = $('#data_criacao_' + i);

        d = new Date(p.html());
        p.html(d.getDate()+'/'+d.getMonth()+'/'+d.getFullYear()+' - '+d.getHours()+':'+d.getMinutes());

        if (p.length == 0)
            break;
    }

    $('#salvar').click((e) => {
        if($("input:checked").length == 0)
            e.preventDefault();
    })
})