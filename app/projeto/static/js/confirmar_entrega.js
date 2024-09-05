$(document).ready(function() {

    var inputs = $( ".input-quantidade" )

    $( "#id_flag_entrega_ok" ).change(function() {
        if ( $( "#id_flag_entrega_ok" ).val() == 'False' ) {   
            inputs.removeAttr('readonly');
        } else {
            inputs.attr('readonly', true);
        }
	  });
    
})