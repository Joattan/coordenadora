from django.urls import path
from . import views

app_name = 'coordenadoras'

urlpatterns = [
    # Public
    path('cadastro/', views.CadastroCandidataView.as_view(), name='cadastro'),
    path('cadastro/sucesso/', views.cadastro_sucesso, name='sucesso'),
    
    # APIs for form
    path('api/cep/', views.api_cep_lookup, name='api_cep'),
    path('api/cpf/', views.api_cpf_lookup, name='api_cpf'),
    
    # Admin
    path('admin/listagem/', views.CandidataListView.as_view(), name='admin_list'),
    path('admin/detalhe/<int:pk>/', views.CandidataDetailView.as_view(), name='admin_detail'),
    path('admin/editar/<int:pk>/', views.CandidataUpdateView.as_view(), name='admin_edit'),
    path('admin/excluir/<int:pk>/', views.admin_excluir_candidata, name='admin_delete'),
    path('admin/atualizar-status/<int:pk>/', views.admin_atualizar_status, name='admin_status'),
]
