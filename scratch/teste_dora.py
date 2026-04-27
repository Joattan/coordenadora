import os
import json
import requests

def test_dora():
    url = "http://127.0.0.1:8000/chat_agente/"
    payload = {
        "message": "Oi Dora! Sou nova, estou na minha 2ª campanha. Consegui 18 cadastros e 40 pedidos. Quanto vou ganhar?"
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Resposta da Dora: {response.json().get('response')}")
    except Exception as e:
        print(f"Erro ao conectar no servidor: {e}")

if __name__ == "__main__":
    test_dora()
