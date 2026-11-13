# Research & Technical Decisions: Conversational RAG & Chatbot Engine

**Feature**: `002-conversational-rag-chat`  
**Date**: 2026-11-13  
**Status**: Completed  

---

## 1. Seleção e Comparativo de Tecnologias

### 1.1 Modelo LLM para Síntese Conversacional
- **Desafio**: Selecionar um modelo de linguagem que combine baixa latência (< 2s para síntese), alta fidelidade ao contexto fornecido, excelente raciocínio em português/inglês e custo balanceado.
- **Opções Analisadas**:
  1. *Gemini 2.5 Flash*: Modelo multimodal mais recente da Google, ultra-rápido, otimizado para tarefas de RAG e raciocínio de alta precisão com custo reduzido.
  2. *Gemini 1.5 Pro*: Excelente para raciocínio complexo, porém com latência mais elevada para interfaces de chat interativo.
- **Decisão**: Adotar o **Gemini 2.5 Flash** (`gemini-2.5-flash`) como modelo padrão configurável via `GEMINI_CHAT_MODEL`.
- **Justificativa Didática**: Oferece o menor *Time-to-First-Token* e atende com facilidade a meta de latência $< 3.5$ segundos fim a fim.

---

### 1.2 Engenharia de Prompt Anti-Alucinação e Proteção contra Prompt Injection
- **Desafio**: Prevenir que o LLM invente respostas quando o contexto for escasso (alucinação) e evitar que instruções adversariais embutidas nos documentos sequestrem o prompt de sistema (*prompt injection*).
- **Decisão**:
  1. **Delimitação Estrita de Contexto**:
     Os chunks recuperados do banco vetorial são encapsulados em tags estruturadas:
     ```text
     <context>
     [Documento 1: manual_tecnico.pdf (Chunk 0, Relevância: 0.89)]
     Trecho de texto recuperado...
     
     [Documento 2: politica.md (Chunk 3, Relevância: 0.84)]
     Outro trecho de texto...
     </context>
     ```
  2. **Diretiva de Sistema Não Negociável**:
     "Você é o assistente virtual Atlas AI. Sua responsabilidade é responder à pergunta do usuário baseando-se ESTRITAMENTE e EXCLUSIVAMENTE nas informações contidas dentro das tags <context> acima. Se o contexto não contiver dados suficientes para responder com certeza, você DEVE declarar explicitamente: 'Desculpe, não encontrei informações sobre este tema nos documentos da base de conhecimento.' NUNCA tente inventar dados ou recorrer a conhecimento externo não fundamentado."
  3. **Mapeamento de Citações**:
     O assistente referencia os documentos e o backend anexa as fontes estruturadas no payload JSON (`citations`).

---

### 1.3 Gestão de Histórico e Janela de Contexto (Multi-Turn)
- **Desafio**: Permitir que o usuário faça perguntas de acompanhamento ("Qual foi o primeiro item mencionado?") sem exceder a janela de contexto ou diluir a recuperação semântica.
- **Decisão**:
  - Armazenar todas as mensagens no PostgreSQL na tabela `chat_messages`.
  - Na chamada ao LLM, enviar uma **janela deslizante** das últimas $K = 6$ mensagens (3 turnos completos de pergunta/resposta) precedidas pelo bloco de contexto dos chunks recuperados da pergunta atual.
  - Isso garante continuidade imediata mantendo a requisição leve e veloz.

---

### 1.4 Observabilidade e Métricas de Execução
- **Decisão**:
  - Registrar em cada mensagem do assistente:
    - `prompt_tokens`: Tokens consumidos pela pergunta, histórico e contexto documental.
    - `completion_tokens`: Tokens gerados na resposta.
    - `latency_ms`: Tempo total transcorrido desde o início da requisição até a persistência no banco.
  - Isso cumpre o **Princípio V da Constitution (Engenharia de IA Responsável & Observabilidade)**.
