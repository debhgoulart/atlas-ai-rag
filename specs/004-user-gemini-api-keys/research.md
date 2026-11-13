# Research & Technical Decisions: Gerenciamento Seguro de Gemini API Keys

**Feature**: `004-user-gemini-api-keys` | **Date**: 2026-11-13

---

## 1. Contexto e Problema Arquitetural

Atualmente, o Atlas AI utiliza uma chave global do Gemini (`GEMINI_API_KEY`) definida no backend via `.env` / Render. Para transformar o Atlas AI em uma plataforma multi-usuário sustentável e com isolamento de custos:
1. Cada usuário autenticado deve prover sua própria Gemini API Key.
2. O sistema nunca deve armazenar chaves em texto puro.
3. O sistema deve validar a chave antes de aceitá-la, criptografá-la de forma simétrica com chave mestra isolada e permitir uso transparente em embeddings e chat.
4. Chaves não devem vazar em logs, respostas HTTP ou inspeção de rede.

---

## 2. Decisões Arquiteturais e Avaliação de Alternativas

### Decisão 1: Autenticação de Usuários e Identidade
- **Situação Atual**: O Atlas AI não possui atualmente modelo de `User`, tabela de usuários ou endpoints de autenticação.
- **Alternativa A (Recomendada)**: Implementar autenticação padrão da indústria com FastAPI:
  - Tabela `users` (`id`, `email`, `hashed_password`, `is_active`, `created_at`, `updated_at`).
  - Hashing seguro com `passlib[bcrypt]` ou `bcrypt`.
  - Autenticação via JWT (`PyJWT` ou `python-jose`) no formato `Authorization: Bearer <token>`.
  - Dependency injection `get_current_user` em FastAPI para proteger rotas e extrair `user_id`.
- **Alternativa B**: Autenticação externa via Supabase/Clerk.
  - *Rejeitada*: Adiciona dependência de serviços externos, complexidade e vai contra o Princípio VI da Constitution (KISS e independência).

### Decisão 2: Algoritmo de Criptografia Simétrica
- **Alternativa A (Recomendada)**: `Fernet` (da biblioteca oficial `cryptography`).
  - Baseado em AES-128-CBC com HMAC-SHA256 para autenticação de integridade (AEAD-equivalent), padding PKCS7 e timestamps para rotação.
  - Chave de 32 bytes base64 (256 bits).
  - Padrão oficial e à prova de falhas em Python.
- **Alternativa B**: `AES-256-GCM` puro (`cryptography.hazmat.primitives.ciphers.aead.AESGCM`).
  - Criptografia autenticada com dados adicionais (AEAD), gera IV/nonce de 96 bits para cada operação e tag de autenticação de 128 bits.
  - Altíssimo desempenho e segurança máxima.
- **Decisão**: Adotar a biblioteca `cryptography` suportando `Fernet` ou `AES-GCM` por meio de um serviço desacoplado `EncryptionService`.

### Decisão 3: Chave Mestra e Variáveis de Ambiente
- Variável dedicada: `CREDENTIALS_ENCRYPTION_KEY`.
- Isolamento: Estritamente separada de `SECRET_KEY` (usada exclusivamente para assinatura de tokens JWT).
- Em desenvolvimento: Gerada via script ou comando `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
- Em produção (Render): Configurada no painel de Environment Variables do backend.

### Decisão 4: Validação da Gemini API Key com Zero Custo
- Para validar se uma chave informada pelo usuário é autêntica e ativa antes de salvar:
  - Inicializar `genai.Client(api_key=candidate_key)`.
  - Executar chamada de metadados: `client.models.get(model=settings.GEMINI_CHAT_MODEL)`.
  - Esta operação é uma requisição HTTP GET de metadados da API do Google Gemini: valida a autenticação da chave imediatamente sem gerar tokens, sem consumir cotas de inferência e sem custos.
  - Se retornar `GoogleAPIError` com status 400/401/403, a chave é considerada inválida (`INVALID_GEMINI_KEY`).

### Decisão 5: Sanitização de Logs e Prevenção de Vazamento
- Criar filtro de logs ou sanitizador que mascare qualquer string no formato padrão de API Keys do Google (`AIzaSy...`).
- O modelo Pydantic de entrada `UserApiKeyInput` nunca deve ser serializado em logs.
- O endpoint de status retorna apenas `key_hint` contendo os 4 últimos caracteres (ex: `"...8xQ2"`).

### Decisão 6: Rotação da Chave Mestra (Estratégia Futura)
- O `EncryptionService` deve ser estruturado com versionamento no cabeçalho do payload criptografado (ex: `v1:<ciphertext>`).
- Um script de rotação de chaves (`app/scripts/rotate_encryption_key.py`) poderá descriptografar com a chave antiga e recriptografar com a chave nova sem interrupção de serviço.
