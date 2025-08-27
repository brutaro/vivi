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
    """Inicializa o agente RAG na startup"""
    global agente, agente_inicializado
    if not agente_inicializado:
        try:
            print("🚀 Inicializando agente RAG...")
            agente = AgenteBuscaGemini()
            agente_inicializado = True
            print("✅ Agente RAG inicializado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao inicializar agente: {e}")
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
    """Verificação de saúde da API"""
    try:
        agente = get_agente()
        if agente:
            return {
                'status': 'healthy',
                'message': 'Vivi IA funcionando normalmente',
                'agent_type': 'AgenteBuscaGemini',
                'agent_initialized': agente_inicializado
            }
        else:
            raise HTTPException(status_code=500, detail='Vivi IA não pôde ser inicializada')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro na verificação de saúde: {str(e)}')

@app.post("/api/buscar")
async def buscar(request: PerguntaRequest):
    """API para executar buscas no agente RAG com retry automático"""
    try:
        pergunta = request.pergunta.strip()

        if not pergunta:
            raise HTTPException(status_code=400, detail='Pergunta não pode estar vazia')

        print(f"🔍 Processando pergunta: {pergunta}")

        # Tentativas de obter o agente (até 3 tentativas)
        agente = None
        for tentativa in range(3):
            agente = get_agente()
            if agente:
                break
            print(f"⚠️ Tentativa {tentativa + 1} de obter agente falhou, tentando novamente...")
            import asyncio
            await asyncio.sleep(1)  # Pequena pausa entre tentativas

        if not agente:
            raise HTTPException(status_code=500, detail='Não foi possível inicializar Vivi IA após várias tentativas')

        # Executar busca com timeout
        try:
            resposta = agente.executar_busca_completa(pergunta)

            return {
                'success': True,
                'resposta': resposta,
                'pergunta': pergunta
            }

        except Exception as busca_error:
            print(f"❌ Erro na busca: {busca_error}")
            # Tentar uma vez mais com agente fresco
            print("🔄 Tentando com agente fresco...")
            global agente_inicializado
            agente_inicializado = False

            agente_fresco = get_agente()
            if agente_fresco:
                try:
                    resposta = agente_fresco.executar_busca_completa(pergunta)
                    return {
                        'success': True,
                        'resposta': resposta,
                        'pergunta': pergunta
                    }
                except Exception as segunda_tentativa_error:
                    print(f"❌ Segunda tentativa também falhou: {segunda_tentativa_error}")

            raise HTTPException(status_code=500, detail=f'Erro na busca após duas tentativas: {str(busca_error)}')

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
