import shutil
import os

# Caminhos
origem = r"C:\Users\joattan.aquino.CTIC\.gemini\antigravity\brain\5751e045-f431-4fba-beaf-26d6197af7ff\coordenadora_hero_v2_png_1776716692528.png"
destino_pasta = r"c:\JGA\JGA\estudos_ufg\core\static\core\images"
destino_arquivo = os.path.join(destino_pasta, "coordenadora_hero.png")

print(f"Tentando mover o banner...")

try:
    if not os.path.exists(destino_pasta):
        os.makedirs(destino_pasta)
    
    shutil.copy(origem, destino_arquivo)
    print(f"✅ SUCESSO! O banner foi salvo em: {destino_arquivo}")
    print(f"Agora é só atualizar o site com Ctrl+F5.")
except Exception as e:
    print(f"❌ ERRO: {e}")
    print(f"Certifique-se de que o arquivo de origem ainda existe no caminho dos artefatos.")
