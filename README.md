# Sistema de Gestão Completo

Aplicação em Python para gestão de usuários, estoque, vendas e financeiro, com interface de terminal e scripts utilitários. O código-fonte principal está em `login/`.

## Requisitos

- Python 3.13 (recomendado) — compatível com 3.12+
- Pip
- Windows: o script `login/EXECUTAR_SISTEMA.bat` facilita a execução

## Como executar

1. (Opcional) Crie e ative um ambiente virtual
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
2. Instale as dependências:
   ```powershell
   pip install -r login/requirements.txt
   ```
3. Rode pelo script (Windows):
   ```powershell
   .\login\EXECUTAR_SISTEMA.bat
   ```
   Ou diretamente pelo módulo principal:
   ```powershell
   python .\login\senha.py
   ```

## Estrutura do projeto

- `login/senha.py`: fluxo de autenticação, menus e orquestração
- `login/estoque.py`: cadastro de produtos e movimentações
- `login/vendas.py`: clientes, pedidos e recibos PDF
- `login/financeiro.py`: contas a pagar/receber e relatórios
- `login/*.json`: armazenamento de dados (simples) em arquivos JSON
- `login/recibos/`: recibos gerados em PDF

## Desenvolvimento

- Verificação rápida de sintaxe:
  ```powershell
  python -m compileall -q login
  ```
- Lint (opcional): instale `flake8` e rode `flake8 login`

## CI

Este repositório possui GitHub Actions para checagem de sintaxe a cada push/PR.

## Observações de segurança

- Evite commitar dados sensíveis. Chaves, tokens e PDFs gerados já estão ignorados via `.gitignore`.
- Os arquivos JSON são apenas para desenvolvimento/local. Para produção, considere um banco de dados.

## Licença

Defina a licença desejada (ex.: MIT) e adicione um arquivo `LICENSE`.


