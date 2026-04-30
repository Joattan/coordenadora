from django.db import models

class CandidataCoordenadora(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente de Aprovação'),
        ('AJUSTE', 'Aguardando Ajuste'),
        ('APROVADO', 'Aprovado'),
        ('REPROVADO', 'Reprovado'),
    ]

    EMPRESA_CHOICES = [
        ('AVON', 'Avon'),
        ('NATURA', 'Natura'),
        ('BOTICARIO', 'O Boticário'),
        ('JEQUITI', 'Jequiti'),
        ('OUTRAS', 'Outras'),
    ]

    # Dados Pessoais
    cpf = models.CharField('CPF', max_length=14, unique=True)
    cod_protheus = models.CharField('Código Protheus', max_length=50, blank=True, null=True, unique=True)
    nome_completo = models.CharField('Nome Completo', max_length=255)
    email = models.EmailField('E-mail', max_length=255, default="")
    foto = models.ImageField('Foto (Opcional)', upload_to='fotos/candidatas/', blank=True, null=True)
    
    # Endereço
    cep = models.CharField('CEP', max_length=9)
    rua = models.CharField('Rua', max_length=255)
    numero = models.CharField('Número', max_length=20)
    complemento = models.CharField('Complemento', max_length=255, blank=True, null=True)
    bairro = models.CharField('Bairro', max_length=100)
    cidade = models.CharField('Cidade', max_length=100)
    estado = models.CharField('Estado', max_length=2)

    # Dados Profissionais
    empresa_anterior = models.CharField('Empresa Anterior', max_length=50, choices=EMPRESA_CHOICES)
    empresa_outra = models.CharField('Outra Empresa', max_length=100, blank=True, null=True)
    media_ganhos = models.DecimalField('Média de Ganhos', max_digits=10, decimal_places=2)
    quantidade_consultoras = models.PositiveIntegerField('Quantidade de Consultoras')

    # Uploads
    documento_rg_cnh = models.FileField('RG ou CNH', upload_to='documentos/rg_cnh/')
    documento_cpf = models.FileField('CPF', upload_to='documentos/cpf/')
    comprovante_endereco = models.FileField('Comprovante de Endereço', upload_to='documentos/endereco/')
    comprovante_ganhos = models.FileField('Comprovante de Ganhos', upload_to='documentos/ganhos/')

    # Status e Observações
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    observacao_aprovacao = models.TextField('Observação de Aprovação', blank=True, null=True)
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Candidata a Coordenadora'
        verbose_name_plural = 'Candidatas a Coordenadoras'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.nome_completo} ({self.cpf})"

class PedidoProtheus(models.Model):
    campanha = models.CharField('Campanha', max_length=10, db_index=True)
    ano = models.CharField('Ano', max_length=4)
    setor = models.CharField('Setor', max_length=10)
    revendedora = models.CharField('Cód. Revendedora', max_length=50) # CODIGO na API
    emissao = models.CharField('Data Emissão', max_length=10) # Manter como texto para evitar erros de conversão do Protheus
    pedido = models.CharField('Nº Pedido', max_length=50)
    produto = models.CharField('Cód. Produto', max_length=50)
    quantidade = models.FloatField('Quantidade', default=0)
    valor_financeiro = models.DecimalField('Valor Financeiro', max_digits=15, decimal_places=2, default=0)
    coordenadora = models.CharField('Cód. Coordenadora', max_length=50, db_index=True) # CODCOORD
    tipo = models.CharField('Tipo', max_length=50, null=True, blank=True)
    tes = models.CharField('TES', max_length=10, null=True, blank=True)
    status_item = models.CharField('Status', max_length=10)
    data_importacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('pedido', 'produto')
        verbose_name = 'Pedido Protheus'
        verbose_name_plural = 'Pedidos Protheus'
        ordering = ['-emissao', '-pedido']

    def __str__(self):
        return f"Pedido {self.pedido} - Prod {self.produto}"
