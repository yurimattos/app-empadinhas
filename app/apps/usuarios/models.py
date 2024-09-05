from django.db import models
from django.shortcuts import redirect
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import default_token_generator
import datetime
from apps.lojas.models import Lojas, Deposito


tipos_usuario = {1:'Master', 2:'Franqueado', 3:'PDV', 4:'Vendedor', 5:'Fábrica'}

# Create your models here.
class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class UserTypes(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    nome = models.CharField(max_length=150)
    flag_ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class User(AbstractUser):
    USER_TYPE_CHOICES = (
      ('', 'Selecione o tipo de acesso'),
      (1, 'Master'),
      (2, 'Franqueado'),
      (3, 'PDV'),
      (4, 'Vendedor'),
      (5, 'Fábrica'),
  )
    email = models.EmailField(null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)
    phone = models.BigIntegerField()
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    #user_type = models.ForeignKey(UserTypes, on_delete=models.SET_NULL)
    lojas = models.ManyToManyField(Lojas, null=True, blank=True, related_name='users')
    depositos = models.ManyToManyField(Deposito, null=True, blank=True, related_name='users')
    config_caixa_selecao = models.BooleanField(default=False)
    objects = CustomUserManager()

    def create_activation_message(self, request):
        """
        Cria token para validação de e-mail e insere no e-mail
        """
        current_site = get_current_site(request)
        self.subject = 'Ative sua conta'
        self.message = render_to_string('account_activation_email.html', {
                'user': self,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(self.pk)),
                'token': default_token_generator.make_token(self),
            })
        return self

    def create_activation_message_2(self, request):
        """
        Cria token para validação de e-mail e insere no e-mail
        """
        current_site = get_current_site(request)
        self.subject = 'Ative sua conta'
        self.message = render_to_string('account_activation_email_2.html', {
                'user': self,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(self.pk)),
                'token': default_token_generator.make_token(self),
            })
        return self

    @classmethod
    def activate_user(cls, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = cls.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, cls.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.email_confirmed = True
            user.is_active = True
            user.save()
            return user
        else:
            return None

    def lojas_vinculadas(self):
        lojas = self.lojas.all().filter(flag_ativo=True).order_by('nome_da_loja')
        return lojas

    def check_acesso_loja(self, loja):
        lojas_permitidas=self.lojas_vinculadas()
        return loja in lojas_permitidas

    def depositos_vinculados(self):
        depositos = self.depositos.all().filter(flag_ativo=True)
        return depositos

    def check_acesso_deposito(self, deposito):
        if self.user_type == 1:
            depositos_permitidos=Deposito.objects.all()
        else:
            depositos_permitidos=self.depositos_vinculados()
        return deposito in depositos_permitidos

    def check_buyer_or_worker(self):
        return self.user_type in [1, 2, 3]