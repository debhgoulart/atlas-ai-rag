#!/usr/bin/env bash
# ==============================================================================
# Atlas AI — Quickstart & Developer Experience (DX) Orchestrator
#
# Automatiza a inicialização da aplicação do zero:
# 1. Configuração interativa da GEMINI_API_KEY no .env
# 2. Inicialização do banco PostgreSQL com extensão pgvector via Docker
# 3. Execução das migrações estruturais via Alembic
# 4. Opção de sanitização (banco zerado)
# 5. Execução concorrente do Backend FastAPI e Frontend Vue 3 com parada limpa
# ==============================================================================

set -e

# Paleta de cores para terminal
CLR_RESET="\033[0m"
CLR_BOLD="\033[1m"
CLR_CYAN="\033[36m"
CLR_GREEN="\033[32m"
CLR_YELLOW="\033[33m"
CLR_RED="\033[31m"
CLR_MAGENTA="\033[35m"

print_header() {
    clear 2>/dev/null || true
    echo -e "${CLR_CYAN}${CLR_BOLD}"
    echo "======================================================================"
    echo "          ATLAS AI — Full Stack RAG & Knowledge Base Chatbot          "
    echo "======================================================================"
    echo -e "${CLR_RESET}"
}

print_header

# ------------------------------------------------------------------------------
# 1. Verificação do arquivo .env e Configuração da Chave Gemini
# ------------------------------------------------------------------------------
echo -e "${CLR_BOLD}[1/5] Verificando variáveis de ambiente...${CLR_RESET}"

if [ ! -f ".env" ]; then
    echo -e "  -> Criando arquivo ${CLR_YELLOW}.env${CLR_RESET} a partir de ${CLR_YELLOW}.env.example${CLR_RESET}..."
    cp .env.example .env
fi

# Carregar valor atual da GEMINI_API_KEY
CURRENT_KEY=$(grep -E "^GEMINI_API_KEY=" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" || true)

if [ -z "$CURRENT_KEY" ] || [ "$CURRENT_KEY" = "your_gemini_api_key_here" ]; then
    echo -e "\n${CLR_YELLOW}┌────────────────────────────────────────────────────────────────────┐${CLR_RESET}"
    echo -e "${CLR_YELLOW}│          COMO OBTER SUA CHAVE DE API GRATUITA DO GEMINI            │${CLR_RESET}"
    echo -e "${CLR_YELLOW}├────────────────────────────────────────────────────────────────────┤${CLR_RESET}"
    echo -e "│ O Atlas AI utiliza os modelos Gemini 2.5 Flash e text-embedding-004│"
    echo -e "│ para o pipeline semântico de RAG e citação de fontes.              │"
    echo -e "│                                                                    │"
    echo -e "│ Passos para gerar sua chave (100% gratuita):                       │"
    echo -e "│  1. Acesse no navegador: ${CLR_CYAN}https://aistudio.google.com/${CLR_RESET}           │"
    echo -e "│  2. Faça login com sua Conta Google.                               │"
    echo -e "│  3. Clique no botão azul ${CLR_BOLD}'Get API key'${CLR_RESET} (Criar chave de API).       │"
    echo -e "│  4. Copie a chave gerada (iniciada por 'AIzaSy...').               │"
    echo -e "${CLR_YELLOW}└────────────────────────────────────────────────────────────────────┘${CLR_RESET}\n"

    read -p "Deseja colar sua GEMINI_API_KEY agora? [S/n]: " WANT_PASTE
    WANT_PASTE=${WANT_PASTE:-S}

    if [[ "$WANT_PASTE" =~ ^[Ss]$ ]]; then
        echo -ne "Cole sua chave da Gemini API: "
        read -r USER_KEY
        USER_KEY=$(echo "$USER_KEY" | xargs) # trim whitespace

        if [ -n "$USER_KEY" ]; then
            # Atualiza no arquivo .env
            if grep -q "^GEMINI_API_KEY=" .env; then
                sed -i "s|^GEMINI_API_KEY=.*|GEMINI_API_KEY=${USER_KEY}|" .env
            else
                echo "GEMINI_API_KEY=${USER_KEY}" >> .env
            fi
            echo -e "${CLR_GREEN}  [✓] GEMINI_API_KEY configurada com sucesso no .env!${CLR_RESET}"
        else
            echo -e "${CLR_YELLOW}  [!] Chave vazia informada. Continuando sem atualizar.${CLR_RESET}"
        fi
    else
        echo -e "${CLR_YELLOW}  [!] Lembre-se de configurar GEMINI_API_KEY no arquivo .env para usar o RAG.${CLR_RESET}"
    fi
else
    echo -e "${CLR_GREEN}  [✓] Chave GEMINI_API_KEY já configurada no .env.${CLR_RESET}"
fi

# ------------------------------------------------------------------------------
# 2. Inicialização do Banco PostgreSQL com pgvector
# ------------------------------------------------------------------------------
echo -e "\n${CLR_BOLD}[2/5] Inicializando PostgreSQL com extensão pgvector...${CLR_RESET}"

if command -v docker >/dev/null 2>&1; then
    echo "  -> Subindo container PostgreSQL (pgvector/pgvector:pg16)..."
    docker compose up -d db

    # Aguardar o banco estar pronto
    echo -n "  -> Aguardando banco de dados aceitar conexões..."
    for i in {1..30}; do
        if docker compose exec -T db pg_isready -U atlas_user -d atlas_ai_db >/dev/null 2>&1; then
            echo -e "${CLR_GREEN} Pronto!${CLR_RESET}"
            break
        fi
        echo -n "."
        sleep 1
    done
else
    echo -e "${CLR_YELLOW}  [!] Docker não encontrado no PATH. Certifique-se de que o Postgres está rodando localmente.${CLR_RESET}"
fi

# ------------------------------------------------------------------------------
# 3. Setup do Backend, Dependências e Migrações Alembic
# ------------------------------------------------------------------------------
echo -e "\n${CLR_BOLD}[3/5] Configurando Backend e Migrações de Banco...${CLR_RESET}"

cd backend
if [ ! -d ".venv" ]; then
    echo "  -> Criando ambiente virtual Python (.venv)..."
    python3 -m venv .venv
fi

PYTHON_BIN=".venv/bin/python"
PIP_BIN=".venv/bin/pip"
ALEMBIC_BIN=".venv/bin/alembic"

if [ ! -f ".venv/installed.flag" ]; then
    echo "  -> Instalando dependências do backend..."
    $PIP_BIN install -q -r requirements.txt
    touch .venv/installed.flag
fi

echo "  -> Aplicando migrações do banco (Alembic)..."
$ALEMBIC_BIN upgrade head

# Pergunta opcional para deixar o banco 100% zerado
echo -e ""
read -p "Deseja sanitizar a base de dados agora (deixar zerada/sem registros)? [s/N]: " WANT_RESET
WANT_RESET=${WANT_RESET:-N}
if [[ "$WANT_RESET" =~ ^[Ss]$ ]]; then
    $PYTHON_BIN -m app.scripts.reset_db
fi

cd ..

# ------------------------------------------------------------------------------
# 4. Setup do Frontend
# ------------------------------------------------------------------------------
echo -e "\n${CLR_BOLD}[4/5] Verificando dependências do Frontend (Vue 3 + Vite)...${CLR_RESET}"

cd frontend
if [ ! -d "node_modules" ]; then
    echo "  -> Instalando pacotes npm..."
    npm install --silent
else
    echo -e "${CLR_GREEN}  [✓] node_modules do frontend presente.${CLR_RESET}"
fi
cd ..

# ------------------------------------------------------------------------------
# 5. Execução dos Servidores Locais com Encerramento Gracioso
# ------------------------------------------------------------------------------
echo -e "\n${CLR_BOLD}[5/5] Iniciando servidores do Atlas AI...${CLR_RESET}"

# Handler para captura de Ctrl+C e desligamento limpo
cleanup() {
    echo -e "\n\n${CLR_YELLOW}Encerrando Atlas AI...${CLR_RESET}"
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    echo -e "${CLR_GREEN}Servidores finalizados com sucesso. Até logo!${CLR_RESET}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar Backend em segundo plano
cd backend
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /dev/null 2>&1 &
BACKEND_PID=$!
cd ..

# Iniciar Frontend em segundo plano
cd frontend
./node_modules/.bin/vite --port 5173 --host > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 2

echo -e "\n${CLR_GREEN}${CLR_BOLD}======================================================================"
echo "          🚀 ATLAS AI ESTÁ EM EXECUÇÃO COM SUCESSO!                    "
echo "======================================================================${CLR_RESET}"
echo -e "  ${CLR_CYAN}➜ Frontend Web (UI):${CLR_RESET}   ${CLR_BOLD}http://localhost:5173${CLR_RESET}"
echo -e "  ${CLR_CYAN}➜ Backend API (Swagger):${CLR_RESET} http://localhost:8000/docs"
echo -e "  ${CLR_CYAN}➜ Health Check:${CLR_RESET}          http://localhost:8000/api/v1/health"
echo -e "  ${CLR_CYAN}➜ Banco de Dados:${CLR_RESET}        localhost:5432 (pgvector)"
echo -e "${CLR_GREEN}======================================================================${CLR_RESET}"
echo -e "${CLR_YELLOW}Pressione [Ctrl + C] para parar todos os servidores a qualquer momento.${CLR_RESET}\n"

# Manter o script ativo aguardando os processos filhos
wait $BACKEND_PID $FRONTEND_PID
