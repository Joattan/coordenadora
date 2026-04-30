import shutil
import os

# Caminhos
origem_pasta = r"C:\JGA\JGA\coordenadora\core\static\core\images"
destino_pasta = r"c:\JGA\JGA\estudos_ufg\core\static\core\images"

imagens = [
    "material01.png", "treinamento.png", "Participacao.png", "Celular.png",
    "c01.png", "c02.png", "c03.png", "c04.png"
]

print(f"Iniciando a cópia das imagens...")

for img in imagens:
    origem = os.path.join(origem_pasta, img)
    destino = os.path.join(destino_pasta, img)
    
    try:
        if os.path.exists(origem):
            shutil.copy(origem, destino)
            print(f"✅ Sucesso: {img} copiado.")
        else:
            print(f"❌ Erro: {img} não encontrado em {origem_pasta}")
    except Exception as e:
        print(f"❌ Erro ao copiar {img}: {e}")

print("Fim do processo.")
