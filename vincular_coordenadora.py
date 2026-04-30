import os
import django

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from coordenadoras.models import CandidataCoordenadora
from django.contrib.auth.models import User

def vincular():
    cpf_alvo = '98469347187'
    cod_protheus_alvo = '1025454'
    
    print(f"--- Iniciando Vínculo da Coordenadora ---")
    
    # 1. Busca a candidata pelo CPF
    try:
        candidata = CandidataCoordenadora.objects.get(cpf=cpf_alvo)
        candidata.cod_protheus = cod_protheus_alvo
        candidata.save()
        print(f"OK: Candidata {candidata.nome_completo} vinculada ao código {cod_protheus_alvo}.")
    except CandidataCoordenadora.DoesNotExist:
        print(f"ERRO: Não encontrei nenhuma candidata com o CPF {cpf_alvo}.")
        return

    # 2. Garante que o usuário Django existe e o username é o CPF
    user, created = User.objects.get_or_create(username=cpf_alvo)
    if created:
        user.set_password('odorata123') # Senha padrão se criar agora
        user.save()
        print(f"OK: Usuário criado para o CPF {cpf_alvo}.")
    else:
        print(f"OK: Usuário já existia.")

    print(f"--- Vínculo concluído com sucesso! ---")
    print(f"Agora, ao logar com {cpf_alvo}, a tela de performance mostrará os dados do código {cod_protheus_alvo}.")

if __name__ == "__main__":
    vincular()
