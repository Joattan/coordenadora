import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from coordenadoras.models import PedidoProtheus, CandidataCoordenadora
from django.contrib.auth.models import User

def debug_data():
    cpf = '98469347187'
    cod_protheus = '1025454'
    campanha = '0126'
    
    print(f"--- DEBUG DE DADOS PERFORMANCE ---")
    
    # 1. Verifica Candidata
    try:
        cand = CandidataCoordenadora.objects.get(cpf=cpf)
        print(f"OK: Candidata encontrada: {cand.nome_completo}")
        print(f"Vínculo Protheus: '{cand.cod_protheus}' (Deveria ser '{cod_protheus}')")
    except:
        print(f"ERRO: Candidata com CPF {cpf} não encontrada.")

    # 2. Verifica Pedidos no Banco para essa Coordenadora
    print(f"\nBuscando pedidos para Coordenadora '{cod_protheus}' na Campanha '{campanha}'...")
    pedidos = PedidoProtheus.objects.filter(coordenadora=cod_protheus, campanha=campanha)
    print(f"Total encontrado: {pedidos.count()}")
    
    if pedidos.count() == 0:
        print("\nAVISO: Não há pedidos para essa coordenadora no banco local.")
        # Busca um exemplo de qualquer pedido para ver como os dados estão vindo
        exemplo = PedidoProtheus.objects.filter(campanha=campanha).first()
        if exemplo:
            print(f"Exemplo de pedido no banco (qualquer coord):")
            print(f"  - Pedido: {exemplo.pedido}")
            print(f"  - Coordenadora no banco: '{exemplo.coordenadora}'")
            print(f"  - Campanha no banco: '{exemplo.campanha}'")
            print(f"  - Status: '{exemplo.status_item}'")
            print(f"  - Tipo: '{exemplo.tipo}'")
        else:
            print("ERRO: Não há NENHUM pedido para a campanha 0126 no banco.")

    # 3. Verifica filtros aplicados na View
    print(f"\nSimulando filtros da View (Apenas 'A' e 'Pedido Normal'):")
    validados = pedidos.filter(valor_financeiro__gt=0, tipo="Pedido Normal", status_item="A")
    print(f"Total validados: {validados.count()}")

if __name__ == "__main__":
    debug_data()
