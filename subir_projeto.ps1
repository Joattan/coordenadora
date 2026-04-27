# Script de Auto-Fix e Inicialização do Projeto
Write-Host "Limpando processos antigos do Python..." -ForegroundColor Cyan
Stop-Process -Name python -ErrorAction SilentlyContinue

Write-Host "Entrando na pasta do projeto e ativando ambiente..." -ForegroundColor Cyan
cd "c:\JGA\JGA\estudos_ufg"
.\.venv\Scripts\activate

Write-Host "Coletando arquivos estáticos..." -ForegroundColor Cyan
python manage.py collectstatic --noinput

Write-Host "Aplicando migrações do banco de dados..." -ForegroundColor Cyan
python manage.py migrate

Write-Host "Iniciando o servidor na porta 8000..." -ForegroundColor Green
python manage.py runserver 8000
