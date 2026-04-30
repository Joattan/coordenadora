import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_api():
    auth_key = os.getenv("PROTHEUS_AUTH")
    url = "http://protheus.ctic.tec.br:53328/rest/OFATR033"
    
    # Testamos 3 variações
    tests = [
        {"camp": "0126", "mes": "01"},
        {"camp": "0126", "mes": "04"},
        {"camp": "0125", "mes": "01"},
    ]
    
    headers = {
        "Authorization": f"Basic {auth_key}"
    }
    
    for t in tests:
        params = {
            "SETOR1": "1",
            "SETOR2": "999",
            "MESREF": t["mes"],
            "CAMP": t["camp"],
            "EMPRESA": "LOG"
        }
        
        print(f"--- Testando Campanha {t['camp']} / Mês {t['mes']} ---")
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Registros retornados: {len(data)}")
                if len(data) > 0:
                    print(f"Exemplo do primeiro item: {data[0]}")
            else:
                print(f"Erro: {response.text}")
        except Exception as e:
            print(f"Erro na requisição: {e}")
        print("\n")

if __name__ == "__main__":
    test_api()
