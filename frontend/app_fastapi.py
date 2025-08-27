#!/usr/bin/env python3
"""
Frontend FastAPI para o Agente RAG Vivi IA
Interface web para consultas sobre SIAPE e gestão pública
"""

import os
import sys
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# Adicionar o diretório pai ao path para importar o agente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agente_busca_gemini import AgenteBuscaGemini

# Carregar variáveis de ambiente
load_dotenv()

app = FastAPI(title="Vivi IA - Agente RAG", version="1.0.0")

# Configurar templates e arquivos estáticos
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Inicializar o agente na startup
agente = None
agente_inicializado = False

class PerguntaRequest(BaseModel):
    pergunta: str

def inicializar_agente():
    """Inicializa o agente RAG na startup com timeout e retry"""
    global agente, agente_inicializado
    if not agente_inicializado:
        max_tentativas = 5
        for tentativa in range(max_tentativas):
            try:
                print(f"🚀 Inicializando agente RAG... (tentativa {tentativa + 1}/{max_tentativas})")
                agente = AgenteBuscaGemini()
                agente_inicializado = True
                print("✅ Agente RAG inicializado com sucesso!")

                # Teste de conectividade
                try:
                    test_result = agente.buscar_no_pinecone("teste", top_k=1)
                    if test_result:
                        print("✅ Conectividade com Pinecone OK!")
                    else:
                        print("⚠️ Pinecone retornou vazio, mas conexão OK")
                except Exception as test_error:
                    print(f"⚠️ Teste de conectividade falhou: {test_error}")

                return True

            except Exception as e:
                print(f"❌ Erro na tentativa {tentativa + 1}: {e}")
                if tentativa < max_tentativas - 1:
                    print("⏳ Aguardando antes da próxima tentativa...")
                    import time
                    time.sleep(2)  # Espera 2 segundos entre tentativas
                else:
                    print("❌ Todas as tentativas falharam")
                    agente_inicializado = False
                    return False
    return True

def get_agente():
    """Retorna o agente RAG, inicializando se necessário"""
    global agente, agente_inicializado

    if not agente_inicializado:
        if not inicializar_agente():
            return None

    # Verificar se o agente ainda está ativo
    try:
        # Teste simples para ver se o agente responde
        if hasattr(agente, 'pc') and agente.pc is not None:
            return agente
        else:
            # Re-inicializar se necessário
            print("🔄 Re-inicializando agente...")
            return inicializar_agente() and agente
    except Exception as e:
        print(f"⚠️ Agente com problemas, re-inicializando: {e}")
        agente_inicializado = False
        return inicializar_agente() and agente

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal do frontend"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
async def startup_event():
    """Inicializar agente na startup da aplicação"""
    print("🌟 Iniciando Vivi IA - Sistema RAG...")
    inicializar_agente()

@app.get("/api/health")
async def health_check():
    """Verificação de saúde completa da API"""
    try:
        health_status = {
            'status': 'checking',
            'agent_initialized': agente_inicializado,
            'checks': {}
        }

        # Verificar se agente está inicializado
        agente = get_agente()
        if agente:
            health_status['checks']['agent_initialization'] = '✅ OK'

            # Testar conectividade com Pinecone
            try:
                test_pinecone = agente.buscar_no_pinecone("teste de conectividade", top_k=1)
                health_status['checks']['pinecone_connection'] = '✅ OK'
            except Exception as pinecone_error:
                health_status['checks']['pinecone_connection'] = f'❌ {str(pinecone_error)}'

            health_status['status'] = 'healthy'
            health_status['message'] = 'Vivi IA funcionando normalmente'

        else:
            health_status['status'] = 'unhealthy'
            health_status['checks']['agent_initialization'] = '❌ Agente não inicializado'
            health_status['message'] = 'Vivi IA não pôde ser inicializada'

        return health_status

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erro na verificação de saúde: {str(e)}',
            'error_details': str(e)
        }

@app.get("/api/diagnostics")
async def diagnostics():
    """Diagnóstico detalhado do sistema"""
    try:
        import os
        import platform

        diagnostics_info = {
            'system': {
                'platform': platform.system(),
                'python_version': platform.python_version(),
                'environment': os.environ.get('ENVIRONMENT', 'unknown')
            },
            'agent': {
                'initialized': agente_inicializado,
                'type': 'AgenteBuscaGemini' if agente else None
            },
            'environment_variables': {
                'PINECONE_API_KEY': '✅ Configurada' if os.getenv('PINECONE_API_KEY') else '❌ Não configurada',
                'GOOGLE_API_KEY': '✅ Configurada' if os.getenv('GOOGLE_API_KEY') else '❌ Não configurada',
                'PINECONE_INDEX_NAME': os.getenv('PINECONE_INDEX_NAME', '❌ Não configurada')
            }
        }

        # Testar conectividade se agente estiver inicializado
        if agente_inicializado and agente:
            try:
                pinecone_test = agente.buscar_no_pinecone("diagnostics test", top_k=1)
                diagnostics_info['connectivity'] = {
                    'pinecone': '✅ OK',
                    'results_count': len(pinecone_test) if pinecone_test else 0
                }
            except Exception as conn_error:
                diagnostics_info['connectivity'] = {
                    'pinecone': f'❌ {str(conn_error)}'
                }

        return diagnostics_info

    except Exception as e:
        return {
            'error': f'Erro no diagnóstico: {str(e)}'
        }

@app.post("/api/buscar")
async def buscar(request: PerguntaRequest):
    """API para executar buscas no agente RAG com retry automático e timeout"""
    try:
        pergunta = request.pergunta.strip()

        if not pergunta:
            raise HTTPException(status_code=400, detail='Pergunta não pode estar vazia')

        print(f"🔍 Processando pergunta: '{pergunta}'")

        # Tentativas de obter o agente (até 5 tentativas no Render)
        agente = None
        max_tentativas_agente = 5

        for tentativa in range(max_tentativas_agente):
            agente = get_agente()
            if agente:
                print(f"✅ Agente obtido na tentativa {tentativa + 1}")
                break

            print(f"⚠️ Tentativa {tentativa + 1}/{max_tentativas_agente} de obter agente falhou")
            if tentativa < max_tentativas_agente - 1:
                import asyncio
                await asyncio.sleep(2)  # Pausa maior entre tentativas no Render

        if not agente:
            raise HTTPException(status_code=500, detail='Não foi possível inicializar Vivi IA após várias tentativas')

        # Executar busca com múltiplas tentativas
        max_tentativas_busca = 3

        for tentativa_busca in range(max_tentativas_busca):
            try:
                print(f"🔍 Executando busca (tentativa {tentativa_busca + 1}/{max_tentativas_busca})...")

                # Timeout maior para o Render
                resposta = agente.executar_busca_completa(pergunta)

                print(f"✅ Busca concluída com sucesso!")
                return {
                    'success': True,
                    'resposta': resposta,
                    'pergunta': pergunta
                }

            except Exception as busca_error:
                print(f"❌ Erro na tentativa {tentativa_busca + 1}: {busca_error}")

                if tentativa_busca < max_tentativas_busca - 1:
                    print("🔄 Tentando novamente em alguns segundos...")
                    import asyncio
                    await asyncio.sleep(3)  # Pausa entre tentativas de busca

                    # Resetar agente se necessário
                    if tentativa_busca >= 1:
                        print("🔄 Resetando agente...")
                        global agente_inicializado
                        agente_inicializado = False
                        agente = get_agente()
                else:
                    print(f"❌ Todas as {max_tentativas_busca} tentativas de busca falharam")

        raise HTTPException(status_code=500, detail=f'Erro na busca após {max_tentativas_busca} tentativas: {str(busca_error)}')

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        raise HTTPException(status_code=500, detail=f'Erro interno inesperado: {str(e)}')

if __name__ == "__main__":
    print("🚀 Iniciando Vivi IA - Sistema RAG...")
    print("🌐 Acesse: http://localhost:5001")

    # Verificar se o agente pode ser inicializado
    if inicializar_agente():
        print("✅ Vivi IA pronta para uso!")
    else:
        print("⚠️ Vivi IA com problemas de inicialização")

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
