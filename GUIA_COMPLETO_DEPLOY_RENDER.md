# 🚀 GUIA COMPLETO: Deploy da Vivi IA no Render

## 📋 SOBRE ESTE GUIA

Este guia fornece instruções completas para fazer deploy da **Vivi IA** - Sistema RAG para SIAPE e gestão pública - no Render. A Vivi IA é uma assistente inteligente especializada em legislação e procedimentos administrativos brasileiros.

---

## 📋 PRÉ-REQUISITOS

### ✅ Conta e Acesso
- **Conta no Render**: [render.com](https://render.com)
- **Repositório GitHub**: Público ou privado com acesso ao Render
- **Chaves de API**:
  - `PINECONE_API_KEY` (Banco vetorial)
  - `GOOGLE_API_KEY` (Gemini AI)
  - `PINECONE_INDEX_NAME` (Índice configurado)

### ✅ Conhecimentos Necessários
- Noções básicas de Git
- Conhecimento de Python
- Familiaridade com APIs REST

---

## 🏗️ ESTRUTURA DO PROJETO

```
agente-rag2/
├── .gitignore                 # Arquivos ignorados
├── README.md                  # Documentação principal
├── DEPLOY_RENDER.md           # Guia específico do Render
├── render.yaml               # Configuração do Render
├── runtime.txt               # Versão Python
├── env.example               # Exemplo variáveis ambiente
├── agente_busca_gemini.py    # Core do agente RAG
├── frontend/                  # Aplicação FastAPI
│   ├── app_fastapi.py       # Servidor principal
│   ├── requirements.txt     # Dependências
│   ├── templates/
│   │   └── index.html      # Interface web
│   └── static/
│       └── js/
│           └── chat.js     # JavaScript do chat
└── test_render_deployment.py # Script de testes
```

---

## 🚀 PASSO 1: PREPARAÇÃO DO AMBIENTE

### 1.1 Clonar e Configurar o Repositório

```bash
# 1. Criar diretório limpo (recomendado)
mkdir vivi-deploy && cd vivi-deploy

# 2. Clonar o repositório oficial
git clone https://github.com/brutaro/vivi.git
cd vivi

# 3. Verificar estrutura
ls -la
```

### 1.2 Configurar Variáveis de Ambiente

```bash
# 1. Copiar arquivo de exemplo
cp env.example .env

# 2. Editar com suas chaves
nano .env
```

**Conteúdo do arquivo `.env`:**
```bash
# Configurações do Pinecone
PINECONE_API_KEY=sua_chave_pinecone_aqui
PINECONE_INDEX_NAME=vivi-ia-base

# Configurações do Google AI
GOOGLE_API_KEY=sua_chave_google_aqui

# Configurações do servidor
PORT=5001
```

### 1.3 Teste Local (Opcional mas Recomendado)

```bash
# 1. Instalar dependências
pip install -r frontend/requirements.txt

# 2. Executar testes
python test_render_deployment.py

# 3. Se tudo OK, testar servidor
python frontend/app_fastapi.py

# 4. Acessar http://localhost:5001
```

---

## 📦 PASSO 2: CONFIGURAÇÃO DO GITHUB

### 2.1 Preparar o Repositório

```bash
# 1. Verificar status
git status

# 2. Adicionar mudanças
git add .

# 3. Commit das configurações
git commit -m "Configuração completa para deploy no Render"

# 4. Push para GitHub
git push origin main
```

### 2.2 Verificar Arquivos Essenciais

Certifique-se de que estes arquivos estão presentes:

```bash
✅ render.yaml (configuração Render)
✅ runtime.txt (versão Python)
✅ frontend/requirements.txt (dependências)
✅ frontend/app_fastapi.py (aplicação)
✅ agente_busca_gemini.py (agente)
✅ .gitignore (arquivos ignorados)
```

---

## 🌐 PASSO 3: DEPLOY NO RENDER

### 3.1 Criar Novo Serviço

1. **Acesse [render.com](https://render.com)**
2. **Clique em "New" > "Web Service"**
3. **Conecte seu repositório GitHub**
   - Selecione `brutaro/vivi`
   - Escolha branch `main`

### 3.2 Configurar Build Settings

```
Name: vivi-ia-agente
Environment: Python
Build Command: pip install -r frontend/requirements.txt
Start Command: python frontend/app_fastapi.py
```

### 3.3 Configurar Environment Variables

Na seção **Environment**, adicione:

```
PINECONE_API_KEY = sua_chave_aqui
GOOGLE_API_KEY = sua_chave_aqui
PINECONE_INDEX_NAME = vivi-ia-base
PYTHON_VERSION = 3.11.0
```

### 3.4 Configurações Avançadas (Opcional)

```yaml
# Instance Type: Free (512 MB RAM)
# Region: São Paulo (ou mais próximo)
# Auto-Deploy: Yes (recomendado)
```

### 3.5 Deploy

1. **Clique em "Create Web Service"**
2. **Aguarde o build** (~5-10 minutos)
3. **Anote a URL gerada**

---

## 🔍 PASSO 4: VALIDAÇÃO E TESTES

### 4.1 Verificar Status do Deploy

```bash
# 1. Health Check
curl https://SEU_APP.render.com/api/health

# 2. Diagnóstico completo
curl https://SEU_APP.render.com/api/diagnostics
```

**Resposta esperada do Health Check:**
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "checks": {
    "agent_initialization": "✅ OK",
    "pinecone_connection": "✅ OK"
  }
}
```

### 4.2 Testar Funcionalidades

**Acesse:** `https://SEU_APP.render.com`

**Testes recomendados:**
1. **Primeira pesquisa** - Deve funcionar imediatamente
2. **Múltiplas perguntas** - Testar catchphrases aleatórias
3. **Perguntas específicas** - Validar conhecimento dos documentos

### 4.3 Testar Endpoints da API

```bash
# 1. Busca
curl -X POST https://SEU_APP.render.com/api/buscar \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Como funciona o SIAPE?"}'

# 2. Health Check
curl https://SEU_APP.render.com/api/health

# 3. Diagnóstico
curl https://SEU_APP.render.com/api/diagnostics
```

---

## 📊 PASSO 5: MONITORAMENTO

### 5.1 Logs do Render

1. **Acesse o painel do Render**
2. **Seção "Logs"** do seu serviço
3. **Monitorar:**
   - Inicialização do agente
   - Conectividade com Pinecone
   - Erros de busca
   - Performance das respostas

### 5.2 Métricas de Performance

```bash
# Monitorar resposta média
curl -w "@curl-format.txt" -o /dev/null -s https://SEU_APP.render.com/api/health
```

### 5.3 Alertas (Opcional)

- Configure alertas para falhas de build
- Configure alertas para tempo de resposta alto
- Monitore uso de recursos (RAM/CPU)

---

## 🔧 PASSO 6: MANUTENÇÃO E ATUALIZAÇÕES

### 6.1 Atualizar Código

```bash
# 1. Fazer mudanças localmente
# 2. Testar localmente
python test_render_deployment.py

# 3. Commit e push
git add .
git commit -m "Atualização: [descrição]"
git push origin main

# 4. Render fará deploy automático
```

### 6.2 Atualizar Dependências

```bash
# 1. Atualizar requirements.txt
nano frontend/requirements.txt

# 2. Testar localmente
pip install -r frontend/requirements.txt
python test_render_deployment.py

# 3. Commit e deploy
git add frontend/requirements.txt
git commit -m "Atualização de dependências"
git push origin main
```

### 6.3 Backup de Configurações

```bash
# Fazer backup das variáveis de ambiente
cp .env .env.backup
```

---

## 🚨 PASSO 7: TROUBLESHOOTING

### 7.1 Problemas Comuns

#### ❌ Erro: "ModuleNotFoundError"
```bash
# Verificar requirements.txt
cat frontend/requirements.txt

# Verificar instalação
pip install -r frontend/requirements.txt
```

#### ❌ Erro: "Agente não inicializado"
```bash
# Verificar variáveis de ambiente
curl https://SEU_APP.render.com/api/diagnostics

# Verificar logs do Render
# - Ir ao painel > Logs
# - Procurar por erros de inicialização
```

#### ❌ Erro: "Pinecone connection failed"
```bash
# Verificar chave da API
# - Ir ao painel Render > Environment
# - Verificar PINECONE_API_KEY
# - Verificar PINECONE_INDEX_NAME
```

#### ❌ Erro: "Build timeout"
- Verificar se requirements.txt não tem dependências desnecessárias
- Considerar usar `--no-cache-dir` no pip install

### 7.2 Debug Avançado

#### Verificar Logs em Tempo Real
```bash
# No painel Render > Logs
# Filtrar por nível: ERROR, WARN, INFO
```

#### Testar Conectividade
```bash
# Testar Pinecone
curl -X POST https://SEU_APP.render.com/api/buscar \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "teste"}'
```

### 7.3 Suporte

- **Render Docs**: [docs.render.com](https://docs.render.com)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Pinecone Docs**: [docs.pinecone.io](https://docs.pinecone.io)

---

## 🎯 PASSO 8: OTIMIZAÇÕES AVANÇADAS

### 8.1 Performance

```yaml
# render.yaml otimizado
services:
  - type: web
    name: vivi-ia-agente
    env: python
    plan: starter  # Upgrade para mais recursos
    buildCommand: pip install -r frontend/requirements.txt --no-cache-dir
    startCommand: python frontend/app_fastapi.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PINECONE_API_KEY
        sync: false
      - key: GOOGLE_API_KEY
        sync: false
      - key: WEB_CONCURRENCY
        value: 2
```

### 8.2 Cache e CDN

- Configurar Cloudflare para cache de assets estáticos
- Usar Redis para cache de respostas (futuro)

### 8.3 Monitoramento Avançado

- Integrar com DataDog ou New Relic
- Configurar alertas customizados
- Monitorar latência de resposta

---

## 📚 RECURSOS ADICIONAIS

### Documentação da Vivi IA
- [README.md](README.md) - Visão geral
- [DEPLOY_RENDER.md](DEPLOY_RENDER.md) - Deploy específico
- [test_render_deployment.py](test_render_deployment.py) - Script de testes

### Endpoints da API
- `GET /` - Interface web
- `POST /api/buscar` - Busca RAG
- `GET /api/health` - Status do sistema
- `GET /api/diagnostics` - Diagnóstico detalhado

### Configurações do Agente
- **Modelo**: Gemini 2.5 Flash
- **Embeddings**: Pinecone com Llama
- **Contexto**: Até 5 documentos por resposta
- **Personalidade**: Vivi IA especialista em SIAPE

---

## 🎉 CHECKLIST FINAL

### ✅ Antes do Deploy
- [ ] Repositório limpo e atualizado
- [ ] Todas as dependências em requirements.txt
- [ ] Variáveis de ambiente configuradas
- [ ] Teste local passou
- [ ] Arquivos essenciais presentes

### ✅ Durante o Deploy
- [ ] Build completou sem erros
- [ ] Agente inicializou corretamente
- [ ] Health check retorna "healthy"
- [ ] Interface web carregou

### ✅ Após o Deploy
- [ ] Primeira pesquisa funciona
- [ ] Respostas têm personalidade da Vivi IA
- [ ] Referências são citadas
- [ ] Logs estão limpos

---

## 🚀 CONCLUSÃO

Seguindo este guia, você terá uma **Vivi IA completamente funcional** no Render, capaz de:

- ✅ **Responder perguntas** sobre SIAPE e gestão pública
- ✅ **Buscar informações** relevantes nos documentos
- ✅ **Manter personalidade** profissional e direta
- ✅ **Funcionar 24/7** com mínimo de manutenção

### 🎯 Próximos Passos Recomendados

1. **Teste exaustivo** com perguntas variadas
2. **Configure monitoramento** contínuo
3. **Documente customizações** específicas do seu uso
4. **Planeje escalabilidade** conforme demanda cresce

**🚀 Sua Vivi IA está pronta para uso em produção!**

---

**📞 Suporte:** Para dúvidas específicas, consulte os logs do Render ou abra uma issue no repositório.

**💡 Dica:** Mantenha este guia atualizado conforme fizer modificações no sistema.
