# 🔐 Sistema de Login e Senha

Um sistema completo de autenticação desenvolvido em Python com interface de terminal.

## ✨ Funcionalidades

- **Cadastro de usuários** com validação
- **Login seguro** com hash de senhas
- **Alteração de senha** para usuários logados
- **Visualização de informações** da conta
- **Logout** e gerenciamento de sessão
- **Armazenamento persistente** em arquivo JSON
- **Interface amigável** com emojis e menus organizados

## 🛡️ Segurança

- Senhas armazenadas com hash SHA-256
- Validação de entrada de dados
- Senha mínima de 6 caracteres
- Verificação de usuário existente

## 🚀 Como usar

### 1. Executar o sistema
```bash
python senha.py
```

### 2. Menu Principal
O sistema apresenta um menu com as seguintes opções:

1. **Cadastrar novo usuário** - Criar uma nova conta
2. **Fazer login** - Acessar com credenciais existentes
3. **Sair** - Encerrar o programa

### 3. Menu do Usuário (após login)
Após fazer login, você terá acesso a:

1. **Ver informações da conta** - Dados pessoais e histórico
2. **Alterar senha** - Modificar a senha atual
3. **Fazer logout** - Sair da conta
4. **Voltar ao menu principal** - Retornar ao menu inicial

## 📁 Arquivos do Sistema

- `senha.py` - Sistema principal
- `usuarios.json` - Arquivo de armazenamento (criado automaticamente)
- `README.md` - Este arquivo de documentação

## 🔧 Estrutura dos Dados

Os usuários são armazenados no arquivo `usuarios.json` com a seguinte estrutura:

```json
{
    "usuario1": {
        "senha": "hash_da_senha",
        "email": "usuario@email.com",
        "data_cadastro": "2024-01-01 12:00:00",
        "ultimo_login": "2024-01-01 15:30:00"
    }
}
```

## ⚠️ Requisitos

- Python 3.6 ou superior
- Bibliotecas padrão do Python (não requer instalação adicional)

## 🎯 Exemplo de Uso

```
==================================================
🔐 SISTEMA DE LOGIN E SENHA
==================================================
1. Cadastrar novo usuário
2. Fazer login
3. Sair
==================================================
Escolha uma opção: 1

📝 CADASTRO DE USUÁRIO
------------------------------
Digite o nome de usuário: joao
Digite a senha: 123456
Digite o email (opcional): joao@email.com
✅ Usuário cadastrado com sucesso!
```

## 🔒 Recursos de Segurança

- **Hash de senhas**: As senhas nunca são armazenadas em texto plano
- **Validação de entrada**: Verificação de dados obrigatórios
- **Sessão única**: Apenas um usuário pode estar logado por vez
- **Persistência segura**: Dados salvos em arquivo JSON com encoding UTF-8

## 🛠️ Personalização

Você pode modificar o sistema alterando:

- **Arquivo de usuários**: Mude o nome do arquivo no construtor da classe
- **Tamanho mínimo da senha**: Modifique a validação no método `cadastrar_usuario`
- **Algoritmo de hash**: Altere o método `hash_senha` para usar outros algoritmos
- **Interface**: Personalize os menus e mensagens

## 📝 Licença

Este projeto é de uso livre para fins educacionais e pessoais.
