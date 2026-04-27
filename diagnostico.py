import os
import sys

print("--- DIAGNÓSTICO DO DJANGO ---")
try:
    import django
    print(f"Django Versão: {django.get_version()}")
except ImportError:
    print("ERRO: Django não instalado!")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    from django.conf import settings
    print(f"WSGI_APPLICATION configurado como: '{settings.WSGI_APPLICATION}'")
except Exception as e:
    print(f"ERRO ao carregar settings: {e}")

try:
    from config.wsgi import application
    print("Aplicação WSGI carregada com SUCESSO!")
except Exception as e:
    print(f"ERRO ao carregar WSGI application: {e}")
    import traceback
    traceback.print_exc()
