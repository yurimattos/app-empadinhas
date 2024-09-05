$(document).ready(function() {
    $( ".linha-mae" ).click(function() {
        var id = $(this).attr('id');
        var id = id.split('_')[1];
        var id2 = '#detalhes_';
        var id2 = id2.concat(id);
        var linhaFilha = $(id2);

        if (linhaFilha.is(':visible')) {
            linhaFilha.hide();
        } else {
            linhaFilha.show();
        }
        
    })

    $( ".linha-mae2" ).click(function() {
        var id = $(this).attr('id');
        var id = id.split('_')[1];
        var id2 = '#detalhes2_';
        var id2 = id2.concat(id);
        var linhaFilha = $(id2);

        if (linhaFilha.is(':visible')) {
            linhaFilha.hide();
        } else {
            linhaFilha.show();
        }
        
    })

    
})