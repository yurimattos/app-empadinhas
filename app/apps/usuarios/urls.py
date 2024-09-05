from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import LoginForm


urlpatterns = [
    path('', views.index, name='index'),
    #path('signup', views.signup, name='signup'),
    path('criar_usuario', views.criar_usuario, name='criar_usuario'),
    path('editar_usuario/<int:usuario>/', views.editar_usuario, name='editar_usuario'),
    path('desativar_usuario/<int:usuario>/', views.desativar_usuario, name='desativar_usuario'),
    #path('login', auth_views.LoginView.as_view(redirect_authenticated_user=True, authentication_form=LoginForm, extra_context={'card_header':'Login', 'card_footer':'Não possui uma conta ainda? Registre-se', 'card_footer_link':'/signup'}), name='login'),
    path('login', auth_views.LoginView.as_view(redirect_authenticated_user=True, authentication_form=LoginForm), name='login'),
    path('password_reset/', auth_views.PasswordResetView.as_view(title='titulo'), name='password_reset'),
    path('account_activation_sent', views.account_activation_sent, name='account_activation_sent'),
    path('account_activation_invalid', views.account_activation_invalid, name='account_activation_invalid'),
    path('activate_user/<str:uidb64>/<str:token>', views.activate_user, name='activate_user'),
    path('error_403', views.error_403, name='error_403'),
    path('change_password', views.change_password, name='change_password'),
]