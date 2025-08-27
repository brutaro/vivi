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

# Inicializar o agente
agente = None

class PerguntaRequest(BaseModel):
    pergunta: str

def get_agente():
    """Inicializa e retorna o agente RAG"""
    global agente
    if agente is None:
        try:
            agente = AgenteBuscaGemini()
            print("🤖 Agente RAG inicializado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao inicializar agente: {e}")
            return None
    return agente

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal do frontend"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """Verificação de saúde da API"""
    try:
        agente = get_agente()
        if agente:
            return {
                'status': 'healthy',
                'message': 'Agente RAG funcionando normalmente',
                'agent_type': 'AgenteBuscaGemini'
            }
        else:
            raise HTTPException(status_code=500, detail='Agente RAG não pôde ser inicializado')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro na verificação de saúde: {str(e)}')

@app.post("/api/buscar")
async def buscar(request: PerguntaRequest):
    """API para executar buscas no agente RAG"""
    try:
        pergunta = request.pergunta.strip()
        
        if not pergunta:
            raise HTTPException(status_code=400, detail='Pergunta não pode estar vazia')
        
        # Obter agente
        agente = get_agente()
        if not agente:
            raise HTTPException(status_code=500, detail='Erro ao inicializar agente RAG')
        
        print(f"🔍 Processando pergunta: {pergunta}")
        
        # Executar busca
        resposta = agente.executar_busca_completa(pergunta)

        return {
            'success': True,
            'resposta': resposta,
            'pergunta': pergunta
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        raise HTTPException(status_code=500, detail=f'Erro interno: {str(e)}')

if __name__ == "__main__":
    print("🚀 Iniciando servidor FastAPI para frontend do Agente RAG...")
    print("🌐 Acesse: http://localhost:5001")
    
    # Verificar se o agente pode ser inicializado
    if get_agente():
        print("✅ Agente RAG pronto!")
    else:
        print("⚠️ Agente RAG com problemas de inicialização")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
