# ADR 0001: Estratégia de Vetorização com pgvector e Chunking Recursivo

- **Status**: Aprovado
- **Data**: 2026-11-13
- **Autores**: Atlas AI Team
- **Contexto Técnico / Escopo**: Backend / RAG Engine / Banco de Dados Vetorial

---

## 1. Contexto e Declaração do Problema
O Atlas AI precisa processar documentos heterogêneos (PDF, TXT, Markdown), dividi-los em partes semanticamente coerentes e permitir busca por similaridade rápida e precisa. Dois desafios centrais se apresentam:
1. **Segmentação (Chunking)**: Textos muito grandes perdem precisão semântica na geração de embeddings; fatiamentos cegos quebram sentenças no meio e destroem o sentido.
2. **Armazenamento e Recuperação Vetorial**: Como armazenar vetores de alta dimensionalidade (768 dimensões) associados a metadados relacionais (bases, documentos, timestamps), evitando a complexidade operacional de gerenciar um banco vetorial externo isolado.

## 2. Decisão Arquitetural
Adotamos:
1. **PostgreSQL com a extensão `pgvector`** e índice **HNSW** (`vector_cosine_ops`) utilizando **Similaridade de Cosseno** como métrica de proximidade.
2. **Chunking Recursivo Nativo** (`RecursiveTextChunker`) com `chunk_size = 500` caracteres e `chunk_overlap = 100` caracteres, priorizando quebras em parágrafos (`\n\n`), linhas (`\n`), sentenças (`. `) e palavras (` `).
3. **Google Gemini `text-embedding-004`** como modelo de embedding padrão de 768 dimensões.

## 3. Justificativa & Alternativas Consideradas

### Alternativa 1: Banco Vetorial Especializado Externo (Pinecone / Qdrant Cloud)
- **Vantagens**: Recursos avançados de busca gerenciados.
- **Por que rejeitado**: Introduz dependência de rede adicional, custos de infraestrutura e quebra a transacionalidade ACID relacional com a base de dados principal.

### Alternativa 2: LangChain RecursiveCharacterTextSplitter
- **Vantagens**: Pronto para uso.
- **Por que rejeitado**: Pesa centenas de megabytes em dependências indiretas para uma função de 60 linhas de Python puro. Contraria o **Princípio VI da Constitution (KISS e uso consciente de frameworks)**.

### Alternativa 3 (Escolhida): pgvector + Chunker Puro em Python
- **Vantagens**:
  - Uma única instância de banco de dados para dados relacionais e vetoriais com suporte a `ON DELETE CASCADE` atômico.
  - Zero sobrecarga de frameworks externos; total transparência algorítmica para fins didáticos de portfólio.
  - O índice HNSW permite busca em sub-milissegundos com alta taxa de revocação (recall).

## 4. Consequências e Impactos
- **Pontos Positivos**: Simplicidade de deploy via `docker compose`, facilidade de testes unitários e perfeita rastreabilidade das fontes.
- **Trade-offs Aceitos**: Necessidade de compilar ou utilizar imagem oficial do PostgreSQL com `pgvector` (`pgvector/pgvector:pg16`).
- **Conformidade com a Constitution**: Atende aos Princípios I, II, V, VI e VII.

## 5. Notas Didáticas (Portfólio & Aprendizado)
- **Similaridade de Cosseno**: Mede o cosseno do ângulo entre dois vetores normalizados no hiperplano de 768 dimensões. Valores próximos de 1.0 indicam alta similaridade de significado, independentemente do comprimento do texto.
- **Overlap**: O overlap de 100 caracteres garante que termos ou sentenças localizadas na fronteira de um corte não percam seu contexto imediato.
