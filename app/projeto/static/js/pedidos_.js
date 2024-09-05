$(document).ready(function() {

	$('input[type=radio]').change(function() {
		let radio = $(this);

		let valor_radio = radio.val();

		let radio_id = radio.attr('id')
		let radio_numero_id = radio_id.split("_")[1]

		id_input = '#id_quantidade_' + radio_numero_id

		$(id_input).val(valor_radio)
		$(id_input).trigger("change", 'radio');

	});

	function limparRadio(id) {
		id_do_radio = '[id=inlineRadio_' + id +']'
		$(id_do_radio).prop('checked', false);
		
	};

	$('form').on("change",".input-quantidade", function(e, change_param){
		e.preventDefault();
		var q = $( this ).val();
		var p = $(this).next().val()//.next().children().val()
		var p = parseFloat(p.replace(",", "."));
		var input_subtotal = $(this).next().next()
		var subtotal = p * q;
		input_subtotal.val('R$ ' + subtotal.toFixed(2));

		subTotal();
		totalPorCategoria();

		if (change_param == 'radio') {
			
		} else {
			id_do_input = $(this).attr('id').split("_")[2]
			limparRadio(id_do_input)
		}
		
	})

	function subTotal() {
		var sum = 0;
		$('.input-subtotal').each(function( ) {
			s = $(this).val()
			sum += Number(s.replace('R$ ', ''));
		});
		$('#id_total').val('R$ ' + sum.toFixed(2));

		frete(sum);
	}

	function totalPorCategoria() {
		var t = []
		$('.input-quantidade').each(function( ) {
			//input quantidade:
			quantidade = $(this).val()

			//tratamento caso esteja vazio (evitar NaN):
			if ( quantidade != '') {
				quantidade = parseInt(quantidade)
			} else {
				quantidade = 0
			}
			
			//input categoria escondido
			categoria = $(this).next().next().next().next().val()

			//verifica se no array ja tem a categoria, e decide se soma ou adiciona:
			categoria_ja_add = t.find(x => x.categoria === categoria)
			if (typeof categoria_ja_add == 'undefined') {
				t.push({categoria:categoria, quantidade:quantidade})
			} else {
				categoria_ja_add.quantidade += quantidade
			}

			
		})

		//Caso a categoria tenha alguma quantidade, mostra no resumo:
		function addToLi(el) {
			if (el.quantidade != 0) {
				li = '<li class="item_resumo">' + el.categoria + ': ' + el.quantidade + ' volume(s)</li>'			
				$("#resumo_volumes").append(li)
			}		
		}
		$('.item_resumo').remove(); //limpa os <li> anteriores
		t.forEach(addToLi)
	}

	function frete(valorPedido) {
		var pedidoMinimoTratado = parseFloat(pedidoMinimo.replace(",", "."));
		var diaEntrega = $( "#id_dia_da_entrega option:selected" ).text();
		var diaEntrega = diaEntrega.toLowerCase();
		var entregaGratis = diaEntrega.includes('grat');
		if (valorPedido >= pedidoMinimoTratado && entregaGratis == true ) {
			$('#id_frete').val('R$ - ');
		} else {
			$('#id_frete').val('R$ ' + valorFrete);
		}
	}


	$( "#id_dia_da_entrega" ).change(function() {
		subTotal();
	  });


	function init() {
	$('.input-quantidade').each(function( ) {
		console.log('calculando valor inicial...')
		var q = $( this ).val();
		var p = $(this).next().val();
		var p = parseFloat(p.replace(",", "."));
		var input_subtotal = $(this).next().next()
		var subtotal = p * q;
		input_subtotal.val('R$ ' + subtotal.toFixed(2));

		subTotal();
		totalPorCategoria();

	});
}

	init();

	console.log('carregamento finalizado!')
	$('input[type=radio]').prop('disabled', false);
	  
});