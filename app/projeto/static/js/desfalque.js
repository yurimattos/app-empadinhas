$(document).ready(function() {
    $( ".checkbox-desfalque" ).click(function() {
        var id = $(this).attr('id');
        var id = id.split('_')[1];
        var idInput = '#q_desfalque_';
        var idInput = idInput.concat(id);
        var inputDesfalque = $(idInput);

        if ($(this).is(":checked")) {
        inputDesfalque.removeAttr('readonly');
        inputDesfalque.removeAttr('disabled');
        } else {
            inputDesfalque.val('');
            inputDesfalque.attr('readonly', true);
            inputDesfalque.attr('disabled', true);
            
        };
    })

    
})