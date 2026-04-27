from django.contrib import admin
from .models import CandidataCoordenadora

@admin.register(CandidataCoordenadora)
class CandidataCoordenadoraAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'cidade', 'estado', 'status', 'data_criacao')
    list_filter = ('status', 'estado', 'empresa_anterior')
    search_fields = ('nome_completo', 'cpf', 'cidade')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('cpf', 'nome_completo')
        }),
        ('Endereço', {
            'fields': ('cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Dados Profissionais', {
            'fields': ('empresa_anterior', 'empresa_outra', 'media_ganhos', 'quantidade_consultoras')
        }),
        ('Documentos', {
            'fields': ('documento_rg_cnh', 'documento_cpf', 'comprovante_endereco', 'comprovante_ganhos')
        }),
        ('Status e Avaliação', {
            'fields': ('status', 'observacao_aprovacao', 'data_criacao', 'data_atualizacao')
        }),
    )
