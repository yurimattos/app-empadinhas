//adicionar classes no form (prevent-double-click-form)
//adicionar botao com classe e onclick:
//<button class="btn btn-primary prevent-double-click-button" type="submit" onclick="javascript:nextStep();">Salvar</button>


$(function () {
    $(".next-step-form1").submit(function ( event ) {
        event.preventDefault();

        //Enviar para o form de submit final:
        $('#id_titulo2').val($('#id_titulo').val());
        $('#id_descricao2').val($('#id_descricao').val());

        $('#wizard1').removeClass( "active show" );
        $('#wizard2').addClass( "active show" );
    });
});

$(function () {
    $(".next-step-form2").submit(function ( event ) {
        event.preventDefault();
        $('#wizard2').removeClass( "active show" );
        $('#wizard3').addClass( "active show" );
    });
});