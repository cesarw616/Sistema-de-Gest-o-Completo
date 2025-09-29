import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

class SistemaEstoque:
    def __init__(self, arquivo_produtos: str = "produtos.json", arquivo_movimentos: str = "movimentos.json"):
        """
        Inicializa o sistema de estoque
        
        Args:
            arquivo_produtos: Arquivo para armazenar produtos
            arquivo_movimentos: Arquivo para armazenar movimentações
        """
        self.arquivo_produtos = arquivo_produtos
        self.arquivo_movimentos = arquivo_movimentos
        self.produtos = self.carregar_produtos()
        self.movimentos = self.carregar_movimentos()
    
    def carregar_produtos(self) -> Dict:
        """Carrega produtos do arquivo JSON"""
        if os.path.exists(self.arquivo_produtos):
            try:
                with open(self.arquivo_produtos, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def carregar_movimentos(self) -> List:
        """Carrega movimentações do arquivo JSON"""
        if os.path.exists(self.arquivo_movimentos):
            try:
                with open(self.arquivo_movimentos, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def salvar_produtos(self):
        """Salva produtos no arquivo JSON"""
        with open(self.arquivo_produtos, 'w', encoding='utf-8') as arquivo:
            json.dump(self.produtos, arquivo, indent=4, ensure_ascii=False)
    
    def salvar_movimentos(self):
        """Salva movimentações no arquivo JSON"""
        with open(self.arquivo_movimentos, 'w', encoding='utf-8') as arquivo:
            json.dump(self.movimentos, arquivo, indent=4, ensure_ascii=False)
    
    def gerar_codigo_produto(self) -> str:
        """Gera um código único para o produto"""
        if not self.produtos:
            return "PROD001"
        
        # Encontra o maior número de produto existente
        codigos = [int(codigo[4:]) for codigo in self.produtos.keys() if codigo.startswith("PROD")]
        if codigos:
            proximo_numero = max(codigos) + 1
        else:
            proximo_numero = 1
        
        return f"PROD{proximo_numero:03d}"
    
    def cadastrar_produto(self, nome: str, categoria: str, preco: float, estoque_minimo: int = 5, usuario: str = "sistema") -> str:
        """
        Cadastra um novo produto
        
        Args:
            nome: Nome do produto
            categoria: Categoria do produto
            preco: Preço unitário
            estoque_minimo: Estoque mínimo para alerta
            usuario: Usuário que está cadastrando
            
        Returns:
            Código do produto criado ou None se erro
        """
        if not nome or not categoria or preco < 0:
            print("❌ Erro: Dados do produto inválidos!")
            return None
        
        # Verifica se já existe produto com mesmo nome
        for codigo, dados in self.produtos.items():
            if dados["nome"].lower() == nome.lower():
                print("❌ Erro: Já existe um produto com este nome!")
                return None
        
        codigo = self.gerar_codigo_produto()
        
        self.produtos[codigo] = {
            "nome": nome,
            "categoria": categoria,
            "preco": preco,
            "quantidade": 0,
            "estoque_minimo": estoque_minimo,
            "data_cadastro": time.strftime("%Y-%m-%d %H:%M:%S"),
            "usuario_cadastro": usuario,
            "ativo": True
        }
        
        self.salvar_produtos()
        print(f"✅ Produto {nome} cadastrado com código {codigo}!")
        return codigo
    
    def registrar_movimento(self, codigo_produto: str, tipo: str, quantidade: int, observacao: str = "", usuario: str = "sistema") -> bool:
        """
        Registra uma movimentação de estoque
        
        Args:
            codigo_produto: Código do produto
            tipo: "entrada" ou "saida"
            quantidade: Quantidade movimentada
            observacao: Observação sobre a movimentação
            usuario: Usuário que fez a movimentação
            
        Returns:
            True se sucesso, False se erro
        """
        if codigo_produto not in self.produtos:
            print("❌ Erro: Produto não encontrado!")
            return False
        
        if tipo not in ["entrada", "saida"]:
            print("❌ Erro: Tipo deve ser 'entrada' ou 'saida'!")
            return False
        
        if quantidade <= 0:
            print("❌ Erro: Quantidade deve ser maior que zero!")
            return False
        
        # Verifica se há estoque suficiente para saída
        if tipo == "saida" and self.produtos[codigo_produto]["quantidade"] < quantidade:
            print("❌ Erro: Estoque insuficiente!")
            print(f"Estoque atual: {self.produtos[codigo_produto]['quantidade']}")
            return False
        
        # Atualiza quantidade no produto
        if tipo == "entrada":
            self.produtos[codigo_produto]["quantidade"] += quantidade
        else:  # saida
            self.produtos[codigo_produto]["quantidade"] -= quantidade
        
        # Registra o movimento
        movimento = {
            "id": len(self.movimentos) + 1,
            "codigo_produto": codigo_produto,
            "nome_produto": self.produtos[codigo_produto]["nome"],
            "tipo": tipo,
            "quantidade": quantidade,
            "estoque_anterior": self.produtos[codigo_produto]["quantidade"] - quantidade if tipo == "entrada" else self.produtos[codigo_produto]["quantidade"] + quantidade,
            "estoque_atual": self.produtos[codigo_produto]["quantidade"],
            "observacao": observacao,
            "usuario": usuario,
            "data_hora": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.movimentos.append(movimento)
        
        # Salva alterações
        self.salvar_produtos()
        self.salvar_movimentos()
        
        emoji = "📦" if tipo == "entrada" else "📤"
        print(f"{emoji} {tipo.capitalize()} registrada: {quantidade} unidades de {self.produtos[codigo_produto]['nome']}")
        print(f"Estoque atual: {self.produtos[codigo_produto]['quantidade']} unidades")
        
        # Alerta de estoque baixo
        if self.produtos[codigo_produto]["quantidade"] <= self.produtos[codigo_produto]["estoque_minimo"]:
            print(f"⚠️ ALERTA: Estoque baixo! Mínimo: {self.produtos[codigo_produto]['estoque_minimo']}")
        
        return True
    
    def listar_produtos(self, apenas_ativos: bool = True) -> List[Dict]:
        """
        Lista produtos cadastrados
        
        Args:
            apenas_ativos: Se deve listar apenas produtos ativos
            
        Returns:
            Lista de produtos
        """
        produtos_lista = []
        for codigo, dados in self.produtos.items():
            if apenas_ativos and not dados.get("ativo", True):
                continue
            
            produto = {
                "codigo": codigo,
                **dados
            }
            produtos_lista.append(produto)
        
        return sorted(produtos_lista, key=lambda x: x["nome"])
    
    def buscar_produto(self, termo: str) -> List[Dict]:
        """
        Busca produto por código ou nome
        
        Args:
            termo: Termo de busca (código ou nome)
            
        Returns:
            Lista de produtos encontrados
        """
        resultados = []
        termo_lower = termo.lower()
        
        for codigo, dados in self.produtos.items():
            if (termo_lower in codigo.lower() or 
                termo_lower in dados["nome"].lower() or 
                termo_lower in dados["categoria"].lower()):
                
                produto = {
                    "codigo": codigo,
                    **dados
                }
                resultados.append(produto)
        
        return resultados
    
    def obter_produtos_estoque_baixo(self) -> List[Dict]:
        """
        Obtém produtos com estoque baixo
        
        Returns:
            Lista de produtos com estoque baixo
        """
        produtos_baixo = []
        for codigo, dados in self.produtos.items():
            if dados.get("ativo", True) and dados["quantidade"] <= dados["estoque_minimo"]:
                produto = {
                    "codigo": codigo,
                    **dados
                }
                produtos_baixo.append(produto)
        
        return sorted(produtos_baixo, key=lambda x: x["quantidade"])
    
    def relatorio_estoque(self) -> Dict:
        """
        Gera relatório geral do estoque
        
        Returns:
            Dicionário com dados do relatório
        """
        total_produtos = len([p for p in self.produtos.values() if p.get("ativo", True)])
        total_itens = sum(p["quantidade"] for p in self.produtos.values() if p.get("ativo", True))
        valor_total = sum(p["quantidade"] * p["preco"] for p in self.produtos.values() if p.get("ativo", True))
        produtos_zerados = len([p for p in self.produtos.values() if p.get("ativo", True) and p["quantidade"] == 0])
        produtos_baixo = len(self.obter_produtos_estoque_baixo())
        
        categorias = {}
        for dados in self.produtos.values():
            if dados.get("ativo", True):
                cat = dados["categoria"]
                if cat not in categorias:
                    categorias[cat] = {"produtos": 0, "itens": 0, "valor": 0}
                categorias[cat]["produtos"] += 1
                categorias[cat]["itens"] += dados["quantidade"]
                categorias[cat]["valor"] += dados["quantidade"] * dados["preco"]
        
        return {
            "total_produtos": total_produtos,
            "total_itens": total_itens,
            "valor_total": valor_total,
            "produtos_zerados": produtos_zerados,
            "produtos_estoque_baixo": produtos_baixo,
            "categorias": categorias,
            "data_relatorio": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def relatorio_movimentos(self, limite: int = 50) -> List[Dict]:
        """
        Obtém últimas movimentações
        
        Args:
            limite: Número máximo de movimentações
            
        Returns:
            Lista das últimas movimentações
        """
        # Ordena por data decrescente e pega os últimos
        movimentos_ordenados = sorted(self.movimentos, 
                                     key=lambda x: x["data_hora"], 
                                     reverse=True)
        return movimentos_ordenados[:limite]
    
    def excluir_produto(self, codigo_produto: str, usuario: str = "sistema") -> bool:
        """
        Exclui (desativa) um produto
        
        Args:
            codigo_produto: Código do produto
            usuario: Usuário que está excluindo
            
        Returns:
            True se sucesso, False se erro
        """
        if codigo_produto not in self.produtos:
            print("❌ Erro: Produto não encontrado!")
            return False
        
        self.produtos[codigo_produto]["ativo"] = False
        self.salvar_produtos()
        
        print(f"✅ Produto {self.produtos[codigo_produto]['nome']} desativado!")
        return True
