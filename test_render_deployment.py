#!/usr/bin/env python3
"""
Script para testar o deploy no Render antes de subir
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_environment():
    """Testa se as variáveis de ambiente estão configuradas"""
    print("🔧 Verificando variáveis de ambiente...")

    required_vars = ['PINECONE_API_KEY', 'GOOGLE_API_KEY', 'PINECONE_INDEX_NAME']
    all_ok = True

    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value[:10])}...{value[-4:] if len(value) > 10 else value}")
        else:
            print(f"❌ {var}: Não configurada")
            all_ok = False

    return all_ok

def test_imports():
    """Testa se todas as dependências podem ser importadas"""
    print("\n📦 Testando imports...")

    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")

        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")

        import pinecone
        print(f"✅ Pinecone: {pinecone.__version__}")

        import google.generativeai as genai
        print("✅ Google Generative AI: OK")

        from agente_busca_gemini import AgenteBuscaGemini
        print("✅ AgenteBuscaGemini: OK")

        return True

    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False

def test_agent_initialization():
    """Testa a inicialização do agente"""
    print("\n🤖 Testando inicialização do agente...")

    try:
        from agente_busca_gemini import AgenteBuscaGemini

        print("🚀 Inicializando agente...")
        start_time = time.time()

        agente = AgenteBuscaGemini()

        end_time = time.time()
        print(".2f"        print("✅ Agente inicializado com sucesso!")

        # Teste de conectividade
        print("🔍 Testando conectividade com Pinecone...")
        test_results = agente.buscar_no_pinecone("teste", top_k=1)

        if test_results:
            print(f"✅ Pinecone: {len(test_results)} resultados encontrados")
        else:
            print("⚠️ Pinecone: Conexão OK, mas nenhum resultado encontrado")

        return True

    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False

def test_frontend_files():
    """Verifica se os arquivos do frontend estão presentes"""
    print("\n🌐 Verificando arquivos do frontend...")

    required_files = [
        'frontend/app_fastapi.py',
        'frontend/requirements.txt',
        'frontend/templates/index.html',
        'frontend/static/js/chat.js'
    ]

    all_present = True

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Arquivo não encontrado")
            all_present = False

    return all_present

def main():
    """Executa todos os testes"""
    print("🚀 TESTE DE DEPLOY - VIVI IA")
    print("=" * 50)

    tests = [
        ("Variáveis de ambiente", test_environment),
        ("Imports das dependências", test_imports),
        ("Arquivos do frontend", test_frontend_files),
        ("Inicialização do agente", test_agent_initialization)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🔬 Executando: {test_name}")
        result = test_func()
        results.append((test_name, result))

    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Pronto para deploy no Render!")
        print("\n📋 Próximos passos:")
        print("1. Faça commit e push das mudanças")
        print("2. Acesse o Render e faça deploy")
        print("3. Monitore os logs durante a inicialização")
        print("4. Teste a aplicação após o deploy")
    else:
        print("❌ Alguns testes falharam!")
        print("🔧 Corrija os problemas antes do deploy.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
