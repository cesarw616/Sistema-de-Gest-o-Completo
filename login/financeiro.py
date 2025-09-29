import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal, ROUND_HALF_UP

class SistemaFinanceiro:
    def __init__(self, arquivo_contas_pagar: str = "contas_pagar.json", 
                 arquivo_contas_receber: str = "contas_receber.json",
                 arquivo_categorias: str = "categorias_financeiras.json"):
        """
        Inicializa o sistema financeiro
        
        Args:
            arquivo_contas_pagar: Arquivo para armazenar contas a pagar
            arquivo_contas_receber: Arquivo para armazenar contas a receber
            arquivo_categorias: Arquivo para armazenar categorias
        """
        self.arquivo_contas_pagar = arquivo_contas_pagar
        self.arquivo_contas_receber = arquivo_contas_receber
        self.arquivo_categorias = arquivo_categorias
        
        self.contas_pagar = self.carregar_contas_pagar()
        self.contas_receber = self.carregar_contas_receber()
        self.categorias = self.carregar_categorias()
        
        # Inicializa categorias padrão se não existirem
        if not self.categorias:
            self.inicializar_categorias_padrao()
    
    def carregar_contas_pagar(self) -> List:
        """Carrega contas a pagar do arquivo JSON"""
        if os.path.exists(self.arquivo_contas_pagar):
            try:
                with open(self.arquivo_contas_pagar, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def carregar_contas_receber(self) -> List:
        """Carrega contas a receber do arquivo JSON"""
        if os.path.exists(self.arquivo_contas_receber):
            try:
                with open(self.arquivo_contas_receber, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def carregar_categorias(self) -> Dict:
        """Carrega categorias do arquivo JSON"""
        if os.path.exists(self.arquivo_categorias):
            try:
                with open(self.arquivo_categorias, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def salvar_contas_pagar(self):
        """Salva contas a pagar no arquivo JSON"""
        with open(self.arquivo_contas_pagar, 'w', encoding='utf-8') as arquivo:
            json.dump(self.contas_pagar, arquivo, indent=4, ensure_ascii=False)
    
    def salvar_contas_receber(self):
        """Salva contas a receber no arquivo JSON"""
        with open(self.arquivo_contas_receber, 'w', encoding='utf-8') as arquivo:
            json.dump(self.contas_receber, arquivo, indent=4, ensure_ascii=False)
    
    def salvar_categorias(self):
        """Salva categorias no arquivo JSON"""
        with open(self.arquivo_categorias, 'w', encoding='utf-8') as arquivo:
            json.dump(self.categorias, arquivo, indent=4, ensure_ascii=False)
    
    def inicializar_categorias_padrao(self):
        """Inicializa categorias padrão do sistema"""
        self.categorias = {
            "contas_pagar": {
                "aluguel": {"nome": "Aluguel", "tipo": "fixa", "cor": "🔴"},
                "internet": {"nome": "Internet", "tipo": "fixa", "cor": "🔴"},
                "energia": {"nome": "Energia Elétrica", "tipo": "variavel", "cor": "🟡"},
                "agua": {"nome": "Água", "tipo": "variavel", "cor": "🟡"},
                "fornecedor": {"nome": "Fornecedor", "tipo": "variavel", "cor": "🟠"},
                "imposto": {"nome": "Imposto", "tipo": "fixa", "cor": "🔴"},
                "salario": {"nome": "Salário", "tipo": "fixa", "cor": "🔴"},
                "manutencao": {"nome": "Manutenção", "tipo": "variavel", "cor": "🟠"},
                "marketing": {"nome": "Marketing", "tipo": "variavel", "cor": "🟢"},
                "outros": {"nome": "Outros", "tipo": "variavel", "cor": "⚪"}
            },
            "contas_receber": {
                "venda": {"nome": "Venda", "tipo": "variavel", "cor": "🟢"},
                "servico": {"nome": "Serviço", "tipo": "variavel", "cor": "🟢"},
                "comissao": {"nome": "Comissão", "tipo": "variavel", "cor": "🟢"},
                "aluguel_recebido": {"nome": "Aluguel Recebido", "tipo": "fixa", "cor": "🟢"},
                "investimento": {"nome": "Investimento", "tipo": "variavel", "cor": "🟢"},
                "outros_recebimentos": {"nome": "Outros Recebimentos", "tipo": "variavel", "cor": "🟢"}
            }
        }
        self.salvar_categorias()
    
    def gerar_id_conta(self, tipo: str) -> str:
        """Gera um ID único para conta"""
        if tipo == "pagar":
            prefixo = "CP"
            contas = self.contas_pagar
        else:
            prefixo = "CR"
            contas = self.contas_receber
        
        if not contas:
            return f"{prefixo}001"
        
        # Encontra o maior número existente
        numeros = []
        for conta in contas:
            if conta["id"].startswith(prefixo):
                try:
                    numero = int(conta["id"][2:])
                    numeros.append(numero)
                except ValueError:
                    continue
        
        if numeros:
            proximo_numero = max(numeros) + 1
        else:
            proximo_numero = 1
        
        return f"{prefixo}{proximo_numero:03d}"
    
    def validar_data(self, data_str: str) -> bool:
        """Valida formato de data (YYYY-MM-DD)"""
        try:
            datetime.strptime(data_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def calcular_status_vencimento(self, data_vencimento: str) -> str:
        """Calcula status baseado na data de vencimento"""
        try:
            data_venc = datetime.strptime(data_vencimento, "%Y-%m-%d")
            data_atual = datetime.now().date()
            
            if data_venc.date() < data_atual:
                return "atrasado"
            elif data_venc.date() == data_atual:
                return "vencendo_hoje"
            elif (data_venc.date() - data_atual).days <= 7:
                return "vencendo_em_breve"
            else:
                return "no_prazo"
        except:
            return "data_invalida"
    
    def formatar_valor(self, valor: float) -> str:
        """Formata valor para exibição"""
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def cadastrar_conta_pagar(self, descricao: str, categoria: str, valor: float, 
                            data_vencimento: str, fornecedor: str = "", 
                            observacoes: str = "", usuario: str = "sistema") -> str:
        """
        Cadastra uma nova conta a pagar
        
        Args:
            descricao: Descrição da conta
            categoria: Categoria da conta
            valor: Valor da conta
            data_vencimento: Data de vencimento (YYYY-MM-DD)
            fornecedor: Nome do fornecedor
            observacoes: Observações adicionais
            usuario: Usuário que está cadastrando
            
        Returns:
            ID da conta criada ou None se erro
        """
        if not descricao or not categoria or valor <= 0:
            print("❌ Erro: Dados da conta inválidos!")
            return None
        
        if categoria not in self.categorias["contas_pagar"]:
            print("❌ Erro: Categoria inválida!")
            return None
        
        if not self.validar_data(data_vencimento):
            print("❌ Erro: Data de vencimento inválida! Use formato YYYY-MM-DD")
            return None
        
        conta_id = self.gerar_id_conta("pagar")
        status_vencimento = self.calcular_status_vencimento(data_vencimento)
        
        conta = {
            "id": conta_id,
            "descricao": descricao,
            "categoria": categoria,
            "valor": valor,
            "data_vencimento": data_vencimento,
            "status": "pendente",
            "status_vencimento": status_vencimento,
            "fornecedor": fornecedor,
            "observacoes": observacoes,
            "data_cadastro": time.strftime("%Y-%m-%d %H:%M:%S"),
            "usuario_cadastro": usuario,
            "data_pagamento": None,
            "usuario_pagamento": None,
            "ativo": True
        }
        
        self.contas_pagar.append(conta)
        self.salvar_contas_pagar()
        
        categoria_info = self.categorias["contas_pagar"][categoria]
        print(f"✅ Conta a pagar {conta_id} cadastrada!")
        print(f"📝 {descricao} - {categoria_info['nome']}")
        print(f"💰 Valor: {self.formatar_valor(valor)}")
        print(f"📅 Vencimento: {data_vencimento}")
        
        return conta_id
    
    def cadastrar_conta_receber(self, cliente: str, descricao: str, categoria: str, 
                              valor: float, data_vencimento: str, 
                              observacoes: str = "", usuario: str = "sistema") -> str:
        """
        Cadastra uma nova conta a receber
        
        Args:
            cliente: Nome do cliente
            descricao: Descrição da conta
            categoria: Categoria da conta
            valor: Valor da conta
            data_vencimento: Data de vencimento (YYYY-MM-DD)
            observacoes: Observações adicionais
            usuario: Usuário que está cadastrando
            
        Returns:
            ID da conta criada ou None se erro
        """
        if not cliente or not descricao or not categoria or valor <= 0:
            print("❌ Erro: Dados da conta inválidos!")
            return None
        
        if categoria not in self.categorias["contas_receber"]:
            print("❌ Erro: Categoria inválida!")
            return None
        
        if not self.validar_data(data_vencimento):
            print("❌ Erro: Data de vencimento inválida! Use formato YYYY-MM-DD")
            return None
        
        conta_id = self.gerar_id_conta("receber")
        status_vencimento = self.calcular_status_vencimento(data_vencimento)
        
        conta = {
            "id": conta_id,
            "cliente": cliente,
            "descricao": descricao,
            "categoria": categoria,
            "valor": valor,
            "data_vencimento": data_vencimento,
            "status": "pendente",
            "status_vencimento": status_vencimento,
            "observacoes": observacoes,
            "data_cadastro": time.strftime("%Y-%m-%d %H:%M:%S"),
            "usuario_cadastro": usuario,
            "data_recebimento": None,
            "usuario_recebimento": None,
            "ativo": True
        }
        
        self.contas_receber.append(conta)
        self.salvar_contas_receber()
        
        categoria_info = self.categorias["contas_receber"][categoria]
        print(f"✅ Conta a receber {conta_id} cadastrada!")
        print(f"👤 Cliente: {cliente}")
        print(f"📝 {descricao} - {categoria_info['nome']}")
        print(f"💰 Valor: {self.formatar_valor(valor)}")
        print(f"📅 Vencimento: {data_vencimento}")
        
        return conta_id
    
    def listar_contas_pagar(self, status: str = None, categoria: str = None) -> List[Dict]:
        """
        Lista contas a pagar com filtros
        
        Args:
            status: Filtro por status (pendente, pago, atrasado)
            categoria: Filtro por categoria
            
        Returns:
            Lista de contas a pagar
        """
        contas_filtradas = []
        
        for conta in self.contas_pagar:
            if not conta.get("ativo", True):
                continue
            
            # Atualiza status de vencimento
            conta["status_vencimento"] = self.calcular_status_vencimento(conta["data_vencimento"])
            
            # Aplica filtros
            if status and conta["status"] != status:
                continue
            if categoria and conta["categoria"] != categoria:
                continue
            
            contas_filtradas.append(conta)
        
        # Salva alterações
        self.salvar_contas_pagar()
        
        return sorted(contas_filtradas, key=lambda x: x["data_vencimento"])
    
    def listar_contas_receber(self, status: str = None, categoria: str = None) -> List[Dict]:
        """
        Lista contas a receber com filtros
        
        Args:
            status: Filtro por status (pendente, recebido, atrasado)
            categoria: Filtro por categoria
            
        Returns:
            Lista de contas a receber
        """
        contas_filtradas = []
        
        for conta in self.contas_receber:
            if not conta.get("ativo", True):
                continue
            
            # Atualiza status de vencimento
            conta["status_vencimento"] = self.calcular_status_vencimento(conta["data_vencimento"])
            
            # Aplica filtros
            if status and conta["status"] != status:
                continue
            if categoria and conta["categoria"] != categoria:
                continue
            
            contas_filtradas.append(conta)
        
        # Salva alterações
        self.salvar_contas_receber()
        
        return sorted(contas_filtradas, key=lambda x: x["data_vencimento"])
    
    def buscar_conta_pagar(self, termo: str) -> List[Dict]:
        """
        Busca conta a pagar por ID, descrição ou fornecedor
        
        Args:
            termo: Termo de busca
            
        Returns:
            Lista de contas encontradas
        """
        resultados = []
        termo_lower = termo.lower()
        
        for conta in self.contas_pagar:
            if not conta.get("ativo", True):
                continue
            
            if (termo_lower in conta["id"].lower() or 
                termo_lower in conta["descricao"].lower() or 
                termo_lower in conta["fornecedor"].lower()):
                resultados.append(conta)
        
        return resultados
    
    def buscar_conta_receber(self, termo: str) -> List[Dict]:
        """
        Busca conta a receber por ID, cliente ou descrição
        
        Args:
            termo: Termo de busca
            
        Returns:
            Lista de contas encontradas
        """
        resultados = []
        termo_lower = termo.lower()
        
        for conta in self.contas_receber:
            if not conta.get("ativo", True):
                continue
            
            if (termo_lower in conta["id"].lower() or 
                termo_lower in conta["cliente"].lower() or 
                termo_lower in conta["descricao"].lower()):
                resultados.append(conta)
        
        return resultados
    
    def registrar_pagamento(self, conta_id: str, data_pagamento: str = None, 
                          usuario: str = "sistema") -> bool:
        """
        Registra pagamento de uma conta
        
        Args:
            conta_id: ID da conta
            data_pagamento: Data do pagamento (YYYY-MM-DD)
            usuario: Usuário que está registrando
            
        Returns:
            True se sucesso, False se erro
        """
        for conta in self.contas_pagar:
            if conta["id"] == conta_id and conta.get("ativo", True):
                if conta["status"] == "pago":
                    print("❌ Erro: Conta já foi paga!")
                    return False
                
                if not data_pagamento:
                    data_pagamento = time.strftime("%Y-%m-%d")
                
                if not self.validar_data(data_pagamento):
                    print("❌ Erro: Data de pagamento inválida!")
                    return False
                
                conta["status"] = "pago"
                conta["data_pagamento"] = data_pagamento
                conta["usuario_pagamento"] = usuario
                conta["status_vencimento"] = "pago"
                
                self.salvar_contas_pagar()
                
                print(f"✅ Pagamento registrado para conta {conta_id}!")
                print(f"📝 {conta['descricao']}")
                print(f"💰 Valor: {self.formatar_valor(conta['valor'])}")
                print(f"📅 Data do pagamento: {data_pagamento}")
                
                return True
        
        print("❌ Erro: Conta não encontrada!")
        return False
    
    def registrar_recebimento(self, conta_id: str, data_recebimento: str = None, 
                            usuario: str = "sistema") -> bool:
        """
        Registra recebimento de uma conta
        
        Args:
            conta_id: ID da conta
            data_recebimento: Data do recebimento (YYYY-MM-DD)
            usuario: Usuário que está registrando
            
        Returns:
            True se sucesso, False se erro
        """
        for conta in self.contas_receber:
            if conta["id"] == conta_id and conta.get("ativo", True):
                if conta["status"] == "recebido":
                    print("❌ Erro: Conta já foi recebida!")
                    return False
                
                if not data_recebimento:
                    data_recebimento = time.strftime("%Y-%m-%d")
                
                if not self.validar_data(data_recebimento):
                    print("❌ Erro: Data de recebimento inválida!")
                    return False
                
                conta["status"] = "recebido"
                conta["data_recebimento"] = data_recebimento
                conta["usuario_recebimento"] = usuario
                conta["status_vencimento"] = "recebido"
                
                self.salvar_contas_receber()
                
                print(f"✅ Recebimento registrado para conta {conta_id}!")
                print(f"👤 Cliente: {conta['cliente']}")
                print(f"📝 {conta['descricao']}")
                print(f"💰 Valor: {self.formatar_valor(conta['valor'])}")
                print(f"📅 Data do recebimento: {data_recebimento}")
                
                return True
        
        print("❌ Erro: Conta não encontrada!")
        return False
    
    def relatorio_financeiro(self, data_inicio: str = None, data_fim: str = None) -> Dict:
        """
        Gera relatório financeiro completo
        
        Args:
            data_inicio: Data de início (YYYY-MM-DD)
            data_fim: Data de fim (YYYY-MM-DD)
            
        Returns:
            Dicionário com dados do relatório
        """
        # Filtra contas por período se especificado
        contas_pagar_filtradas = self.contas_pagar
        contas_receber_filtradas = self.contas_receber
        
        if data_inicio or data_fim:
            contas_pagar_filtradas = []
            contas_receber_filtradas = []
            
            for conta in self.contas_pagar:
                if conta.get("ativo", True):
                    data_conta = conta["data_vencimento"]
                    if data_inicio and data_conta < data_inicio:
                        continue
                    if data_fim and data_conta > data_fim:
                        continue
                    contas_pagar_filtradas.append(conta)
            
            for conta in self.contas_receber:
                if conta.get("ativo", True):
                    data_conta = conta["data_vencimento"]
                    if data_inicio and data_conta < data_inicio:
                        continue
                    if data_fim and data_conta > data_fim:
                        continue
                    contas_receber_filtradas.append(conta)
        
        # Calcula totais
        total_pagar = sum(conta["valor"] for conta in contas_pagar_filtradas if conta.get("ativo", True))
        total_receber = sum(conta["valor"] for conta in contas_receber_filtradas if conta.get("ativo", True))
        
        # Contas pagas e recebidas
        total_pago = sum(conta["valor"] for conta in contas_pagar_filtradas 
                        if conta.get("ativo", True) and conta["status"] == "pago")
        total_recebido = sum(conta["valor"] for conta in contas_receber_filtradas 
                           if conta.get("ativo", True) and conta["status"] == "recebido")
        
        # Contas pendentes
        total_pagar_pendente = sum(conta["valor"] for conta in contas_pagar_filtradas 
                                 if conta.get("ativo", True) and conta["status"] == "pendente")
        total_receber_pendente = sum(conta["valor"] for conta in contas_receber_filtradas 
                                   if conta.get("ativo", True) and conta["status"] == "pendente")
        
        # Contas atrasadas
        contas_pagar_atrasadas = [conta for conta in contas_pagar_filtradas 
                                if conta.get("ativo", True) and conta["status_vencimento"] == "atrasado"]
        contas_receber_atrasadas = [conta for conta in contas_receber_filtradas 
                                  if conta.get("ativo", True) and conta["status_vencimento"] == "atrasado"]
        
        total_pagar_atrasado = sum(conta["valor"] for conta in contas_pagar_atrasadas)
        total_receber_atrasado = sum(conta["valor"] for conta in contas_receber_atrasadas)
        
        # Saldo
        saldo = total_recebido - total_pago
        saldo_futuro = (total_receber - total_pagar)
        
        # Análise por categoria
        categorias_pagar = {}
        categorias_receber = {}
        
        for conta in contas_pagar_filtradas:
            if conta.get("ativo", True):
                cat = conta["categoria"]
                if cat not in categorias_pagar:
                    categorias_pagar[cat] = {"total": 0, "pago": 0, "pendente": 0}
                categorias_pagar[cat]["total"] += conta["valor"]
                if conta["status"] == "pago":
                    categorias_pagar[cat]["pago"] += conta["valor"]
                else:
                    categorias_pagar[cat]["pendente"] += conta["valor"]
        
        for conta in contas_receber_filtradas:
            if conta.get("ativo", True):
                cat = conta["categoria"]
                if cat not in categorias_receber:
                    categorias_receber[cat] = {"total": 0, "recebido": 0, "pendente": 0}
                categorias_receber[cat]["total"] += conta["valor"]
                if conta["status"] == "recebido":
                    categorias_receber[cat]["recebido"] += conta["valor"]
                else:
                    categorias_receber[cat]["pendente"] += conta["valor"]
        
        return {
            "resumo": {
                "total_pagar": total_pagar,
                "total_receber": total_receber,
                "total_pago": total_pago,
                "total_recebido": total_recebido,
                "total_pagar_pendente": total_pagar_pendente,
                "total_receber_pendente": total_receber_pendente,
                "total_pagar_atrasado": total_pagar_atrasado,
                "total_receber_atrasado": total_receber_atrasado,
                "saldo": saldo,
                "saldo_futuro": saldo_futuro
            },
            "contas_pagar": {
                "total": len(contas_pagar_filtradas),
                "pendentes": len([c for c in contas_pagar_filtradas if c.get("ativo", True) and c["status"] == "pendente"]),
                "pagas": len([c for c in contas_pagar_filtradas if c.get("ativo", True) and c["status"] == "pago"]),
                "atrasadas": len(contas_pagar_atrasadas)
            },
            "contas_receber": {
                "total": len(contas_receber_filtradas),
                "pendentes": len([c for c in contas_receber_filtradas if c.get("ativo", True) and c["status"] == "pendente"]),
                "recebidas": len([c for c in contas_receber_filtradas if c.get("ativo", True) and c["status"] == "recebido"]),
                "atrasadas": len(contas_receber_atrasadas)
            },
            "categorias_pagar": categorias_pagar,
            "categorias_receber": categorias_receber,
            "contas_atrasadas": {
                "pagar": contas_pagar_atrasadas,
                "receber": contas_receber_atrasadas
            },
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "data_relatorio": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def obter_alertas_vencimento(self) -> Dict:
        """
        Obtém alertas de vencimento
        
        Returns:
            Dicionário com alertas
        """
        hoje = datetime.now().date()
        alertas = {
            "vencendo_hoje": [],
            "vencendo_em_7_dias": [],
            "atrasadas": []
        }
        
        # Contas a pagar
        for conta in self.contas_pagar:
            if not conta.get("ativo", True) or conta["status"] == "pago":
                continue
            
            try:
                data_venc = datetime.strptime(conta["data_vencimento"], "%Y-%m-%d").date()
                dias_para_vencer = (data_venc - hoje).days
                
                if dias_para_vencer == 0:
                    alertas["vencendo_hoje"].append({"tipo": "pagar", "conta": conta})
                elif dias_para_vencer < 0:
                    alertas["atrasadas"].append({"tipo": "pagar", "conta": conta})
                elif dias_para_vencer <= 7:
                    alertas["vencendo_em_7_dias"].append({"tipo": "pagar", "conta": conta})
            except:
                continue
        
        # Contas a receber
        for conta in self.contas_receber:
            if not conta.get("ativo", True) or conta["status"] == "recebido":
                continue
            
            try:
                data_venc = datetime.strptime(conta["data_vencimento"], "%Y-%m-%d").date()
                dias_para_vencer = (data_venc - hoje).days
                
                if dias_para_vencer == 0:
                    alertas["vencendo_hoje"].append({"tipo": "receber", "conta": conta})
                elif dias_para_vencer < 0:
                    alertas["atrasadas"].append({"tipo": "receber", "conta": conta})
                elif dias_para_vencer <= 7:
                    alertas["vencendo_em_7_dias"].append({"tipo": "receber", "conta": conta})
            except:
                continue
        
        return alertas
    
    def excluir_conta_pagar(self, conta_id: str, usuario: str = "sistema") -> bool:
        """
        Exclui (desativa) uma conta a pagar
        
        Args:
            conta_id: ID da conta
            usuario: Usuário que está excluindo
            
        Returns:
            True se sucesso, False se erro
        """
        for conta in self.contas_pagar:
            if conta["id"] == conta_id and conta.get("ativo", True):
                conta["ativo"] = False
                self.salvar_contas_pagar()
                print(f"✅ Conta a pagar {conta_id} excluída!")
                return True
        
        print("❌ Erro: Conta não encontrada!")
        return False
    
    def excluir_conta_receber(self, conta_id: str, usuario: str = "sistema") -> bool:
        """
        Exclui (desativa) uma conta a receber
        
        Args:
            conta_id: ID da conta
            usuario: Usuário que está excluindo
            
        Returns:
            True se sucesso, False se erro
        """
        for conta in self.contas_receber:
            if conta["id"] == conta_id and conta.get("ativo", True):
                conta["ativo"] = False
                self.salvar_contas_receber()
                print(f"✅ Conta a receber {conta_id} excluída!")
                return True
        
        print("❌ Erro: Conta não encontrada!")
        return False
    
    def fluxo_caixa_diario(self, data: str = None) -> Dict:
        """
        Gera fluxo de caixa diário
        
        Args:
            data: Data no formato YYYY-MM-DD (padrão: hoje)
            
        Returns:
            Dicionário com resumo do fluxo de caixa
        """
        if data is None:
            data = datetime.now().strftime("%Y-%m-%d")
        
        if not self.validar_data(data):
            return {"erro": "Data inválida"}
        
        data_obj = datetime.strptime(data, "%Y-%m-%d").date()
        
        # Entradas (receitas recebidas na data)
        entradas = []
        total_entradas = Decimal('0.00')
        
        for conta in self.contas_receber:
            if (conta.get("ativo", True) and 
                conta["status"] == "recebido" and 
                conta.get("data_recebimento") == data):
                entradas.append(conta)
                total_entradas += Decimal(str(conta["valor"]))
        
        # Saídas (despesas pagas na data)
        saidas = []
        total_saidas = Decimal('0.00')
        
        for conta in self.contas_pagar:
            if (conta.get("ativo", True) and 
                conta["status"] == "pago" and 
                conta.get("data_pagamento") == data):
                saidas.append(conta)
                total_saidas += Decimal(str(conta["valor"]))
        
        # Saldo do dia
        saldo_dia = total_entradas - total_saidas
        
        return {
            "data": data,
            "entradas": {
                "transacoes": entradas,
                "total": float(total_entradas),
                "quantidade": len(entradas)
            },
            "saidas": {
                "transacoes": saidas,
                "total": float(total_saidas),
                "quantidade": len(saidas)
            },
            "saldo_dia": float(saldo_dia),
            "saldo_formatado": self.formatar_valor(saldo_dia)
        }
    
    def fluxo_caixa_mensal(self, ano: int = None, mes: int = None) -> Dict:
        """
        Gera fluxo de caixa mensal
        
        Args:
            ano: Ano (padrão: ano atual)
            mes: Mês (1-12, padrão: mês atual)
            
        Returns:
            Dicionário com resumo do fluxo de caixa mensal
        """
        if ano is None:
            ano = datetime.now().year
        if mes is None:
            mes = datetime.now().month
        
        # Primeiro e último dia do mês
        data_inicio = datetime(ano, mes, 1).date()
        if mes == 12:
            data_fim = datetime(ano + 1, 1, 1).date() - timedelta(days=1)
        else:
            data_fim = datetime(ano, mes + 1, 1).date() - timedelta(days=1)
        
        # Entradas do mês
        entradas = []
        total_entradas = Decimal('0.00')
        
        for conta in self.contas_receber:
            if not conta.get("ativo", True) or conta["status"] != "recebido":
                continue
            
            try:
                data_recebimento = datetime.strptime(conta.get("data_recebimento", ""), "%Y-%m-%d").date()
                if data_inicio <= data_recebimento <= data_fim:
                    entradas.append(conta)
                    total_entradas += Decimal(str(conta["valor"]))
            except:
                continue
        
        # Saídas do mês
        saidas = []
        total_saidas = Decimal('0.00')
        
        for conta in self.contas_pagar:
            if not conta.get("ativo", True) or conta["status"] != "pago":
                continue
            
            try:
                data_pagamento = datetime.strptime(conta.get("data_pagamento", ""), "%Y-%m-%d").date()
                if data_inicio <= data_pagamento <= data_fim:
                    saidas.append(conta)
                    total_saidas += Decimal(str(conta["valor"]))
            except:
                continue
        
        # Saldo do mês
        saldo_mes = total_entradas - total_saidas
        
        # Resumo por categoria
        categorias_entradas = {}
        categorias_saidas = {}
        
        for conta in entradas:
            categoria = conta.get("categoria", "Sem categoria")
            if categoria not in categorias_entradas:
                categorias_entradas[categoria] = Decimal('0.00')
            categorias_entradas[categoria] += Decimal(str(conta["valor"]))
        
        for conta in saidas:
            categoria = conta.get("categoria", "Sem categoria")
            if categoria not in categorias_saidas:
                categorias_saidas[categoria] = Decimal('0.00')
            categorias_saidas[categoria] += Decimal(str(conta["valor"]))
        
        return {
            "ano": ano,
            "mes": mes,
            "mes_nome": datetime(ano, mes, 1).strftime("%B"),
            "data_inicio": data_inicio.strftime("%Y-%m-%d"),
            "data_fim": data_fim.strftime("%Y-%m-%d"),
            "entradas": {
                "transacoes": entradas,
                "total": float(total_entradas),
                "quantidade": len(entradas),
                "por_categoria": {k: float(v) for k, v in categorias_entradas.items()}
            },
            "saidas": {
                "transacoes": saidas,
                "total": float(total_saidas),
                "quantidade": len(saidas),
                "por_categoria": {k: float(v) for k, v in categorias_saidas.items()}
            },
            "saldo_mes": float(saldo_mes),
            "saldo_formatado": self.formatar_valor(saldo_mes)
        }
    
    def fluxo_caixa_periodo(self, data_inicio: str, data_fim: str) -> Dict:
        """
        Gera fluxo de caixa para um período específico
        
        Args:
            data_inicio: Data inicial (YYYY-MM-DD)
            data_fim: Data final (YYYY-MM-DD)
            
        Returns:
            Dicionário com resumo do fluxo de caixa do período
        """
        if not self.validar_data(data_inicio) or not self.validar_data(data_fim):
            return {"erro": "Data inválida"}
        
        data_ini = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        data_fim_obj = datetime.strptime(data_fim, "%Y-%m-%d").date()
        
        if data_ini > data_fim_obj:
            return {"erro": "Data inicial maior que data final"}
        
        # Entradas do período
        entradas = []
        total_entradas = Decimal('0.00')
        
        for conta in self.contas_receber:
            if not conta.get("ativo", True) or conta["status"] != "recebido":
                continue
            
            try:
                data_recebimento = datetime.strptime(conta.get("data_recebimento", ""), "%Y-%m-%d").date()
                if data_ini <= data_recebimento <= data_fim_obj:
                    entradas.append(conta)
                    total_entradas += Decimal(str(conta["valor"]))
            except:
                continue
        
        # Saídas do período
        saidas = []
        total_saidas = Decimal('0.00')
        
        for conta in self.contas_pagar:
            if not conta.get("ativo", True) or conta["status"] != "pago":
                continue
            
            try:
                data_pagamento = datetime.strptime(conta.get("data_pagamento", ""), "%Y-%m-%d").date()
                if data_ini <= data_pagamento <= data_fim_obj:
                    saidas.append(conta)
                    total_saidas += Decimal(str(conta["valor"]))
            except:
                continue
        
        # Saldo do período
        saldo_periodo = total_entradas - total_saidas
        
        return {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "entradas": {
                "transacoes": entradas,
                "total": float(total_entradas),
                "quantidade": len(entradas)
            },
            "saidas": {
                "transacoes": saidas,
                "total": float(total_saidas),
                "quantidade": len(saidas)
            },
            "saldo_periodo": float(saldo_periodo),
            "saldo_formatado": self.formatar_valor(saldo_periodo)
        }
    
    def tabela_transacoes_fluxo_caixa(self, fluxo_data: Dict) -> str:
        """
        Gera tabela formatada das transações do fluxo de caixa
        
        Args:
            fluxo_data: Dados do fluxo de caixa
            
        Returns:
            String formatada da tabela
        """
        if "erro" in fluxo_data:
            return f"❌ Erro: {fluxo_data['erro']}"
        
        tabela = []
        
        # Cabeçalho
        if "data" in fluxo_data:  # Fluxo diário
            tabela.append("=" * 80)
            tabela.append(f"📊 FLUXO DE CAIXA - {fluxo_data['data']}")
            tabela.append("=" * 80)
        elif "mes_nome" in fluxo_data:  # Fluxo mensal
            tabela.append("=" * 80)
            tabela.append(f"📊 FLUXO DE CAIXA - {fluxo_data['mes_nome']}/{fluxo_data['ano']}")
            tabela.append("=" * 80)
        else:  # Fluxo por período
            tabela.append("=" * 80)
            tabela.append(f"📊 FLUXO DE CAIXA - {fluxo_data['data_inicio']} a {fluxo_data['data_fim']}")
            tabela.append("=" * 80)
        
        # Resumo
        tabela.append("")
        tabela.append("📈 RESUMO:")
        tabela.append(f"   Entradas: {fluxo_data['entradas']['quantidade']} transações - {self.formatar_valor(fluxo_data['entradas']['total'])}")
        tabela.append(f"   Saídas: {fluxo_data['saidas']['quantidade']} transações - {self.formatar_valor(fluxo_data['saidas']['total'])}")
        
        if "saldo_dia" in fluxo_data:
            saldo = fluxo_data['saldo_dia']
        elif "saldo_mes" in fluxo_data:
            saldo = fluxo_data['saldo_mes']
        else:
            saldo = fluxo_data['saldo_periodo']
        
        saldo_str = self.formatar_valor(saldo)
        if saldo >= 0:
            tabela.append(f"   Saldo: +{saldo_str} ✅")
        else:
            tabela.append(f"   Saldo: {saldo_str} ❌")
        
        # Entradas
        if fluxo_data['entradas']['transacoes']:
            tabela.append("")
            tabela.append("💰 ENTRADAS (Receitas Recebidas):")
            tabela.append("-" * 80)
            tabela.append(f"{'ID':<8} {'Cliente':<20} {'Descrição':<25} {'Valor':<12} {'Data':<12}")
            tabela.append("-" * 80)
            
            for conta in fluxo_data['entradas']['transacoes']:
                tabela.append(f"{conta['id']:<8} {conta.get('cliente', 'N/A')[:18]:<20} {conta['descricao'][:23]:<25} {self.formatar_valor(conta['valor']):<12} {conta.get('data_recebimento', 'N/A'):<12}")
        else:
            tabela.append("")
            tabela.append("💰 ENTRADAS: Nenhuma transação encontrada")
        
        # Saídas
        if fluxo_data['saidas']['transacoes']:
            tabela.append("")
            tabela.append("💸 SAÍDAS (Despesas Pagas):")
            tabela.append("-" * 80)
            tabela.append(f"{'ID':<8} {'Fornecedor':<20} {'Descrição':<25} {'Valor':<12} {'Data':<12}")
            tabela.append("-" * 80)
            
            for conta in fluxo_data['saidas']['transacoes']:
                tabela.append(f"{conta['id']:<8} {conta.get('fornecedor', 'N/A')[:18]:<20} {conta['descricao'][:23]:<25} {self.formatar_valor(conta['valor']):<12} {conta.get('data_pagamento', 'N/A'):<12}")
        else:
            tabela.append("")
            tabela.append("💸 SAÍDAS: Nenhuma transação encontrada")
        
        tabela.append("")
        tabela.append("=" * 80)
        
        return "\n".join(tabela)
    
    def dados_para_grafico_fluxo_caixa(self, fluxo_data: Dict) -> Dict:
        """
        Prepara dados para geração de gráficos do fluxo de caixa
        
        Args:
            fluxo_data: Dados do fluxo de caixa
            
        Returns:
            Dicionário com dados formatados para gráficos
        """
        if "erro" in fluxo_data:
            return {"erro": fluxo_data["erro"]}
        
        dados_grafico = {
            "titulo": "",
            "valores": {
                "entradas": fluxo_data['entradas']['total'],
                "saidas": fluxo_data['saidas']['total']
            },
            "categorias_entradas": {},
            "categorias_saidas": {},
            "transacoes_diarias": []
        }
        
        # Definir título
        if "data" in fluxo_data:
            dados_grafico["titulo"] = f"Fluxo de Caixa - {fluxo_data['data']}"
        elif "mes_nome" in fluxo_data:
            dados_grafico["titulo"] = f"Fluxo de Caixa - {fluxo_data['mes_nome']}/{fluxo_data['ano']}"
        else:
            dados_grafico["titulo"] = f"Fluxo de Caixa - {fluxo_data['data_inicio']} a {fluxo_data['data_fim']}"
        
        # Categorias (se disponível)
        if "por_categoria" in fluxo_data['entradas']:
            dados_grafico["categorias_entradas"] = fluxo_data['entradas']['por_categoria']
        
        if "por_categoria" in fluxo_data['saidas']:
            dados_grafico["categorias_saidas"] = fluxo_data['saidas']['por_categoria']
        
        # Transações diárias (para gráfico de linha)
        if "mes_nome" in fluxo_data:  # Apenas para fluxo mensal
            transacoes_por_dia = {}
            
            # Agrupar entradas por dia
            for conta in fluxo_data['entradas']['transacoes']:
                data = conta.get('data_recebimento', '')
                if data not in transacoes_por_dia:
                    transacoes_por_dia[data] = {"entradas": 0, "saidas": 0}
                transacoes_por_dia[data]["entradas"] += conta['valor']
            
            # Agrupar saídas por dia
            for conta in fluxo_data['saidas']['transacoes']:
                data = conta.get('data_pagamento', '')
                if data not in transacoes_por_dia:
                    transacoes_por_dia[data] = {"entradas": 0, "saidas": 0}
                transacoes_por_dia[data]["saidas"] += conta['valor']
            
            # Ordenar por data
            for data in sorted(transacoes_por_dia.keys()):
                dados_grafico["transacoes_diarias"].append({
                    "data": data,
                    "entradas": transacoes_por_dia[data]["entradas"],
                    "saidas": transacoes_por_dia[data]["saidas"],
                    "saldo": transacoes_por_dia[data]["entradas"] - transacoes_por_dia[data]["saidas"]
                })
        
        return dados_grafico
    
    def relatorio_fluxo_caixa_completo(self, tipo: str = "mes", **kwargs) -> str:
        """
        Gera relatório completo do fluxo de caixa
        
        Args:
            tipo: "dia", "mes", ou "periodo"
            **kwargs: Parâmetros específicos para cada tipo
            
        Returns:
            String formatada do relatório
        """
        if tipo == "dia":
            data = kwargs.get('data', datetime.now().strftime("%Y-%m-%d"))
            fluxo_data = self.fluxo_caixa_diario(data)
        elif tipo == "mes":
            ano = kwargs.get('ano', datetime.now().year)
            mes = kwargs.get('mes', datetime.now().month)
            fluxo_data = self.fluxo_caixa_mensal(ano, mes)
        elif tipo == "periodo":
            data_inicio = kwargs.get('data_inicio')
            data_fim = kwargs.get('data_fim')
            if not data_inicio or not data_fim:
                return "❌ Erro: Data inicial e final são obrigatórias para relatório por período"
            fluxo_data = self.fluxo_caixa_periodo(data_inicio, data_fim)
        else:
            return "❌ Erro: Tipo de relatório inválido. Use 'dia', 'mes' ou 'periodo'"
        
        # Gerar tabela
        tabela = self.tabela_transacoes_fluxo_caixa(fluxo_data)
        
        # Preparar dados para gráfico
        dados_grafico = self.dados_para_grafico_fluxo_caixa(fluxo_data)
        
        # Adicionar informações sobre gráficos
        relatorio = tabela + "\n\n"
        relatorio += "📊 DADOS PARA GRÁFICOS:\n"
        relatorio += "-" * 40 + "\n"
        relatorio += f"Título: {dados_grafico['titulo']}\n"
        relatorio += f"Total Entradas: {self.formatar_valor(dados_grafico['valores']['entradas'])}\n"
        relatorio += f"Total Saídas: {self.formatar_valor(dados_grafico['valores']['saidas'])}\n"
        
        if dados_grafico['categorias_entradas']:
            relatorio += "\nCategorias de Entradas:\n"
            for categoria, valor in dados_grafico['categorias_entradas'].items():
                relatorio += f"  {categoria}: {self.formatar_valor(valor)}\n"
        
        if dados_grafico['categorias_saidas']:
            relatorio += "\nCategorias de Saídas:\n"
            for categoria, valor in dados_grafico['categorias_saidas'].items():
                relatorio += f"  {categoria}: {self.formatar_valor(valor)}\n"
        
        if dados_grafico['transacoes_diarias']:
            relatorio += f"\nTransações Diárias ({len(dados_grafico['transacoes_diarias'])} dias):\n"
            for transacao in dados_grafico['transacoes_diarias'][:5]:  # Mostrar apenas os primeiros 5 dias
                relatorio += f"  {transacao['data']}: E={self.formatar_valor(transacao['entradas'])}, S={self.formatar_valor(transacao['saidas'])}, Saldo={self.formatar_valor(transacao['saldo'])}\n"
            if len(dados_grafico['transacoes_diarias']) > 5:
                relatorio += f"  ... e mais {len(dados_grafico['transacoes_diarias']) - 5} dias\n"
        
        relatorio += "\n💡 DICA: Use os dados acima para gerar gráficos com Matplotlib ou Plotly!"
        
        return relatorio
