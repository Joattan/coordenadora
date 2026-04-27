import urllib.request
import json
import re

def validate_cpf(cpf):
    """
    Valida o formato do CPF usando o algoritmo oficial.
    """
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11:
        return False
    
    # CPFs com todos os dígitos iguais são inválidos
    if cpf == cpf[0] * 11:
        return False
    
    # Cálculo dos dígitos verificadores
    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != int(cpf[i]):
            return False
    return True

def get_name_by_cpf(cpf):
    """
    Apenas valida o CPF, sem retornar um nome fictício,
    conforme solicitado pelo usuário.
    """
    cpf_clean = re.sub(r'\D', '', cpf)
    if validate_cpf(cpf_clean):
        return {
            "success": True, 
            "message": "CPF válido."
        }
    return {"success": False, "error": "CPF inválido."}

def get_address_by_cep(cep):
    """
    Busca o endereço pelo CEP via ViaCEP usando urllib para evitar dependências externas.
    """
    cep_clean = re.sub(r'\D', '', cep)
    if len(cep_clean) != 8:
        return {"success": False, "error": "CEP deve conter 8 dígitos."}
    
    url = f"https://viacep.com.br/ws/{cep_clean}/json/"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            if "erro" in data:
                return {"success": False, "error": "CEP não encontrado na base do ViaCEP."}
            
            return {
                "success": True,
                "rua": data.get("logradouro", ""),
                "bairro": data.get("bairro", ""),
                "cidade": data.get("localidade", ""),
                "estado": data.get("uf", ""),
            }
    except Exception as e:
        return {"success": False, "error": f"Erro de conexão: {str(e)}"}
