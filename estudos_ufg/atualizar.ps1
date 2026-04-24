Write-Host "Iniciando atualizacao completa..." -ForegroundColor Cyan

# 0. Instalar dependencias necessarias (como o Pillow)
Write-Host "Verificando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt

# 1. Gerar Migracoes
Write-Host "Gerando novas migracoes..." -ForegroundColor Yellow
python manage.py makemigrations coordenadoras

# 2. Aplicar Migracoes
Write-Host "Aplicando mudancas no banco de dados..." -ForegroundColor Yellow
python manage.py migrate

Write-Host "Sistema pronto!" -ForegroundColor Green
Write-Host "Iniciando o servidor..." -ForegroundColor Cyan

# 3. Iniciar o servidor
python manage.py runserver
