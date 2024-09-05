from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.usuarios.decorators import master_user_required
from .forms import DiaDeEntregaBloqueadoForm, BloquearDataForm
from .models import DiaDeEntregaBloqueado, DiaDeEntrega


@login_required
@master_user_required
def entregas(request):
    if request.method == 'POST':
        form = BloquearDataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('entregas')

    else:
        form = BloquearDataForm()
        dias_bloqueados = DiaDeEntregaBloqueado.objects.all()

    dados = {
        'titulo': 'Configurações de Entrega',
        'dias_bloqueados': dias_bloqueados,
        'form': form,
    }
    return render(request, 'entregas.html', dados)

@login_required
@master_user_required
def desbloquear_dia(request, dia):
    dia = get_object_or_404(DiaDeEntregaBloqueado, pk=dia)
    dia.delete()
    return redirect('entregas')