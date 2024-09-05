$(document).ready(function() {
	var wrapper = $(".input_fields_wrap"); //Fields wrapper
	var add_button = $("#add_field_button"); //Add button ID
	var options = $('select')[0];
	
	var x = 1; //initlal text box count
	$(add_button).click(function(e){ //on add input button click
		e.preventDefault();

		$(wrapper).append('<div> <hr style="border-top: dotted 1px;"/> <div class="form-row"> <hr style="border-top: dotted 1px;"/> <div class="form-group col-md-5"> <label for="id_item_pedido">Item pedido</label>' + options.outerHTML + '</div><div class="form-group col-md-2"> <label for="id_quantidade">Quantidade</label> <input type="number" name="quantidade" min="1" class="form-control input-quantidade" required="" id="id_quantidade"> </div><div class="form-group col-md-2"> <label for="preco">Preço</label> <input type="number" name="preco" min="1" class="form-control input-preco" id="id_preco" readonly=""> </div><div class="form-group col-md-2"> <label for="subtotal">Subtotal</label> <input type="number" name="total" min="1" class="form-control input-subtotal" id="id_subtotal" readonly=""> </div><div class="form-group col-md-1"> <label for="remover">Excluir</label> <div class="text-center mt-2"> <a href="#" class="remove_field" id="remover"><i class="fa fa-trash fa-lg" aria-hidden="true"></i></a> </div></div></div></div>'); //add input box
	});
	
	$(wrapper).on("click",".remove_field", function(e){ //user click on remove text
		e.preventDefault();
		$(this).parent('div').parent('div').parent('div').parent('div').remove();
		x--;
		subTotal();
	})




	$('form').on("change","#id_item_pedido", function(e){ //user click on remove text
		e.preventDefault();
		var i = $( this ).val();  //id do item
		var preco = precos[i];	//preco correspondente ao cód do item
		var q = $(this).parent('div').next().children().next().val()
		var input_subtotal = $(this).parent('div').next().next().next().children()

		$(this).parent('div').next().next().children().val(preco);	//insere preço
		input_subtotal.val(preco * q)
		//x--;
		subTotal();
	})


	$('form').on("change","#id_quantidade", function(e){
		e.preventDefault();
		var q = $( this ).val();
		var p = $(this).parent('div').next().children().val()
		var input_subtotal = $(this).parent('div').next().next().children()
		var subtotal = p * q;
		input_subtotal.val(subtotal);

		subTotal();
		
	})

	function subTotal() {
		var sum = 0;
		$('.input-subtotal').each(function( ) {
			sum += Number($(this).val());
		});
		$('#id_total').val(sum);
	}


});