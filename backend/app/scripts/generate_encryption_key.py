#!/usr/bin/env python3
"""CLI utility to generate a secure 32-byte Fernet encryption key for CREDENTIALS_ENCRYPTION_KEY."""

import sys
from cryptography.fernet import Fernet


def main() -> None:
    key = Fernet.generate_key().decode("utf-8")
    print("=" * 70)
    print("Atlas AI — Chave Mestra de Criptografia Gerada com Sucesso")
    print("=" * 70)
    print(f"\nCREDENTIALS_ENCRYPTION_KEY={key}\n")
    print("=" * 70)
    print("INSTRUÇÕES DE SEGURANÇA:")
    print("1. Copie e adicione essa variável no painel Environment do Render (Backend).")
    print("2. Para ambiente local, adicione no arquivo .env na raiz do projeto.")
    print("3. NUNCA faça commit desta chave no repositório Git.")
    print("=" * 70)


if __name__ == "__main__":
    main()
