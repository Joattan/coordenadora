import requests
import os
from dotenv import load_dotenv

load_dotenv()

PROTHEUS_BASE_URL = "http://protheus.ctic.tec.br:53328/rest/OFATR033"

def fetch_protheus_data(camp="0126", mesref="01", setor1="1", setor2="999", empresa="LOG"):
    """
    Busca dados de pedidos no Protheus via API REST.
    """
    auth_key = os.getenv("PROTHEUS_AUTH")
    
    params = {
        "SETOR1": setor1,
        "SETOR2": setor2,
        "MESREF": mesref,
        "CAMP": camp,
        "EMPRESA": empresa
    }
    
    headers = {
        "Authorization": f"Basic {auth_key}"
    }
    
    print(f"-> Iniciando chamada ao Protheus: Camp {camp}, Mes {mesref}")
    try:
        response = requests.get(
            PROTHEUS_BASE_URL, 
            params=params, 
            headers=headers, 
            timeout=600
        )
        print(f"<- Resposta recebida. Status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"<- Dados decodificados. Total de itens: {len(data)}")
        return data
    except Exception as e:
        print(f"!!! Erro ao buscar dados do Protheus: {e}")
        return None

def sync_protheus_to_db(data):
    """
    Salva ou atualiza os dados da API no banco de dados local de forma otimizada.
    """
    from coordenadoras.models import PedidoProtheus
    from django.db import transaction
    
    if not data:
        return 0
    
    count = 0
    novos_pedidos = []
    pedidos_existentes = set(PedidoProtheus.objects.values_list('pedido', 'produto'))
    print(f"-> Pedidos já existentes no banco local: {len(pedidos_existentes)}")
    
    ids_no_pacote = set() # Para evitar duplicados dentro do próprio JSON da API
    
    if data and len(data) > 0:
        print(f"-> Exemplo do 1º item recebido: Pedido {data[0].get('PEDIDO')}, Campanha {data[0].get('CAMPANHA')}")
    
    try:
        with transaction.atomic():
            for item in data:
                pedido_id = item.get("PEDIDO")
                produto_id = item.get("PRODUTO")
                
                if not pedido_id or not produto_id:
                    continue
                    
                chave = (pedido_id, produto_id)
                
                # Só adiciona se não existe no banco E não está repetido no próprio pacote
                if chave not in pedidos_existentes and chave not in ids_no_pacote:
                    vlr_finan = str(item.get("VALOR FINAN", "0")).replace(",", ".")
                    qtd = str(item.get("QTD", "0")).replace(",", ".")
                    
                    novos_pedidos.append(PedidoProtheus(
                        pedido=pedido_id,
                        produto=produto_id,
                        campanha=item.get("CAMPANHA"),
                        ano=item.get("ANO"),
                        setor=item.get("SETOR"),
                        revendedora=item.get("CODIGO"),
                        emissao=item.get("EMISSAO"),
                        quantidade=float(qtd),
                        valor_financeiro=float(vlr_finan),
                        coordenadora=item.get("CODCOORD"),
                        tipo=item.get("TIPO"),
                        tes=item.get("TES"),
                        status_item=item.get("STATUS_ITEM"),
                    ))
                    ids_no_pacote.add(chave)
            
            if novos_pedidos:
                print(f"-> Gravando {len(novos_pedidos)} novos itens no banco local...")
                # ignore_conflicts=True garante que se algo passar, o banco não trava
                PedidoProtheus.objects.bulk_create(novos_pedidos, ignore_conflicts=True)
                count = len(novos_pedidos)
                print(f"<- Gravação concluída.")
            else:
                print("-> Nenhum pedido novo para gravar.")
    except Exception as e:
        print(f"Erro crítico na sincronização: {e}")
        return 0
            
    return count

def summarize_performance(data):
    """
    Gera um resumo dos dados retornados pela API e normaliza chaves.
    """
    if not data:
        return None
    
    summary = {
        "total_pedidos": len(data),
        "total_valor_financeiro": 0,
        "total_valor_cat": 0,
        "pedidos_por_setor": {},
        "pedidos_por_coordenadora": {},
        "raw_data": []
    }
    
    for item in data:
        # Normaliza chaves para o template (remove espaços)
        normalized_item = {k.replace(" ", "_"): v for k, v in item.items()}
        
        # Soma valores
        try:
            vlr_finan = float(str(normalized_item.get("VALOR_FINAN", 0)).replace(",", "."))
            vlr_cat = float(str(normalized_item.get("VLR_CAT", 0)).replace(",", "."))
        except:
            vlr_finan = 0
            vlr_cat = 0
            
        summary["total_valor_financeiro"] += vlr_finan
        summary["total_valor_cat"] += vlr_cat
        
        # Agrupa por setor
        setor = normalized_item.get("SETOR", "S/N")
        summary["pedidos_por_setor"][setor] = summary["pedidos_por_setor"].get(setor, 0) + 1
        
        # Agrupa por coordenadora
        coord = normalized_item.get("CODCOORD", "S/N")
        summary["pedidos_por_coordenadora"][coord] = summary["pedidos_por_coordenadora"].get(coord, 0) + 1
        
        if len(summary["raw_data"]) < 100:
            summary["raw_data"].append(normalized_item)
        
    return summary
