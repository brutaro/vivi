# 🚀 Vivi IA - Sistema RAG para SIAPE e Gestão Pública

Sistema de Recuperação de Informações baseado em RAG (Retrieval-Augmented Generation) para consultas sobre SIAPE e gestão pública brasileira.

## ✨ Características

- **Agente RAG Inteligente**: Integração com Pinecone para busca semântica
- **IA Avançada**: Utiliza Google Gemini 2.5 Flash para geração de respostas
- **Interface Web**: Frontend moderno com FastAPI
- **Especialização SIAPE**: Foco em legislação e procedimentos administrativos
- **Deploy Automático**: Configurado para Nixpacks (Railway, Render, etc.)

## 🛠️ Tecnologias

- **Backend**: FastAPI + Python 3.11
- **IA**: Google Gemini 2.5 Flash
- **Vector DB**: Pinecone (versão compatível)
- **Frontend**: HTML + CSS + JavaScript
- **Deploy**: Nixpacks

## 🚀 Deploy Rápido

### Render (Recomendado)
1. Fork este repositório
2. Conecte ao Render usando `render.yaml`
3. Configure as variáveis de ambiente
4. Deploy automático!

### Railway
1. Conecte o repositório
2. Configure as variáveis de ambiente
3. Deploy automático com Nixpacks!

### Outros
- **Vercel**: Use `vercel.json`
- **Heroku**: Use `Procfile`
- **Docker**: Use `Dockerfile`

## ⚙️ Configuração Local

1. **Clone o repositório**
```bash
git clone https://github.com/brutaro/vivi.git
cd vivi
```

2. **Instale as dependências**
```bash
# Instale as dependências do frontend
pip install -r frontend/requirements.txt
```

3. **Configure as variáveis de ambiente**
```bash
cp env.example .env
# Edite .env com suas chaves
```

4. **Execute o servidor**
```bash
# Do diretório raiz do projeto
python frontend/app_fastapi.py

# Ou usando uvicorn diretamente
uvicorn frontend.app_fastapi:app --host 0.0.0.0 --port 5001 --reload
```

5. **Acesse**: http://localhost:5001

## 🔑 Variáveis de Ambiente

```bash
PINECONE_API_KEY=sua_chave_api_aqui
PINECONE_INDEX_NAME=vivi-ia-base
GOOGLE_API_KEY=sua_chave_google_aqui
PORT=5001
```

## 📁 Estrutura do Projeto

```
agente-rag2/
├── frontend/                    # Aplicação FastAPI
│   ├── app_fastapi.py          # Servidor principal
│   ├── requirements.txt        # Dependências do frontend
│   ├── templates/
│   │   └── index.html         # Interface web
│   └── static/
│       └── js/
│           └── chat.js         # JavaScript do chat
├── agente_busca_gemini.py      # Agente RAG principal
├── render.yaml                # Configuração Render
├── railway.toml              # Configuração Railway
├── nixpacks.toml             # Configuração Nixpacks
├── runtime.txt               # Versão Python
├── env.example               # Exemplo variáveis ambiente
├── DEPLOY_RENDER.md          # Guia deploy Render
└── README.md                 # Este arquivo
```

## 🔍 Como Funciona

1. **Usuário faz pergunta** via interface web
2. **Sistema busca** no Pinecone por similaridade semântica
3. **Documentos relevantes** são recuperados
4. **Gemini 2.5 Flash** processa e gera resposta
5. **Resposta formatada** é exibida com referências

## 📚 Documentação

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Google AI Documentation](https://ai.google.dev/)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🚀 Deploy Detalhado

### Render (Passo a Passo)

1. **Fork/Clone este repositório**
2. **Acesse [render.com](https://render.com)**
3. **New > Web Service**
4. **Conecte seu repositório GitHub**
5. **Configure**:
   - **Name**: `vivi-ia-agente`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r frontend/requirements.txt`
   - **Start Command**: `python frontend/app_fastapi.py`
6. **Environment Variables**:
   ```
   PINECONE_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   PINECONE_INDEX_NAME=vivi-ia-base
   ```
7. **Deploy!**

📖 **Guia completo**: [GUIA_COMPLETO_DEPLOY_RENDER.md](GUIA_COMPLETO_DEPLOY_RENDER.md)
📖 **Guia rápido**: [DEPLOY_RENDER.md](DEPLOY_RENDER.md)

## 🆘 Suporte

Para suporte, abra uma [issue](https://github.com/brutaro/vivi/issues) no GitHub.

---

**Desenvolvido com ❤️ para a gestão pública brasileira**
