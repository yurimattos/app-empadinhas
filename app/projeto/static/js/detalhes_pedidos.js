// função assincrona pra obter detalhes do pedido
// incluir na página:
// <script>const UrlFetch= "{% url 'detalhes_pedido' %}"</script>
// <script src="{% static 'js/detalhes_pedidos.js' %}"></script>

// Na view:
// @login_required
// @buyer_user_required
// def detalhes_pedido(request):
//     pedido_id = json.loads(request.body.decode('utf-8'))
//     itens_do_pedido = get_list_or_404(ItensPedido, pedido=pedido_id)

//     data = serializers.serialize("json", itens_do_pedido, fields=('produto', 'preco', 'quantidade'))

// 	return JsonResponse(data, safe=False)
	

$(document).ready(function() {


	$( ".detalhes-pedido" ).click(function() {
		var idPedido = $(this).val();
		fetch(UrlFetch, {
			method: 'post',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken'),
			  },
			credentials: 'same-origin',
			body: JSON.stringify(idPedido),
		}).then(function(response) {
			return response.json();
		  }).then(function(result) {
			console.log('retorno:');
			console.log(result);
			// console.log(result.valor_entrega);
			// console.log(result['valor_entrega']);
		  })
	  });

	
	  function getCookie(name) {
		let cookieValue = null;
		if (document.cookie && document.cookie !== '') {
			const cookies = document.cookie.split(';');
			for (let i = 0; i < cookies.length; i++) {
				const cookie = cookies[i].trim();
				// Does this cookie string begin with the name we want?
				if (cookie.substring(0, name.length + 1) === (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	  }
	  const csrftoken = getCookie('csrftoken');
	  

});