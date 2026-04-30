from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from coordenadoras.models import CandidataCoordenadora
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
import os
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
from .protheus_api import fetch_protheus_data, summarize_performance, sync_protheus_to_db
from coordenadoras.models import PedidoProtheus

load_dotenv()

# Create your views here.

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    import re
    username = request.user.username
    # Tenta buscar pelo CPF puro ou formatado
    cpf_formatado = f"{username[:3]}.{username[3:6]}.{username[6:9]}-{username[9:]}"
    candidata = CandidataCoordenadora.objects.filter(models.Q(cpf=username) | models.Q(cpf=cpf_formatado)).first()
    
    primeiro_nome = ""
    if candidata:
        primeiro_nome = candidata.nome_completo.split()[0]
    
    return render(request, 'core/index.html', {
        'candidata': candidata,
        'primeiro_nome': primeiro_nome
    })

@login_required
def elite(request):
    import re
    username = request.user.username
    cpf_formatado = f"{username[:3]}.{username[3:6]}.{username[6:9]}-{username[9:]}"
    candidata = CandidataCoordenadora.objects.filter(models.Q(cpf=username) | models.Q(cpf=cpf_formatado)).first()
    
    primeiro_nome = ""
    if candidata:
        primeiro_nome = candidata.nome_completo.split()[0]
    
    return render(request, 'core/elite_new.html', {
        'candidata': candidata,
        'primeiro_nome': primeiro_nome
    })

def seja_coordenadora(request):
    return render(request, 'core/seja_coordenadora.html')

def calcular_ganhos_odorata(cad, ped, camp, ticket=300):
    # Regra de negócio: Todo cadastro novo já conta como 1 pedido mínimo
    if ped < cad:
        ped = cad

    # 1. Taxa por cadastro
    rate_cad = 0
    if cad >= 10: rate_cad = 50
    elif cad >= 5: rate_cad = 25
    total_cad = cad * rate_cad

    # 2. Bônus campanha (cadastros ≥ 15)
    bonus_camp_cad = 0
    if cad >= 15:
        if camp == 1: bonus_camp_cad = 600
        elif camp == 2: bonus_camp_cad = 600
        elif camp == 3: bonus_camp_cad = 600
        elif camp == 4: bonus_camp_cad = 300

    # 3. Bateu Levou (Min 5 cads)
    bateu = 0
    if cad >= 5:
        if ped >= 300: bateu = 2000
        elif ped >= 200: bateu = 1500
        elif ped >= 150: bateu = 1200
        elif ped >= 80: bateu = 800
        elif ped >= 50: bateu = 500
        elif ped >= 30: bateu = 300

    # 4. Bônus pedidos por campanha
    bp = 0
    if camp == 1 and ped >= 30: bp = 200
    elif camp == 2 and ped >= 50: bp = 300
    elif camp == 3 and ped >= 70: bp = 400

    # 5. Faturamento (Comissão)
    faturamento = ped * ticket
    perc = 3
    if ped >= 300: perc = 11
    elif ped >= 200: perc = 10
    elif ped >= 150: perc = 9
    elif ped >= 100: perc = 7
    elif ped >= 70: perc = 5
    bonus_fat = faturamento * perc / 100

    # 6. Bônus Dobro (30+ cadastros)
    bonus_dobro = 0
    if cad >= 30:
        bonus_dobro = 500

    total = total_cad + bonus_camp_cad + bateu + bp + bonus_fat + bonus_dobro
    
    return {
        'total': total,
        'detalhes': f"{cad} cads (R$ {rate_cad}/cada), {ped} pedidos, Campanha {camp}, Comissão {perc}%, Bônus Camp {bp}, Bateu Levou {bateu}, Bônus Dobro {bonus_dobro}"
    }

@csrf_exempt
def chat_agente(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
    except:
        return JsonResponse({'error': 'Dados inválidos'}, status=400)

    # Recupera memória de números da sessão para manter contexto
    cad = request.session.get('last_cad', 0)
    ped = request.session.get('last_ped', 0)
    camp = request.session.get('last_camp', 1)
    ticket = request.session.get('last_ticket', 300)
    
    user_msg_lower = user_message.lower()
    nums = [int(n) for n in re.findall(r'\d+', user_message)]
    calc_context = ""
    
    # Se houver números, atualizamos a memória de forma inteligente
    if nums:
        # Identifica Campanha
        camp_match = re.search(r'(\d+)\s*(?:camp|ciclo)', user_msg_lower)
        if camp_match:
            camp = int(camp_match.group(1))
        
        # Identifica Ticket Médio (valores altos ou palavra chave)
        if any(k in user_msg_lower for k in ["tick", "medio", "valor"]) or (nums and nums[0] > 100 and "cad" not in user_msg_lower):
            ticket = nums[0]
        
        # Identifica Cadastros e Pedidos
        if "cad" in user_msg_lower:
            cad = nums[0]
            if len(nums) > 1 and "ped" in user_msg_lower: ped = nums[1]
        elif "ped" in user_msg_lower or "vend" in user_msg_lower:
            ped = nums[0]
            if len(nums) > 1 and "cad" in user_msg_lower: cad = nums[1]
        elif not camp_match:
            # Se não houver palavras chave, assume a ordem padrão (cad, ped)
            cad = nums[0]
            if len(nums) > 1: ped = nums[1]
            
        # Salva o novo estado na sessão
        request.session['last_cad'] = cad
        request.session['last_ped'] = ped
        request.session['last_camp'] = camp
        request.session['last_ticket'] = ticket
            
    # Sempre gera o contexto se houver dados mínimos (pedidos ou cadastros)
    if cad > 0 or ped > 0:
        res = calcular_ganhos_odorata(cad, ped, camp, ticket)
        calc_context = f"\nCALCULADORA (DADOS REAIS): VALOR TOTAL FINAL A RECEBER = R$ {res['total']}. Detalhes: {res['detalhes']}."

    # System Prompt (Dora - Mentora e Especialista)
    system_prompt = (
        "Você é a Dora da Odorata. Responda de forma curta (máx 3-4 linhas) e profissional.\n\n"
        "REQUISITOS PARA SER COORDENADORA:\n"
        "- CNPJ ativo e contrato assinado.\n"
        "- Enviar documentos pessoais, conta corrente e ter ensino médio.\n"
        "- Residir na cidade base. NÃO exige exclusividade.\n\n"
        "REGRAS DE NEGÓCIO:\n"
        "- CADASTROS: 5-9 (R$ 25) | 10+ (R$ 50) | Meta 15+ (Bônus R$ 300-600) | 30+ (Bônus Dobro R$ 500).\n"
        "- BATEU LEVOU (pedidos): 30 (300) | 50 (500) | 80 (800) | 150 (1200) | 200 (1500) | 300 (2000).\n"
        "- COMISSÃO: 3% a 11% sobre o faturamento total.\n\n"
        "PROTOCOLOS:\n"
        "- SAUDAÇÃO: Apenas 'Olá! Como posso te ajudar?'. Proibido dar dicas no 'Oi'.\n"
        "- CÁLCULOS: Use sempre os dados do 'CALCULADORA (DADOS REAIS)' e dê a SOMA TOTAL FINAL.\n"
        + calc_context
    )

    try:
        from groq import Groq
        groq_key = os.environ.get('GROQ_API_KEY')
        if not groq_key: return JsonResponse({'response': "Erro: GROQ_API_KEY não configurada."})

        client = Groq(api_key=groq_key)
        
        # Mudança de chave para resetar memória
        session_key = 'dora_v6_final_check'
        history = request.session.get(session_key, [])
        history.append({"role": "user", "content": user_message})
        
        # Mantém as últimas 5 mensagens para ter contexto de cálculos anteriores
        messages_to_send = [{"role": "system", "content": system_prompt}] + history[-5:]
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_to_send,
            temperature=0,
            max_tokens=250
        )
        
        ai_msg = completion.choices[0].message.content
        history.append({"role": "assistant", "content": ai_msg})
        request.session[session_key] = history[-10:] # Guarda até 10 mensagens
        request.session.modified = True

        return JsonResponse({'response': ai_msg})
    except Exception as e:
        return JsonResponse({'response': f"Dora: Tive um pequeno problema. Pode repetir? (Erro: {str(e)})"})


def brl(v):
    return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    links = [
        {'title': 'Páginas Públicas', 'urls': [
            {'name': 'Landing Page (Seja Coordenadora)', 'url': '/seja-coordenadora/'},
            {'name': 'Cadastro de Novas Consultoras (Oficial)', 'url': 'https://ambientevirtual.odorata.com.br/pre-cadastro?_gl=1%2a1gtdomn%2a_gcl_aw%2aR0NMLjE3NzYyNzIyNTMuQ2p3S0NBanc3dnpPQmhCeEVpd0FjN1dOcjZwRmRtNndQa3ZyU2E4VHlMNTBhcFJUbnI5aTNPT3BnUkI1aUJnNS16Vkt5Z0dWTFMweTR4b0NfR0VRQXZEX0J3RQ..%2a_gcl_au%2aMTEyMzA0MTEzMS4xNzc2MjcxMTg5%2a_ga%2aMTQ5MzE0MDA1Ny4xNzI2ODYwODQ0%2a_ga_H278Y0TMM1%2aczE3NzcwMzkyNTEkbzI4JGcxJHQxNzc3MDM5MjczJGozOCRsMCRoMA..%2a_ga_ZK2YT4K3XL%2aczE3NzcwMzkyNTIkbzE5JGcxJHQxNzc3MDM5MjczJGozOSRsMCRoMA..%2a_ga_6S9V3M68PS%2aczE3NzcwMzkyNTIkbzE5JGcxJHQxNzc3MDM5MjczJGozOSRsMCRoMA..'},
            {'name': 'Página Inicial (Guia Logada)', 'url': '/'},
        ]},
        {'title': 'Programas e Ferramentas', 'urls': [
            {'name': 'Elite da Beleza', 'url': '/elite/'},
            {'name': 'Agente Dora (Chat Inteligente)', 'url': '/chat/'},
            {'name': 'Performance de Vendas (Protheus)', 'url': '/performance/'},
        ]},
        {'title': 'Administração e Segurança', 'urls': [
            {'name': 'Listagem Geral de Candidatas', 'url': '/coordenadoras/admin/listagem/'},
            {'name': 'Gestão de Usuários (Acessos)', 'url': '/admin/auth/user/'},
            {'name': 'Banco de Dados (Django Admin)', 'url': '/admin/'},
        ]},
    ]
    return render(request, 'core/admin_dashboard.html', {'links': links})

@login_required
def performance_vendas(request):
    camp = request.GET.get('camp', '0126')
    mesref = request.GET.get('mesref', '01')
    force_sync = request.GET.get('sync') == '1'
    
    # Recupera o código protheus da coordenadora logada
    cod_protheus = None
    try:
        # Tenta buscar pelo CPF (username)
        candidata = CandidataCoordenadora.objects.get(cpf=request.user.username)
        cod_protheus = candidata.cod_protheus
    except CandidataCoordenadora.DoesNotExist:
        # Se não encontrar, tenta buscar se o usuário tem um perfil vinculado de outra forma ou se é admin
        pass

    # Verifica se já temos dados no banco local para essa campanha
    # Filtro base por campanha
    pedidos_locais = PedidoProtheus.objects.filter(campanha=camp)
    
    # Se não for superusuário, OBRIGATORIAMENTE filtra pelo código dela
    if not request.user.is_superuser:
        if cod_protheus:
            pedidos_locais = pedidos_locais.filter(coordenadora=cod_protheus)
        else:
            # Se não tem código vinculado, não vê nada por segurança
            pedidos_locais = pedidos_locais.none()

    novos_itens = 0
    # Se não houver dados ou o usuário forçar a sincronização
    # Importante: A sincronização baixa TUDO da API, o filtro acontece na exibição acima
    if force_sync or not pedidos_locais.exists():
        raw_data = fetch_protheus_data(camp=camp, mesref=mesref)
        if raw_data:
            novos_itens = sync_protheus_to_db(raw_data)
            # Recarrega do banco após sincronizar (aplicando os mesmos filtros)
            pedidos_locais = PedidoProtheus.objects.filter(campanha=camp)
            if not request.user.is_superuser:
                if cod_protheus:
                    pedidos_locais = pedidos_locais.filter(coordenadora=cod_protheus)
                else:
                    pedidos_locais = pedidos_locais.none()

    # Prepara o sumário com base nos dados do banco local e filtros DAX
    # Regra: Faturamento > 0, Tipo = Pedido Normal, Status = Atendido (A)
    pedidos_validados = pedidos_locais.filter(
        valor_financeiro__gt=0,
        tipo="Pedido Normal",
        status_item="A"
    )

    total_pedidos_itens = pedidos_validados.count()
    # Clientes = DISTINCTCOUNT(Revendedora + Campanha)
    total_clientes = pedidos_validados.values('revendedora', 'campanha').distinct().count()
    
    total_valor_financeiro = pedidos_validados.aggregate(models.Sum('valor_financeiro'))['valor_financeiro__sum'] or 0
    ticket_medio = total_valor_financeiro / total_clientes if total_clientes > 0 else 0
    
    # Formata para o template (estilo raw_data que o template espera)
    display_data = []
    for p in pedidos_validados.order_by('-emissao', '-pedido')[:100]:
        display_data.append({
            'PEDIDO': p.pedido,
            'EMISSAO': p.emissao,
            'SETOR': p.setor,
            'CODCOORD': p.coordenadora,
            'VALOR_FINAN': p.valor_financeiro,
            'STATUS_ITEM': p.status_item,
            'TIPO': p.tipo,
            'TES': p.tes
        })

    summary = {
        "total_pedidos": total_clientes, # Agora usamos a contagem de clientes reais
        "total_itens": total_pedidos_itens,
        "total_valor_financeiro": total_valor_financeiro,
        "raw_data": display_data
    }
        
    return render(request, 'core/performance.html', {
        'summary': summary,
        'ticket_medio': ticket_medio,
        'camp': camp,
        'novos_itens': novos_itens
    })

