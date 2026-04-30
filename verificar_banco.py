import os
import django
import sys

# Configura o ambiente Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from coordenadoras.models import PedidoProtheus

def check():
    total = PedidoProtheus.objects.count()
    print(f"\n=== DIAGNÓSTICO DO BANCO ===")
    print(f"Total de registros na tabela PedidoProtheus: {total}")
    
    if total > 0:
        print("\n--- Primeiros 5 registros salvos: ---")
        for p in PedidoProtheus.objects.all()[:5]:
            print(f"Pedido: {p.pedido}")
            print(f"  - Campanha: '{p.campanha}'")
            print(f"  - Tipo: '{p.tipo}'")
            print(f"  - Status Item: '{p.status_item}'")
            print(f"  - Valor Financeiro: {p.valor_financeiro}")
            print("-" * 30)
            
        # Testa o filtro que usamos na View
        camp = "0126"
        filtrados = PedidoProtheus.objects.filter(
            campanha=camp,
            valor_financeiro__gt=0,
            tipo="Pedido Normal",
            status_item="A"
        )
        print(f"\n--- Teste de Filtro (Campanha {camp}) ---")
        print(f"Pedidos que passam no filtro (Normal/Atendido/Vlr > 0): {filtrados.count()}")
        
        if filtrados.count() == 0:
            print("\nAVISO: O filtro está retornando ZERO. Verifique se os textos (Tipo/Status) batem exatamente com os dados acima.")

if __name__ == "__main__":
    check()
