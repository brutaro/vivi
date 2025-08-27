// Inicializar markdown-it
const md = window.markdownit({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true
});

// Elementos do DOM
const perguntaInput = document.getElementById('pergunta-input');
const enviarBtn = document.getElementById('enviar-btn');
const loading = document.getElementById('loading');
const resultados = document.getElementById('resultados');
const respostaCompleta = document.getElementById('resposta-completa');
const erro = document.getElementById('erro');
const erroMensagem = document.getElementById('erro-mensagem');
const btnCopiar = document.getElementById('btn-copiar');
const btnDownload = document.getElementById('btn-download');
const btnNovaConsulta = document.getElementById('btn-nova-consulta');
const btnLimpar = document.getElementById('btn-limpar');
const btnTentarNovamente = document.getElementById('btn-tentar-novamente');

// Variáveis de estado
let ultimaResposta = '';
let perguntaAtual = '';

// Função para mostrar loading
function mostrarLoading() {
    loading.classList.remove('hidden');
}

// Função para esconder loading
function esconderLoading() {
    loading.classList.add('hidden');
}

// Função para mostrar resultados
function mostrarResultados() {
    resultados.classList.remove('hidden');
}

// Função para esconder resultados
function esconderResultados() {
    resultados.classList.add('hidden');
}

// Função para mostrar erro
function mostrarErro(mensagem) {
    erroMensagem.textContent = mensagem;
    erro.classList.remove('hidden');
}

// Função para esconder erro
function esconderErro() {
    erro.classList.add('hidden');
}

// Função para copiar resposta
async function copiarResposta() {
    if (!ultimaResposta) return;
    
    try {
        await navigator.clipboard.writeText(ultimaResposta);
        
        // Feedback visual
        const originalText = btnCopiar.innerHTML;
        btnCopiar.innerHTML = '<i class="fas fa-check"></i> Copiado!';
        btnCopiar.classList.remove('btn-secondary');
        btnCopiar.classList.add('btn-primary');
        
        setTimeout(() => {
            btnCopiar.innerHTML = originalText;
            btnCopiar.classList.remove('btn-primary');
            btnCopiar.classList.add('btn-secondary');
        }, 2000);
        
    } catch (error) {
        console.error('Erro ao copiar:', error);
        alert('Erro ao copiar para a área de transferência');
    }
}

// Função para download da resposta
function downloadResposta() {
    if (!ultimaResposta || !perguntaAtual) return;
    
    try {
        // Criar nome do arquivo baseado na pergunta
        const nomeArquivo = `resposta_vivi_${new Date().toISOString().slice(0, 10)}.txt`;
        
        // Criar conteúdo do arquivo
        const conteudo = `PERGUNTA: ${perguntaAtual}\n\nRESPOSTA:\n${ultimaResposta}\n\n---\nVivi IA - Assistente em SIAPE e Gestão Pública\nData: ${new Date().toLocaleString('pt-BR')}`;
        
        // Criar blob e download
        const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = nomeArquivo;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Feedback visual
        const originalText = btnDownload.innerHTML;
        btnDownload.innerHTML = '<i class="fas fa-check"></i> Baixado!';
        
        setTimeout(() => {
            btnDownload.innerHTML = originalText;
        }, 2000);
        
    } catch (error) {
        console.error('Erro ao fazer download:', error);
        alert('Erro ao fazer download do arquivo');
    }
}

// Função para nova consulta
function novaConsulta() {
    // Limpar input
    perguntaInput.value = '';
    
    // Esconder resultados e erro
    esconderResultados();
    esconderErro();
    
    // Focar no input
    perguntaInput.focus();
}

// Função para limpar chat
function limparChat() {
    // Limpar input
    perguntaInput.value = '';
    
    // Esconder resultados e erro
    esconderResultados();
    esconderErro();
    
    // Focar no input
    perguntaInput.focus();
}

// Função para processar resposta da API
async function processarResposta(resposta) {
    try {
        if (resposta.success) {
            ultimaResposta = resposta.resposta;
            perguntaAtual = perguntaInput.value;
            
            // Renderizar resposta com markdown
            respostaCompleta.innerHTML = md.render(resposta.resposta);
            
            // Mostrar resultados
            mostrarResultados();
        } else {
            mostrarErro(resposta.error || 'Erro desconhecido');
        }
    } catch (error) {
        console.error('Erro ao processar resposta:', error);
        mostrarErro('Erro interno ao processar resposta');
    }
}

// Função para fazer busca
async function fazerBusca(pergunta) {
    try {
        const response = await fetch('/api/buscar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ pergunta: pergunta })
        });

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Erro na requisição:', error);
        return { success: false, error: 'Erro de conexão' };
    }
}

// Função para enviar pergunta
async function enviarPergunta() {
    const pergunta = perguntaInput.value.trim();
    
    if (!pergunta) {
        return;
    }

    // Esconder resultados e erro anteriores
    esconderResultados();
    esconderErro();
    
    // Mostrar loading
    mostrarLoading();
    
    try {
        // Fazer busca
        const resposta = await fazerBusca(pergunta);
        
        // Esconder loading
        esconderLoading();
        
        // Processar resposta
        await processarResposta(resposta);
        
    } catch (error) {
        console.error('Erro:', error);
        esconderLoading();
        mostrarErro('Erro interno do sistema');
    }
}

// Event listeners
enviarBtn.addEventListener('click', enviarPergunta);

perguntaInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        enviarPergunta();
    }
});

// Event listeners para botões de ação
btnCopiar.addEventListener('click', copiarResposta);
btnDownload.addEventListener('click', downloadResposta);
btnNovaConsulta.addEventListener('click', novaConsulta);
btnLimpar.addEventListener('click', limparChat);
btnTentarNovamente.addEventListener('click', enviarPergunta);

// Focar no input ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    perguntaInput.focus();
});
