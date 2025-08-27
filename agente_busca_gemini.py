#!/usr/bin/env python3
"""
Agente de Busca com Gemini 2.5 Flash como Redator
Fluxo: Pergunta → Pinecone → Documentos → Gemini → Resposta Formal + Referências
Integrado com a persona da Vivi IA - Especialista em SIAPE e Gestão Pública
"""

import os
import google.generativeai as genai
from pinecone import Pinecone
import json
import random

class AgenteBuscaGemini:
    def __init__(self):
        """Inicializa o agente"""
        # Configurar Pinecone (versão 7.3.0)
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(os.getenv("PINECONE_INDEX", "vivi-ia-base"))
        
        # Configurar Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Catchphrases da Vivi IA
        self.catchphrases = {
            "abertura": [
                "Vamos ao que interessa...",
                "Analisando os dados enviados...",
                "Olha só o que temos aqui...",
                "Vamos conferir se está nos conformes..."
            ],
            "positivo": [
                "Procedimento correto. Seguindo em frente.",
                "Tudo nos conformes, sem ressalvas.",
                "Aqui temos um exemplo de boa gestão documental."
            ],
            "negativo": [
                "Temos um problema aqui...",
                "Isso não bate com as normativas. Vamos corrigir.",
                "Estamos diante de um caso que precisa de ajustes."
            ]
        }
        
        print("🤖 Agente de Busca Vivi IA com Gemini 2.5 Flash inicializado!")

    def gerar_embedding(self, texto):
        """Gera embedding usando modelo integrado do Pinecone (llama-text-embed-v2)"""
        try:
            # Usar o modelo integrado do Pinecone que gera 1024 dimensões
            response = self.pc.inference.embed(
                model="llama-text-embed-v2",
                inputs=[texto],
                parameters={"input_type": "passage"}
            )
            return response.data[0]['values']
        except Exception as e:
            print(f"❌ Erro ao gerar embedding: {e}")
            return None

    def buscar_no_pinecone(self, pergunta, top_k=10):
        """Busca semântica no Pinecone"""
        print(f"🔍 Buscando no Pinecone: '{pergunta}'")

        try:
            # Gerar embedding usando modelo integrado do Pinecone
            embedding = self.gerar_embedding(pergunta)
            if embedding is None:
                print("❌ Erro ao gerar embedding")
                return []

            # Buscar usando query no namespace vazio (onde estão os dados)
            results = self.index.query(
                namespace="",
                vector=embedding,
                top_k=top_k,
                include_metadata=True
            )

            if hasattr(results, 'matches') and results.matches:
                matches = results.matches
                print(f"✅ {len(matches)} documentos encontrados")
                return matches
            else:
                print("⚠️ Nenhum resultado encontrado")
                return []

        except Exception as e:
            print(f"❌ Erro na busca Pinecone: {e}")
            return []
    
    def limpar_e_corrigir_texto(self, texto):
        """Limpa e corrige automaticamente erros de texto"""
        # Correções obrigatórias
        correcoes = {
            'escontado': 'descontado',
            'ESCONTADO': 'DESCONTADO',
            'chunk': 'documento',
            'chunks': 'documentos',
            'Chunk': 'Documento',
            'Chunks': 'Documentos',
            'Abate do Teto Constitucional': 'Abate Teto Constitucional',
            'ABATE DO TETO CONSTITUCIONAL': 'ABATE TETO CONSTITUCIONAL',
            'Ministério da Economia': 'Ministério da Gestão e Inovação em Serviços Públicos (MGI)',
            'MINISTÉRIO DA ECONOMIA': 'MINISTÉRIO DA GESTÃO E INOVAÇÃO EM SERVIÇOS PÚBLICOS (MGI)',
            'Ministério da Infraestrutura': 'Ministério do Trabalho (MT)',
            'MINISTÉRIO DA INFRAESTRUTURA': 'MINISTÉRIO DO TRABALHO (MT)'
        }

        texto_limpo = texto
        for erro, correcao in correcoes.items():
            texto_limpo = texto_limpo.replace(erro, correcao)

        return texto_limpo

    def preparar_contexto_para_gemini(self, documentos):
        """Prepara o contexto dos documentos para o Gemini"""
        contexto = []

        for i, doc in enumerate(documentos):
            if hasattr(doc, 'metadata') and doc.metadata:
                metadata = doc.metadata
                # Na versão 7.3.0, o conteúdo pode estar em diferentes campos
                conteudo = metadata.get('text', '') or metadata.get('content', '') or metadata.get('chunk_text', '')
                document_title = metadata.get('document_title', metadata.get('source', f'Documento {i+1}'))

                if conteudo:
                    # Limpar texto (remover caracteres especiais)
                    chunk_clean = conteudo.replace('\uf0c9', '').replace('\uf002', '').replace('\uf142', '')
                    chunk_clean = ' '.join(chunk_clean.split())  # Normalizar espaços

                    # Aplicar correções automáticas
                    chunk_clean = self.limpar_e_corrigir_texto(chunk_clean)

                    contexto.append({
                        "documento_id": doc.id if hasattr(doc, 'id') else f'doc_{i}',
                        "document_title": document_title,
                        "relevancia": f"{doc.score:.2%}" if hasattr(doc, 'score') else "N/A",
                        "conteudo": chunk_clean[:5000] + "..." if len(chunk_clean) > 5000 else chunk_clean
                    })

        return contexto

    def processar_com_gemini(self, pergunta, documentos):
        """Processa a pergunta e documentos com Gemini usando persona da Vivi IA"""
        print("🤖 Gerando resposta com Gemini 2.5 Flash (Vivi IA)...")

        if not documentos:
            return "❌ Nenhum resultado encontrado no banco de dados."

        # Preparar contexto
        contexto = self.preparar_contexto_para_gemini(documentos)

        # Selecionar catchphrase aleatória
        catchphrase = random.choice(self.catchphrases["abertura"])

        # Prompt da Vivi IA - VERSÃO REFORÇADA
        prompt = f"""
VOCÊ É VIVI IA. A PARTIR DE AGORA, VOCÊ É ELA COMPLETAMENTE.

INSTRUÇÕES DE PERSONALIDADE (OBRIGATÓRIAS):
- VOCÊ SEMPRE fala na primeira pessoa como "eu" (Vivi)
- SUA primeira frase DEVE SER EXATAMENTE a catchphrase fornecida: "{catchphrase}"
- VOCÊ é DIRETA, EFICIENTE, COMPETENTE e PROFISSIONAL
- VOCÊ é INTOLERANTE com preguiça e falta de esforço
- VOCÊ é CORDIAL mas FIRME quando necessário
- VOCÊ é especialista em gestão pública e SIAPE

EXEMPLO DE ABERTURA:
"{catchphrase}"

Agora responda à pergunta mantendo esta personalidade.

PERGUNTA DO USUÁRIO:
{pergunta}

CONTEXTO DISPONÍVEL (documentos do documento):
{json.dumps(contexto, indent=2, ensure_ascii=False)}

INSTRUÇÕES DE RESPOSTA:
1. COMECE SUA RESPOSTA com EXATAMENTE esta frase: "{catchphrase}"
2. RESPONDA NA PRIMEIRA PESSOA como Vivi IA
3. Seja DIRETA e OBJETIVA, mas PROFISSIONAL
4. Use linguagem FORMAL e TÉCNICA quando necessário
5. NÃO cite referências inline (documento_id) ao longo do texto
6. Se não houver informação suficiente, diga claramente
7. NÃO invente informações que não estejam no contexto
8. Estruture a resposta para facilitar a compreensão
9. Use CAPSLOCK para ÊNFASE em normativas relevantes
10. Seja ASSERTIVA e OBJETIVA

PERSONALIDADE VIVI IA:
- Competente, Direta, Eficiente, Cordial, Justa, Inteligente
- Impaciente com a falta de esforço
- Tom profissional e objetivo, sem ser rude
- Respeito sempre, mas sem tolerar desorganização

IMPORTANTE SOBRE CONCLUSÃO:
- ANTES das referências, SEMPRE faça uma conclusão sucinta
- A conclusão deve ser na primeira pessoa como Vivi IA
- Deve reforçar a importância da informação ou orientar sobre próximos passos
- Deve ser breve (2-3 frases) e manter o tom profissional mas pessoal da Vivi IA
- Exemplos: "Espero que estas informações sejam úteis para sua gestão.", "Fique atento às normativas específicas do seu caso.", "Esta é uma questão que merece atenção especial."

IMPORTANTE SOBRE REFERÊNCIAS:
- NÃO use referências inline como "documento_id: abate_teto#5"
- Após a conclusão, adicione uma seção "Referências:"
- Use APENAS os metadados document_title dos documentos que você realmente utilizou para construir a resposta
- NÃO invente títulos de documentos - use APENAMENTE os títulos reais dos metadados
- IMPORTANTE: Sempre cite TODAS as referências consultadas, tanto o documento principal quanto todos os documentos complementares que foram utilizados para enriquecer a resposta
- SEMPRE liste TODOS os documentos complementares que foram utilizados para enriquecer a resposta, mesmo que não sejam o documento principal consultado

IMPORTANTE SOBRE LISTAS E INFORMAÇÕES COMPLETAS:
- Quando a pergunta solicitar uma lista (bancos, órgãos, processos, etc.), forneça TODOS os itens disponíveis no contexto
- NÃO use expressões como "alguns dos", "entre outros", "dentre os quais" - seja COMPLETO
- Liste TODOS os itens encontrados, organizando-os de forma clara e legível
- Se houver muitos itens, use formatação adequada (tópicos, tabelas, etc.)
- EXEMPLO: ❌ "Alguns bancos: Banco A, Banco B, entre outros" | ✅ "Bancos credenciados: Banco A, Banco B, Banco C, Banco D"

INSTRUÇÕES ESPECÍFICAS PARA LISTAS ESTRUTURADAS:
- Para listas com metadados estruturados (bancos, órgãos, processos, etc.), SEMPRE inclua TODAS as informações disponíveis
- NÃO omita nenhuma informação - se estiver no contexto, deve aparecer na resposta
- Se uma informação não estiver disponível, indique claramente "Não especificado" ou "Não disponível"
- Organize a lista de forma sistemática e consistente para todos os itens
- Use formatação padronizada (símbolos, espaçamento, estrutura)
- EXEMPLOS CORRETOS:
  • Bancos: "001 - BANCO DO BRASIL S.A. ○ Ponto Focal: Nome Completo ○ E-mail: email@banco.com ○ Telefone: (XX) XXXX-XXXX"
  • Órgãos: "ÓRGÃO A - Nome do Órgão ○ Responsável: Nome ○ Departamento: Setor ○ Contato: email@orgao.gov.br"
  • Processos: "PROCESSO 001 - Descrição ○ Prazo: X dias ○ Responsável: Nome ○ Status: Em andamento"

CORREÇÕES OBRIGATÓRIAS DE PALAVRAS:
- SEMPRE substitua "chunks" por "documentos"
- SEMPRE substitua "escontado" por "descontado"
- SEMPRE substitua "chunk_id" por "documento_id"
- SEMPRE substitua "chunk" por "documento"
- SEMPRE substitua "chunks" por "documentos"
- SEMPRE substitua "chunk_text" por "conteúdo do documento"
- SEMPRE substitua "chunk_index" por "índice do documento"
- SEMPRE substitua "chunk_size" por "tamanho do documento"
- SEMPRE substitua "Abate do Teto Constitucional" por "Abate Teto Constitucional"
- SEMPRE substitua "Ministério da Economia" por "Ministério da Gestão e Inovação em Serviços Públicos (MGI)"
- SEMPRE substitua "Ministério da Infraestrutura" por "Ministério do Trabalho (MT)"

EXEMPLOS DE CORREÇÃO:
❌ INCORRETO: "os chunks encontrados", "escontado no contracheque", "Abate do Teto Constitucional", "Ministério da Economia"
✅ CORRETO: "os documentos encontrados", "descontado no contracheque", "Abate Teto Constitucional", "Ministério da Gestão e Inovação em Serviços Públicos (MGI)"

IMPORTANTE: SUA RESPOSTA DEVE começar EXATAMENTE com: "{catchphrase}"

AGORA RESPONDA COMO VIVI IA:
"""

        try:
            response = self.model.generate_content(prompt)
            resposta = response.text

            # Mostrar documentos encontrados (debug)
            print(f"\n📚 DOCUMENTOS ENCONTRADOS:")
            for i, ctx in enumerate(contexto):
                print(f"\n--- Documento {i+1} ---")
                print(f"ID: {ctx['documento_id']}")
                print(f"Título: {ctx['document_title']}")
                print(f"Relevância: {ctx['relevancia']}")
                print(f"Conteúdo (CORRIGIDO): {ctx['conteudo'][:150]}...")

            return resposta

        except Exception as e:
            print(f"❌ Erro no Gemini: {e}")
            return f"Erro ao processar com IA: {str(e)}"
    
    def executar_busca_completa(self, pergunta):
        """Executa a busca completa"""
        print(f"\n🎯 EXECUTANDO BUSCA COMPLETA - VIVI IA")
        print(f"📝 Pergunta: {pergunta}")
        print("=" * 60)
        
        # 1. Buscar no Pinecone
        documentos = self.buscar_no_pinecone(pergunta)
        
        # 2. Processar com Gemini
        resposta = self.processar_com_gemini(pergunta, documentos)
        
        print("✅ Busca completa finalizada!")
        return resposta

if __name__ == "__main__":
    # Teste simples
    agente = AgenteBuscaGemini()
    resposta = agente.executar_busca_completa("Como funciona o SIAPE?")
    print(resposta)
