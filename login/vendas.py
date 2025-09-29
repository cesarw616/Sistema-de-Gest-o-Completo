import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class SistemaVendas:
    def __init__(self, arquivo_pedidos: str = "pedidos.json", arquivo_clientes: str = "clientes.json"):
        """
        Inicializa o sistema de vendas
        
        Args:
            arquivo_pedidos: Arquivo para armazenar pedidos
            arquivo_clientes: Arquivo para armazenar clientes
        """
        self.arquivo_pedidos = arquivo_pedidos
        self.arquivo_clientes = arquivo_clientes
        self.pedidos = self.carregar_pedidos()
        self.clientes = self.carregar_clientes()
    
    def carregar_pedidos(self) -> List:
        """Carrega pedidos do arquivo JSON"""
        if os.path.exists(self.arquivo_pedidos):
            try:
                with open(self.arquivo_pedidos, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def carregar_clientes(self) -> Dict:
        """Carrega clientes do arquivo JSON"""
        if os.path.exists(self.arquivo_clientes):
            try:
                with open(self.arquivo_clientes, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def salvar_pedidos(self):
        """Salva pedidos no arquivo JSON"""
        with open(self.arquivo_pedidos, 'w', encoding='utf-8') as arquivo:
            json.dump(self.pedidos, arquivo, indent=4, ensure_ascii=False)
    
    def salvar_clientes(self):
        """Salva clientes no arquivo JSON"""
        with open(self.arquivo_clientes, 'w', encoding='utf-8') as arquivo:
            json.dump(self.clientes, arquivo, indent=4, ensure_ascii=False)
    
    def gerar_codigo_pedido(self) -> str:
        """Gera um código único para o pedido"""
        if not self.pedidos:
            return "PED001"
        
        # Encontra o maior número de pedido existente
        codigos = [int(pedido["codigo"][3:]) for pedido in self.pedidos if pedido["codigo"].startswith("PED")]
        if codigos:
            proximo_numero = max(codigos) + 1
        else:
            proximo_numero = 1
        
        return f"PED{proximo_numero:03d}"
    
    def cadastrar_cliente(self, nome: str, email: str, telefone: str, endereco: str = "", usuario: str = "sistema") -> str:
        """
        Cadastra um novo cliente
        
        Args:
            nome: Nome do cliente
            email: Email do cliente
            telefone: Telefone do cliente
            endereco: Endereço do cliente
            usuario: Usuário que está cadastrando
            
        Returns:
            ID do cliente criado ou None se erro
        """
        if not nome or not email or not telefone:
            print("❌ Erro: Dados do cliente inválidos!")
            return None
        
        # Verifica se já existe cliente com mesmo email
        for cliente_id, dados in self.clientes.items():
            if dados["email"].lower() == email.lower():
                print("❌ Erro: Já existe um cliente com este email!")
                return None
        
        cliente_id = str(len(self.clientes) + 1)
        
        self.clientes[cliente_id] = {
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "endereco": endereco,
            "data_cadastro": time.strftime("%Y-%m-%d %H:%M:%S"),
            "usuario_cadastro": usuario,
            "ativo": True
        }
        
        self.salvar_clientes()
        print(f"✅ Cliente {nome} cadastrado com ID {cliente_id}!")
        return cliente_id
    
    def listar_clientes(self, apenas_ativos: bool = True) -> List[Dict]:
        """
        Lista clientes cadastrados
        
        Args:
            apenas_ativos: Se deve listar apenas clientes ativos
            
        Returns:
            Lista de clientes
        """
        clientes_lista = []
        for cliente_id, dados in self.clientes.items():
            if apenas_ativos and not dados.get("ativo", True):
                continue
            
            cliente = {
                "id": cliente_id,
                **dados
            }
            clientes_lista.append(cliente)
        
        return sorted(clientes_lista, key=lambda x: x["nome"])
    
    def buscar_cliente(self, termo: str) -> List[Dict]:
        """
        Busca cliente por ID, nome ou email
        
        Args:
            termo: Termo de busca
            
        Returns:
            Lista de clientes encontrados
        """
        resultados = []
        termo_lower = termo.lower()
        
        for cliente_id, dados in self.clientes.items():
            if (termo_lower in cliente_id.lower() or 
                termo_lower in dados["nome"].lower() or 
                termo_lower in dados["email"].lower()):
                
                cliente = {
                    "id": cliente_id,
                    **dados
                }
                resultados.append(cliente)
        
        return resultados
    
    def criar_pedido(self, cliente_id: str, produtos: List[Dict], observacoes: str = "", usuario: str = "sistema") -> str:
        """
        Cria um novo pedido
        
        Args:
            cliente_id: ID do cliente
            produtos: Lista de produtos com quantidade e preço
            observacoes: Observações do pedido
            usuario: Usuário que está criando o pedido
            
        Returns:
            Código do pedido criado ou None se erro
        """
        if cliente_id not in self.clientes:
            print("❌ Erro: Cliente não encontrado!")
            return None
        
        if not produtos:
            print("❌ Erro: Pedido deve ter pelo menos um produto!")
            return None
        
        # Calcula totais
        subtotal = sum(item["quantidade"] * item["preco_unitario"] for item in produtos)
        total = subtotal
        
        codigo_pedido = self.gerar_codigo_pedido()
        
        pedido = {
            "codigo": codigo_pedido,
            "cliente_id": cliente_id,
            "cliente_nome": self.clientes[cliente_id]["nome"],
            "produtos": produtos,
            "subtotal": subtotal,
            "total": total,
            "observacoes": observacoes,
            "status": "pendente",
            "usuario_criacao": usuario,
            "data_criacao": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data_atualizacao": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.pedidos.append(pedido)
        self.salvar_pedidos()
        
        print(f"✅ Pedido {codigo_pedido} criado para {self.clientes[cliente_id]['nome']}!")
        print(f"💰 Total: R$ {total:.2f}")
        
        return codigo_pedido
    
    def listar_pedidos(self, status: str = None) -> List[Dict]:
        """
        Lista pedidos
        
        Args:
            status: Filtro por status (pendente, aprovado, cancelado, finalizado)
            
        Returns:
            Lista de pedidos
        """
        if status:
            return [pedido for pedido in self.pedidos if pedido["status"] == status]
        return self.pedidos
    
    def buscar_pedido(self, termo: str) -> List[Dict]:
        """
        Busca pedido por código ou nome do cliente
        
        Args:
            termo: Termo de busca
            
        Returns:
            Lista de pedidos encontrados
        """
        resultados = []
        termo_lower = termo.lower()
        
        for pedido in self.pedidos:
            if (termo_lower in pedido["codigo"].lower() or 
                termo_lower in pedido["cliente_nome"].lower()):
                resultados.append(pedido)
        
        return resultados
    
    def atualizar_status_pedido(self, codigo_pedido: str, novo_status: str, usuario: str = "sistema") -> bool:
        """
        Atualiza o status de um pedido
        
        Args:
            codigo_pedido: Código do pedido
            novo_status: Novo status
            usuario: Usuário que está atualizando
            
        Returns:
            True se sucesso, False se erro
        """
        for pedido in self.pedidos:
            if pedido["codigo"] == codigo_pedido:
                pedido["status"] = novo_status
                pedido["data_atualizacao"] = time.strftime("%Y-%m-%d %H:%M:%S")
                pedido["usuario_atualizacao"] = usuario
                
                self.salvar_pedidos()
                print(f"✅ Status do pedido {codigo_pedido} atualizado para '{novo_status}'!")
                return True
        
        print("❌ Erro: Pedido não encontrado!")
        return False
    
    def gerar_recibo_pdf(self, codigo_pedido: str, caminho_saida: str = "recibos") -> str:
        """
        Gera um recibo em PDF
        
        Args:
            codigo_pedido: Código do pedido
            caminho_saida: Pasta para salvar o PDF
            
        Returns:
            Caminho do arquivo PDF gerado
        """
        # Encontra o pedido
        pedido = None
        for p in self.pedidos:
            if p["codigo"] == codigo_pedido:
                pedido = p
                break
        
        if not pedido:
            print("❌ Erro: Pedido não encontrado!")
            return None
        
        # Cria pasta se não existir
        if not os.path.exists(caminho_saida):
            os.makedirs(caminho_saida)
        
        # Nome do arquivo
        nome_arquivo = f"recibo_{codigo_pedido}_{time.strftime('%Y%m%d_%H%M%S')}.pdf"
        caminho_completo = os.path.join(caminho_saida, nome_arquivo)
        
        # Cria o documento PDF
        doc = SimpleDocTemplate(caminho_completo, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Título
        story.append(Paragraph("RECIBO DE VENDA", title_style))
        story.append(Spacer(1, 20))
        
        # Informações do pedido
        info_pedido = [
            ["Código do Pedido:", pedido["codigo"]],
            ["Data:", pedido["data_criacao"]],
            ["Status:", pedido["status"].upper()],
            ["", ""]
        ]
        
        t_info = Table(info_pedido, colWidths=[2*inch, 4*inch])
        t_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 20))
        
        # Informações do cliente
        cliente = self.clientes[pedido["cliente_id"]]
        story.append(Paragraph("DADOS DO CLIENTE", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        info_cliente = [
            ["Nome:", cliente["nome"]],
            ["Email:", cliente["email"]],
            ["Telefone:", cliente["telefone"]],
            ["Endereço:", cliente.get("endereco", "Não informado")],
            ["", ""]
        ]
        
        t_cliente = Table(info_cliente, colWidths=[1.5*inch, 4.5*inch])
        t_cliente.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_cliente)
        story.append(Spacer(1, 20))
        
        # Produtos
        story.append(Paragraph("ITENS DO PEDIDO", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Cabeçalho da tabela
        dados_produtos = [["Produto", "Quantidade", "Preço Unit.", "Subtotal"]]
        
        # Dados dos produtos
        for item in pedido["produtos"]:
            dados_produtos.append([
                item["nome"],
                str(item["quantidade"]),
                f"R$ {item['preco_unitario']:.2f}",
                f"R$ {item['quantidade'] * item['preco_unitario']:.2f}"
            ])
        
        # Linha de total
        dados_produtos.append(["", "", "TOTAL:", f"R$ {pedido['total']:.2f}"])
        
        t_produtos = Table(dados_produtos, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        t_produtos.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_produtos)
        story.append(Spacer(1, 20))
        
        # Observações
        if pedido["observacoes"]:
            story.append(Paragraph("OBSERVAÇÕES", styles['Heading2']))
            story.append(Spacer(1, 10))
            story.append(Paragraph(pedido["observacoes"], styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Rodapé
        story.append(Spacer(1, 30))
        story.append(Paragraph("Assinatura: _________________________", styles['Normal']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Data: {time.strftime('%d/%m/%Y')}", styles['Normal']))
        
        # Gera o PDF
        doc.build(story)
        
        print(f"✅ Recibo gerado: {caminho_completo}")
        return caminho_completo
    
    def relatorio_vendas(self, data_inicio: str = None, data_fim: str = None) -> Dict:
        """
        Gera relatório de vendas
        
        Args:
            data_inicio: Data de início (YYYY-MM-DD)
            data_fim: Data de fim (YYYY-MM-DD)
            
        Returns:
            Dicionário com dados do relatório
        """
        pedidos_filtrados = self.pedidos
        
        # Filtra por data se especificado
        if data_inicio or data_fim:
            pedidos_filtrados = []
            for pedido in self.pedidos:
                data_pedido = pedido["data_criacao"][:10]  # Pega apenas a data
                
                if data_inicio and data_pedido < data_inicio:
                    continue
                if data_fim and data_pedido > data_fim:
                    continue
                
                pedidos_filtrados.append(pedido)
        
        # Calcula estatísticas
        total_pedidos = len(pedidos_filtrados)
        total_vendas = sum(pedido["total"] for pedido in pedidos_filtrados)
        pedidos_finalizados = len([p for p in pedidos_filtrados if p["status"] == "finalizado"])
        pedidos_pendentes = len([p for p in pedidos_filtrados if p["status"] == "pendente"])
        
        # Produtos mais vendidos
        produtos_vendidos = {}
        for pedido in pedidos_filtrados:
            for item in pedido["produtos"]:
                nome_produto = item["nome"]
                if nome_produto not in produtos_vendidos:
                    produtos_vendidos[nome_produto] = {"quantidade": 0, "valor": 0}
                produtos_vendidos[nome_produto]["quantidade"] += item["quantidade"]
                produtos_vendidos[nome_produto]["valor"] += item["quantidade"] * item["preco_unitario"]
        
        # Top 5 produtos
        top_produtos = sorted(produtos_vendidos.items(), 
                            key=lambda x: x[1]["quantidade"], 
                            reverse=True)[:5]
        
        return {
            "total_pedidos": total_pedidos,
            "total_vendas": total_vendas,
            "pedidos_finalizados": pedidos_finalizados,
            "pedidos_pendentes": pedidos_pendentes,
            "produtos_vendidos": produtos_vendidos,
            "top_produtos": top_produtos,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "data_relatorio": time.strftime("%Y-%m-%d %H:%M:%S")
        }
