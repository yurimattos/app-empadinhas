from django import forms
from .models import DiaDeEntregaBloqueado


class DiaDeEntregaBloqueadoForm(forms.ModelForm):
    dia = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder':"Selecione um dia",
                'min':1,
                'max':31
                })
    )
    class Meta:
        model = DiaDeEntregaBloqueado
        fields = ['dia', 'mes']

class BloquearDataForm(forms.ModelForm):
    data_bloqueio = forms.DateField(
        label='Data',
        widget=forms.TextInput(
            attrs={'type':'date'}
        )
    )
    class Meta:
        model = DiaDeEntregaBloqueado
        fields = ['data_bloqueio']