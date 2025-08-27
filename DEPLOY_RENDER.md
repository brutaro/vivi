# 🚀 Deploy da Vivi IA no Render

## 📋 Pré-requisitos

1. **Conta no Render**: [render.com](https://render.com)
2. **Chaves de API**:
   - PINECONE_API_KEY
   - GOOGLE_API_KEY
   - PINECONE_INDEX_NAME (vivi-ia-base)

## 📁 Estrutura do Projeto

```
agente-rag2/
├── frontend/
│   ├── app_fastapi.py       # Servidor principal
│   ├── requirements.txt     # Dependências
│   ├── templates/
│   │   └── index.html       # Interface web
│   └── static/
│       └── js/
│           └── chat.js      # JavaScript do chat
├── agente_busca_gemini.py   # Agente RAG
├── render.yaml             # Configuração do Render
├── runtime.txt            # Versão do Python
└── env.example           # Exemplo de variáveis de ambiente
```

## 🚀 Passos para Deploy

### 1. Preparar o Repositório

```bash
# Certifique-se de que está na branch main
git checkout main
git add .
git commit -m "Deploy da Vivi IA no Render"
git push origin main
```

### 2. Deploy no Render

1. **Acesse [render.com](https://render.com)**
2. **Clique em "New" > "Web Service"**
3. **Conecte seu repositório GitHub**
4. **Configure o serviço**:
   - **Name**: `vivi-ia-agente`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r frontend/requirements.txt`
   - **Start Command**: `python frontend/app_fastapi.py`

### 3. Configurar Variáveis de Ambiente

No painel do Render, vá em **Environment** e adicione:

```
PINECONE_API_KEY=your_pinecone_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
PINECONE_INDEX_NAME=vivi-ia-base
```

### 4. Deploy

1. **Clique em "Deploy"**
2. **Aguarde a conclusão do build** (~5-10 minutos)
3. **Acesse a URL gerada pelo Render**

## 🔧 Configurações Técnicas

### Runtime
- **Python**: 3.11.9
- **Framework**: FastAPI + Uvicorn
- **Dependências**: Ver `frontend/requirements.txt`

### Endpoints
- **Frontend**: `https://your-app.render.com/`
- **Health Check**: `https://your-app.render.com/api/health`
- **API Busca**: `https://your-app.render.com/api/buscar`

### Recursos (Plano Free)
- **512 MB RAM**
- **0.1 CPU**
- **750 horas/mês**

## 🐛 Troubleshooting

### Erro: ModuleNotFoundError
```bash
# Verifique se todas as dependências estão em requirements.txt
pip install -r frontend/requirements.txt
```

### Erro: API Key não encontrada
```bash
# Verifique as variáveis de ambiente no Render
# Todas devem ser configuradas: PINECONE_API_KEY, GOOGLE_API_KEY
```

### Timeout no build
- Verifique se o arquivo `requirements.txt` não tem dependências desnecessárias
- Considere usar `--no-cache-dir` no pip install se necessário

## 📊 Monitoramento

Após o deploy, você pode monitorar:
- **Logs**: No painel do Render
- **Health Check**: Acesse `/api/health`
- **Uptime**: Status do serviço

## 🎯 Próximos Passos

1. **Teste a aplicação** com perguntas reais
2. **Configure domínio customizado** (opcional)
3. **Configure backup** das configurações
4. **Monitore logs** regularmente

## 📞 Suporte

- **Render Docs**: [docs.render.com](https://docs.render.com)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Pinecone Docs**: [docs.pinecone.io](https://docs.pinecone.io)
