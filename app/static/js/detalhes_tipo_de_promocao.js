$( "select" )
.change(function () {
    $( "select option:selected" ).each(function() {

        var condicoes = '<br>É possível configurar condições para a campanha: unidades participantes, dias, horários, etc.'

    $("#infos").show();
    if ( $( this ).val() == 'voucher' ) {
        $("#infos-text").html('Escolha essa opção para criar uma promoção de voucher de consumação.<br>Ex: voucher custa R$ 50,00 e dá direito à R$ 80,00 de consumação.' + condicoes);
    }

    if ( $( this ).val() == 'item' ) {
        $("#infos-text").html('Escolha essa opção para criar uma promoção para um item específico do seu cardápio.' + condicoes);
    }

    if ( $( this ).val() == '' ) {
        $("#infos").hide();
    }

    });
})
.change();


$(window).on("load", function(){
    $("#infos").hide();
});