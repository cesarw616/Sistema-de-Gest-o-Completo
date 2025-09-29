# 💰 SISTEMA FINANCEIRO COMPLETO

## 📋 Visão Geral

O sistema financeiro é um módulo completo integrado ao sistema principal que gerencia **Contas a Pagar** e **Contas a Receber** com funcionalidades avançadas de controle financeiro.

## 🎯 Funcionalidades Principais

### 📤 **Contas a Pagar**
- ✅ Cadastro de despesas fixas e variáveis
- ✅ Categorização automática (aluguel, internet, energia, etc.)
- ✅ Controle de vencimentos
- ✅ Status automático (pendente, pago, atrasado)
- ✅ Registro de pagamentos
- ✅ Alertas de vencimento

### 📥 **Contas a Receber**
- ✅ Cadastro de receitas
- ✅ Categorização por tipo (venda, serviço, comissão, etc.)
- ✅ Controle de vencimentos
- ✅ Status automático (pendente, recebido, atrasado)
- ✅ Registro de recebimentos
- ✅ Alertas de vencimento

## 🏗️ Estrutura de Dados

### **Contas a Pagar**
```json
{
  "id": "CP001",
  "descricao": "Aluguel",
  "categoria": "aluguel",
  "valor": 1000.00,
  "data_vencimento": "2025-09-05",
  "status": "pendente",
  "status_vencimento": "no_prazo",
  "fornecedor": "Imobiliária XYZ",
  "observacoes": "Aluguel mensal",
  "data_cadastro": "2025-08-21 13:30:00",
  "usuario_cadastro": "admin",
  "data_pagamento": null,
  "usuario_pagamento": null,
  "ativo": true
}
```

### **Contas a Receber**
```json
{
  "id": "CR001",
  "cliente": "João Silva",
  "descricao": "Venda de produtos",
  "categoria": "venda",
  "valor": 5000.00,
  "data_vencimento": "2025-08-25",
  "status": "pendente",
  "status_vencimento": "vencendo_em_breve",
  "observacoes": "Venda parcelada",
  "data_cadastro": "2025-08-21 13:30:00",
  "usuario_cadastro": "admin",
  "data_recebimento": null,
  "usuario_recebimento": null,
  "ativo": true
}
```

## 📊 Categorias Disponíveis

### **Contas a Pagar**
| Categoria | Nome | Tipo | Cor |
|-----------|------|------|-----|
| `aluguel` | Aluguel | Fixa | 🔴 |
| `internet` | Internet | Fixa | 🔴 |
| `energia` | Energia Elétrica | Variável | 🟡 |
| `agua` | Água | Variável | 🟡 |
| `fornecedor` | Fornecedor | Variável | 🟠 |
| `imposto` | Imposto | Fixa | 🔴 |
| `salario` | Salário | Fixa | 🔴 |
| `manutencao` | Manutenção | Variável | 🟠 |
| `marketing` | Marketing | Variável | 🟢 |
| `outros` | Outros | Variável | ⚪ |

### **Contas a Receber**
| Categoria | Nome | Tipo | Cor |
|-----------|------|------|-----|
| `venda` | Venda | Variável | 🟢 |
| `servico` | Serviço | Variável | 🟢 |
| `comissao` | Comissão | Variável | 🟢 |
| `aluguel_recebido` | Aluguel Recebido | Fixa | 🟢 |
| `investimento` | Investimento | Variável | 🟢 |
| `outros_recebimentos` | Outros Recebimentos | Variável | 🟢 |

## 🔧 Como Usar

### **1. Acessar o Sistema Financeiro**
1. Faça login no sistema
2. Escolha a opção **12. 💰 Gerenciar Financeiro**
3. Navegue pelas funcionalidades disponíveis

### **2. Cadastrar Conta a Pagar**
1. Escolha **1. Cadastrar conta a pagar**
2. Preencha os dados:
   - **Descrição**: Nome da conta
   - **Categoria**: Escolha uma categoria da lista
   - **Valor**: Valor em reais
   - **Data de vencimento**: Formato YYYY-MM-DD
   - **Fornecedor**: (opcional)
   - **Observações**: (opcional)

### **3. Cadastrar Conta a Receber**
1. Escolha **2. Cadastrar conta a receber**
2. Preencha os dados:
   - **Cliente**: Nome do cliente
   - **Descrição**: Descrição da conta
   - **Categoria**: Escolha uma categoria da lista
   - **Valor**: Valor em reais
   - **Data de vencimento**: Formato YYYY-MM-DD
   - **Observações**: (opcional)

### **4. Registrar Pagamento/Recebimento**
1. Escolha **7. Registrar pagamento** ou **8. Registrar recebimento**
2. Digite o **ID da conta**
3. Digite a **data** (ou pressione Enter para hoje)

## 📈 Relatórios Disponíveis

### **Acessar Relatórios**
1. Escolha **13. 📊 Relatórios Financeiros**
2. Navegue pelas opções disponíveis

### **Tipos de Relatórios**

#### **1. Relatório Financeiro Geral**
- Total a pagar e receber
- Valores pagos e recebidos
- Contas pendentes e atrasadas
- Saldo atual e projetado
- Resumo de contas

#### **2. Relatório por Período**
- Filtro por data de início e fim
- Análise temporal das finanças

#### **3. Análise por Categoria**
- Distribuição por categoria
- Valores pagos/pendentes por categoria

#### **4. Contas Atrasadas**
- Lista de contas vencidas
- Valores em atraso

#### **5. Fluxo de Caixa**
- Entradas e saídas
- Saldo atual e projetado

## ⚠️ Alertas de Vencimento

O sistema possui alertas automáticos:

- **🔴 Vencendo Hoje**: Contas que vencem hoje
- **🟡 Vencendo em 7 dias**: Contas que vencem na próxima semana
- **🔴 Atrasadas**: Contas vencidas

### **Acessar Alertas**
1. No menu financeiro, escolha **11. Alertas de vencimento**
2. Visualize todos os alertas ativos

## 🔍 Funcionalidades de Busca

### **Buscar Contas a Pagar**
- Por ID da conta
- Por descrição
- Por fornecedor

### **Buscar Contas a Receber**
- Por ID da conta
- Por cliente
- Por descrição

## 📊 Filtros Disponíveis

### **Contas a Pagar**
- Todas as contas
- Pendentes
- Pagas
- Atrasadas

### **Contas a Receber**
- Todas as contas
- Pendentes
- Recebidas
- Atrasadas

## 🗂️ Arquivos do Sistema

O sistema financeiro utiliza os seguintes arquivos:

- `contas_pagar.json` - Contas a pagar
- `contas_receber.json` - Contas a receber
- `categorias_financeiras.json` - Categorias do sistema

## 🎮 Exemplos de Uso

### **Exemplo 1: Cadastrar Aluguel**
```
Descrição: Aluguel da loja
Categoria: aluguel
Valor: R$ 2.500,00
Vencimento: 2025-09-05
Fornecedor: Imobiliária Central
```

### **Exemplo 2: Cadastrar Venda**
```
Cliente: Maria Silva
Descrição: Venda de produtos
Categoria: venda
Valor: R$ 1.500,00
Vencimento: 2025-08-30
```

### **Exemplo 3: Registrar Pagamento**
```
ID da conta: CP001
Data: 2025-08-20
```

## 💡 Dicas Importantes

1. **Sempre use o formato de data YYYY-MM-DD**
2. **Os valores são automaticamente formatados em reais**
3. **O sistema calcula automaticamente o status de vencimento**
4. **Use as categorias predefinidas para melhor organização**
5. **Monitore os alertas de vencimento regularmente**

## 🔐 Permissões

- **Funcionários**: Acesso completo ao sistema financeiro
- **Administradores**: Acesso completo + exclusão de contas
- **Clientes**: Sem acesso ao sistema financeiro

## 📞 Suporte

Se encontrar algum problema:
1. Verifique se está na pasta correta
2. Confirme se todos os arquivos estão presentes
3. Teste com dados simples primeiro
4. Consulte a documentação do sistema principal

---
**🎉 Sistema Financeiro Completo e Funcional!**
