$(document).ready(function() {
console.log('projeto')
    function convertTZ(date, tzString) {
        return new Date((typeof date === "string" ? new Date(date) : date).toLocaleString("en-US", {timeZone: tzString}));   
    }
    const options = { month: 'short', day: 'numeric' };

    $( "#id_loja_pedido" ).change(function() {
        var loja_selecionada = $(this).val();
        urlContagem='/ultimas_contagens/'+loja_selecionada
        urlSugestoes='sugestoes_por_loja/'+loja_selecionada

        let inventarios_list=[]
        let td_resumo = $(`#soma_categorias`)

        //Mostra ultimas contagens
        $.get(urlContagem, function(data) {

            $('#inventario').show();

            $('.li').remove();
            if (data.length >= 1) {
                $(data).each(
                    function(key, value) {
                        inventarios_list.push(value.inventario_id)
                        let s = `
                        <li class="li">${value.tipo}</li>
                        <ul class="li">
                            <li>Status: ${value.status}</li>
                            <li>Última Atualização: ${value.atualizacao_dia} - ${value.atualizacao_hora}</li>
                        </ul>
                        `
                        $('#contagens').append(s)
                    }
                )

                if (inventarios_list.length > 0) {
                    soma(inventarios_list, td_resumo)
                }

            } else {
                let s = '<li class="li">Nenhuma contagem recente encontrada</li>'
                $('#contagens').append(s)
            }
            

        });

        //Preenche opções de pedido inteligente
        $.get(urlSugestoes, function(data) {
            //Limpa opções antes de inserir as novas
            $("#id_pedido_inteligente").empty();
            $('#id_pedido_inteligente').append('<option disabled selected>Selecione uma Opção</option>');

            $(data).each(
                function(key, value) {
                    $('#id_pedido_inteligente').append($('<option/>', { 
                        value: (value.id),
                        text : (value.nome)
                    }));
                }
            )
        });

    })


    function soma(inventarios, td_resumo) {
        console.log('obtendo soma por categorias...')
        let urlSoma='/soma_inventarios'
        $.get(urlSoma, {'inventarios':inventarios}, function(data) {
            console.log(data)
            Object.entries(data).forEach((entry) => {
                const [key, value] = entry;
                td_resumo.append(`<li class="li">${key}: ${value}</li>`)
              });
        })
    }

})

