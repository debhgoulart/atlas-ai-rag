# ADR 0003: Criptografia Simétrica de Credenciais e Isolamento de Chaves por Usuário

- **Status**: Aprovado
- **Data**: 2026-11-13
- **Autores**: Atlas AI Team
- **Contexto Técnico / Escopo**: Backend / Segurança / Gestão de Credenciais / Multi-tenancy

---

## 1. Contexto e Declaração do Problema
O Atlas AI originalmente utilizava uma única chave de API global (`GEMINI_API_KEY`) compartilhada entre todas as operações e usuários. Esse modelo apresenta três limitações críticas:
1. **Falta de Isolamento de Custos e Cotas**: O proprietário da aplicação arca com todo o volume de inferência e corre risco de esgotamento de taxa (rate limits) por uso concorrente.
2. **Ausência de Autonomia do Usuário**: Cada usuário deve ter controle sobre suas cotas e modelos sem compartilhar credenciais ou expor segredos para terceiros.
3. **Risco de Segurança e Vazamento de Dados**: API Keys armazenadas em texto puro em banco de dados ou variáveis de ambiente globais são alvos frequentes de exfiltração.

## 2. Decisão Arquitetural
Adotamos:
1. **Autenticação Baseada em Usuário (`User`) com JWT**:
   Introdução do modelo `User` e tokens JWT Bearer (`HS256`), permitindo associar cada sessão HTTP a uma identidade autenticada (`user_id`).
2. **Criptografia Simétrica com Fernet (AES-128-CBC + HMAC-SHA256)**:
   Todas as chaves informadas pelos usuários são cifradas antes da gravação no PostgreSQL na tabela `user_gemini_credentials`. O algoritmo Fernet garante confidencialidade com AES e integridade autenticada com HMAC, impedindo qualquer modificação no payload cifrado.
3. **Segregação Estrita de Chaves Mestras**:
   A chave mestra de criptografia (`CREDENTIALS_ENCRYPTION_KEY`) é armazenada exclusivamente nas variáveis de ambiente do backend no Render. Ela é rigorosamente separada da `SECRET_KEY` usada para assinatura de tokens de autenticação.
4. **Validação Custo-Zero antes da Persistência**:
   Antes de criptografar e salvar, o backend valida a autenticidade da chave informada consultando metadados via `genai.Client.models.get(model=settings.GEMINI_CHAT_MODEL)`. Essa requisição não consome tokens nem custos de inferência.
5. **Máscara e Redação de Logs**:
   Apenas os últimos 4 caracteres da chave (`key_hint`, ex: `"...3aF1"`) são retornados nas APIs de consulta de status. Nenhum segredo ou chave em texto claro é emitido em logs, mensagens de erro ou responses HTTP.
6. **Injeção em Memória no Pipeline RAG**:
   Durante a ingestão de documentos e chamadas conversacionais no chat, a chave do usuário é descriptografada em memória temporária para instanciar os clientes do Google Gemini, sendo descartada ao final do escopo da requisição.

## 3. Justificativa & Alternativas Consideradas

### Alternativa 1: Armazenamento em Texto Puro
- **Por que rejeitado**: Violação gravíssima dos Princípios IV (Security & Secrets Management) e da Constitution do Atlas AI. Um dump acidental do banco exporia credenciais de todos os usuários.

### Alternativa 2: Delegar Chamadas ao Frontend (Chave no Navegador)
- **Por que rejeitado**: Exporia a chave em chamadas de rede no cliente e impediria o backend de controlar o pipeline de RAG (pgvector, busca vetorial e prompt grounding ocorrem no servidor).

### Alternativa 3 (Escolhida): Criptografia Simétrica no Backend com Fernet
- **Vantagens**:
  - Segurança comprovada com autenticação de mensagem (AEAD).
  - Simplicidade operacional (chave de 32 bytes base64).
  - Capacidade de rotação segura via script de recriptografia.
  - Zero exposição de segredos para clientes.

## 4. Consequências e Impactos
- **Pontos Positivos**: Total privacidade e isolamento de custos por usuário; imunidade a vazamentos em logs e responses; compatibilidade total com o modelo de deploy Render + Vercel.
- **Trade-offs Aceitos**: Necessidade de gerenciar a variável `CREDENTIALS_ENCRYPTION_KEY` com backup seguro e necessidade de login do usuário para operações de IA.
- **Conformidade com a Constitution**: Atende estritamente aos Princípios I, II, III, IV, VI, VII e VIII.
