$(document).ready(function() {

	//Filtrar por categoria:
	$(".enfatizar").click(function () {
		$('.enfatizar').removeClass('active');
        $(this).addClass('active');

		let categoriaEscolhida = $(this).attr('id')
		let inputs = $('.filtrar')
		if (categoriaEscolhida == '_all') {
			inputs.show()
		} else {
			inputs.each( function() {
				let input = $(this)
				if ( input.hasClass(categoriaEscolhida) ) {
					input.show()
				} else {
					input.hide()
				}
			})
		}
    });

	//Multiplica quantidade por preço e calcula o frete:
	$('.input-quantidade').change( function(event, change_param) {
		let id_do_input = $(this).attr('id')
		var quantidade = $(this).val()

		//Tratamento para inserir zero caso o valor informado seja negativo:
		if (quantidade < 1) {
			$(this).val('')
			var quantidade = 0
		}

		let id_do_input_preco = '#' + id_do_input + '.input-preco'
		let preco = $(id_do_input_preco).val()
		let preco_tratado = parseFloat(preco.replace(",", "."));
		let subTotal = quantidade * preco_tratado
		let id_do_input_subtotal = '#' + id_do_input + '.input-subtotal'
		$(id_do_input_subtotal).val('R$ ' + subTotal.toFixed(2));

		total();
		total_por_categoria();

		if (change_param == 'radio') {
			//Se o evento veio do radio, não limpa o radio		
		} else {
			id_do_input = $(this).attr('id')
			limparRadio(id_do_input)
		}

	})

	//Recalcula valor do total e frete ao mudar o dia da entrega:
	$("#input-entrega").change(function() {
		total();
	});


	//Multipla escolha:
	$('input[type=radio]').change(function() {
		let radio = $(this);

		let valor_radio = radio.val();

		let radio_id = radio.attr('id')
		let radio_numero_id = radio_id.split("_")[1]

		id_input = '#' + radio_numero_id + '.input-quantidade'

		$(id_input).val(valor_radio)
		$(id_input).trigger("change", 'radio');

	});

	function limparRadio(id) {
		id_do_radio = '[id=inlineRadio_' + id +']'
		$(id_do_radio).prop('checked', false);
		
	};



	function frete(valorPedido) {
		let valorFrete = $('#custo-entrega').val()
		let pedidoMinimo = $('#pedido-minimo').val()
		var pedidoMinimoTratado = parseFloat(pedidoMinimo.replace(",", "."));
		var diaEntrega = $( "#input-entrega option:selected" ).text();
		var diaEntrega = diaEntrega.toLowerCase();
		var entregaGratis = diaEntrega.includes('grat');
		if (valorPedido >= pedidoMinimoTratado && entregaGratis == true ) {
			$('#id_frete').val('R$ - ');
		} else {
			$('#id_frete').val('R$ ' + valorFrete);
		}
	}

	function total() {
		var sum = 0;
		$('.input-subtotal').each(function() {
			s = $(this).val()
			sum += Number(s.replace('R$ ', ''));
		});
		$('#input-total').val('R$ ' + sum.toFixed(2));
		frete(sum);
	}

	function total_por_categoria() {
		var t = []
		$('.input-quantidade').each(function() {
			id_do_input = $(this).attr('id')
			//input quantidade:
			quantidade = $(this).val()

			//tratamento caso esteja vazio (evitar NaN):
			if ( quantidade != '') {
				quantidade = parseInt(quantidade)
			} else {
				quantidade = 0
			}
			
			//input categoria escondido
			id_da_categoria = '#' + id_do_input + '.input-categoria'
			categoria=$(id_da_categoria).val()

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

	//Clica na categoria Empadas ao abrir a tela:
	$("#Empadas").trigger("click");

	//Desencadeia calculos de subtotal, total, etc:
	$('.input-quantidade').trigger("change");

	//Habilita Radio:
	$('input[type=radio]').prop('disabled', false);
});