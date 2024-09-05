$(document).ready(function() {
   
    lojas=$('.loja')
    $(lojas).each(
        function() {
            let id = $(this).attr('id');
            let urlContagem='/ultimas_contagens/'+id
            let inventarios_list=[]
            let td_resumo = $(`#td_resumo${id}`)

            $.get(urlContagem, function(data) {
                //console.log(data)
                $(data).each(
                    function(key, value) {
                        inventarios_list.push(value.inventario_id)
                        let td = $(`#td${value.loja_id}${value.tipo_id}`)

                        td.append(`
                            <div class="spinner" role="status">
                                <span class="sr-only">Loading...</span>
                            </div>
                        `)
                        
                        td.append(`
                        <li class="li">Data: ${value.atualizacao_dia} - ${value.atualizacao_hora}</li>
                        <li class="li">Status: ${value.status}</li>
                        `)
                        $(`#td${value.loja_id}${value.tipo_id} div`).remove()

                        var date1 = new Date(value.ultima_atualizacao);
                        var timeStamp = Math.round(new Date().getTime() / 1000);
                        var timeStampYesterday = timeStamp - (24 * 3600);
                        var is24 = date1 >= new Date(timeStampYesterday*1000).getTime();

                        if (is24 && value.status == 'Concluído') {
                            td.css("color", "black")
                            td.addClass('bg-success')
                          } else if (is24 && value.status != 'Concluído') {
                            td.css("color", "black")
                            td.addClass('bg-warning')
                          } else {
                            td.css("color", "black")
                            td.addClass('bg-danger')
                          }
                        
                    }
                )

                if (inventarios_list.length > 0) {
                    soma(inventarios_list, td_resumo)
                } 

            })
        }
    )

    function soma(inventarios, td_resumo) {
        let urlSoma='/soma_inventarios'
        $.get(urlSoma, {'inventarios':inventarios}, function(data) {
            Object.entries(data).forEach((entry) => {
                const [key, value] = entry;
                td_resumo.append(`<li>${key}: ${value}</li>`)
              });
        })
    }
    

})

