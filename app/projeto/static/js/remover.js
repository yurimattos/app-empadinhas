$(document).ready(function() {
	var wrapper = $(".input_fields_wrap"); //Fields wrapper

	
	var x = 1; //initlal text box count

	$(wrapper).on("click",".remove_field", function(e){ //user click on remove text
		e.preventDefault();
		$(this).parent('div').parent('div').parent('div').parent('div').remove();
		x--;
	})

});