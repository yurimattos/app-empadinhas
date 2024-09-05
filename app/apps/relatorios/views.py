from django.shortcuts import redirect, render
from datetime import datetime, timedelta
from .relatorios import relatorio_perdas, relatorio_pedidos, gerar_extracao, relatorio_pedido_detalhes, relatorio_contagens
from django.contrib.auth.decorators import login_required
from apps.usuarios.decorators import master_user_required
from django.contrib import messages

# Create your views here.
@login_required
@master_user_required
def exportar_relatorio(request):
    if request.method == 'GET':
        dados={}
        return render(request, 'exportar_relatorio.html', dados)

    if request.method == 'POST':
        f=request.POST['fim']
        i=request.POST['inicio']
        id_relatorio=request.POST['relatorio']

        fim=datetime.strptime(f, '%Y-%m-%d')
        inicio=datetime.strptime(i, '%Y-%m-%d')
        intervalo=fim-inicio

        if intervalo.days>31:
            messages.info(request, 'O período selecionado não pode ser maior que 31 dias!', extra_tags='alert alert-danger alert-dismissible fade show text-xs')
            return redirect('exportar_relatorio')

        if id_relatorio == '1':
            relatorio=relatorio_pedidos(inicio, fim)
        if id_relatorio == '2':
            relatorio=relatorio_pedido_detalhes(inicio, fim)
        if id_relatorio == '3':
            relatorio=relatorio_perdas(inicio, fim)
        if id_relatorio == '4':
            relatorio=relatorio_contagens(inicio, fim)

        response=gerar_extracao(file_name=relatorio['name'], columns=relatorio['columns'], data=relatorio['data'])
        return response
