import hashlib
import json
import os
import time
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Optional
from estoque import SistemaEstoque
from vendas import SistemaVendas
from financeiro import SistemaFinanceiro

class SistemaLogin:
    def __init__(self, arquivo_usuarios: str = "usuarios.json"):
        """
        Inicializa o sistema de login
        
        Args:
            arquivo_usuarios: Nome do arquivo para armazenar os usuários
        """
        self.arquivo_usuarios = arquivo_usuarios
        self.usuario_atual = None
        self.usuarios = self.carregar_usuarios()
        self.chave_mestre = self.obter_chave_mestre()
        self.estoque = SistemaEstoque()
        self.vendas = SistemaVendas()
        self.financeiro = SistemaFinanceiro()
    
    def obter_chave_mestre(self) -> bytes:
        """
        Obtém ou cria a chave mestra para criptografia
        
        Returns:
            Chave mestra em bytes
        """
        arquivo_chave = "chave_mestra.key"
        
        if os.path.exists(arquivo_chave):
            # Carrega chave existente
            with open(arquivo_chave, "rb") as f:
                return f.read()
        else:
            # Cria nova chave mestra
            chave = Fernet.generate_key()
            with open(arquivo_chave, "wb") as f:
                f.write(chave)
            return chave
    
    def gerar_salt(self) -> bytes:
        """
        Gera um salt único para cada senha
        
        Returns:
            Salt em bytes
        """
        return os.urandom(16)
    
    def derivar_chave(self, senha: str, salt: bytes) -> bytes:
        """
        Deriva uma chave da senha usando PBKDF2
        
        Args:
            senha: Senha em texto plano
            salt: Salt único
            
        Returns:
            Chave derivada em bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(senha.encode()))
    
    def criptografar_senha(self, senha: str) -> str:
        """
        Criptografa uma senha usando salt único e PBKDF2
        
        Args:
            senha: Senha em texto plano
            
        Returns:
            String criptografada (salt + hash)
        """
        salt = self.gerar_salt()
        chave_derivada = self.derivar_chave(senha, salt)
        
        # Combina salt + hash para armazenamento
        return base64.urlsafe_b64encode(salt + chave_derivada).decode()
    
    def verificar_senha(self, senha: str, senha_criptografada: str) -> bool:
        """
        Verifica se uma senha corresponde à versão criptografada
        
        Args:
            senha: Senha em texto plano
            senha_criptografada: Senha criptografada
            
        Returns:
            True se a senha está correta
        """
        try:
            # Decodifica a string criptografada
            dados = base64.urlsafe_b64decode(senha_criptografada.encode())
            
            # Extrai salt e hash
            salt = dados[:16]
            hash_armazenado = dados[16:]
            
            # Deriva chave da senha fornecida
            chave_derivada = self.derivar_chave(senha, salt)
            
            # Compara os hashes
            return hash_armazenado == chave_derivada
        except:
            return False
    
    def hash_senha(self, senha: str) -> str:
        """
        Criptografa uma senha usando PBKDF2 com salt único
        
        Args:
            senha: Senha em texto plano
            
        Returns:
            Senha criptografada
        """
        return self.criptografar_senha(senha)
    
    def carregar_usuarios(self) -> Dict:
        """
        Carrega os usuários do arquivo JSON
        
        Returns:
            Dicionário com os usuários
        """
        if os.path.exists(self.arquivo_usuarios):
            try:
                with open(self.arquivo_usuarios, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def salvar_usuarios(self):
        """Salva os usuários no arquivo JSON"""
        with open(self.arquivo_usuarios, 'w', encoding='utf-8') as arquivo:
            json.dump(self.usuarios, arquivo, indent=4, ensure_ascii=False)
    
    def cadastrar_usuario(self, usuario: str, senha: str, email: str = "", tipo_usuario: str = "cliente") -> bool:
        """
        Cadastra um novo usuário
        
        Args:
            usuario: Nome do usuário
            senha: Senha do usuário
            email: Email do usuário (opcional)
            tipo_usuario: Tipo do usuário (cliente, funcionario, admin)
            
        Returns:
            True se o cadastro foi bem-sucedido, False caso contrário
        """
        if usuario in self.usuarios:
            print("❌ Erro: Usuário já existe!")
            return False
        
        if len(senha) < 6:
            print("❌ Erro: A senha deve ter pelo menos 6 caracteres!")
            return False
        
        # Valida o tipo de usuário
        tipos_validos = ["cliente", "funcionario", "admin"]
        if tipo_usuario not in tipos_validos:
            print("❌ Erro: Tipo de usuário inválido! Use: cliente, funcionario ou admin")
            return False
        
        # Cria o hash da senha
        senha_hash = self.hash_senha(senha)
        
        # Adiciona o usuário
        self.usuarios[usuario] = {
            "senha": senha_hash,
            "email": email,
            "tipo": tipo_usuario,
            "data_cadastro": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ultimo_login": None,
            "ativo": True
        }
        
        # Salva no arquivo
        self.salvar_usuarios()
        print(f"✅ Usuário {tipo_usuario} cadastrado com sucesso!")
        return True
    
    def fazer_login(self, usuario: str, senha: str) -> bool:
        """
        Realiza o login do usuário
        
        Args:
            usuario: Nome do usuário
            senha: Senha do usuário
            
        Returns:
            True se o login foi bem-sucedido, False caso contrário
        """
        if usuario not in self.usuarios:
            print("❌ Erro: Usuário não encontrado!")
            return False
        
        if self.verificar_senha(senha, self.usuarios[usuario]["senha"]):
            # Verifica se o usuário está ativo
            if not self.usuarios[usuario].get("ativo", True):
                print("❌ Erro: Usuário desativado! Entre em contato com o administrador.")
                return False
            
            self.usuario_atual = usuario
            self.usuarios[usuario]["ultimo_login"] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.salvar_usuarios()
            
            tipo_usuario = self.usuarios[usuario].get("tipo", "cliente")
            print(f"✅ Login realizado com sucesso! Bem-vindo, {usuario} ({tipo_usuario})!")
            return True
        else:
            print("❌ Erro: Senha incorreta!")
            return False
    
    def fazer_logout(self):
        """Realiza o logout do usuário atual"""
        if self.usuario_atual:
            print(f"👋 Logout realizado. Até logo, {self.usuario_atual}!")
            self.usuario_atual = None
        else:
            print("❌ Nenhum usuário logado!")
    
    def alterar_senha(self, senha_atual: str, nova_senha: str) -> bool:
        """
        Altera a senha do usuário logado
        
        Args:
            senha_atual: Senha atual
            nova_senha: Nova senha
            
        Returns:
            True se a alteração foi bem-sucedida, False caso contrário
        """
        if not self.usuario_atual:
            print("❌ Erro: Nenhum usuário logado!")
            return False
        
        if len(nova_senha) < 6:
            print("❌ Erro: A nova senha deve ter pelo menos 6 caracteres!")
            return False
        
        if not self.verificar_senha(senha_atual, self.usuarios[self.usuario_atual]["senha"]):
            print("❌ Erro: Senha atual incorreta!")
            return False
        
        self.usuarios[self.usuario_atual]["senha"] = self.hash_senha(nova_senha)
        self.salvar_usuarios()
        print("✅ Senha alterada com sucesso!")
        return True
    
    def obter_info_usuario(self) -> Optional[Dict]:
        """
        Obtém informações do usuário logado
        
        Returns:
            Dicionário com informações do usuário ou None se não estiver logado
        """
        if not self.usuario_atual:
            print("❌ Erro: Nenhum usuário logado!")
            return None
        
        return self.usuarios[self.usuario_atual]
    
    def listar_usuarios(self) -> list:
        """
        Lista todos os usuários cadastrados (apenas nomes)
        
        Returns:
            Lista com os nomes dos usuários
        """
        return list(self.usuarios.keys())
    
    def esta_logado(self) -> bool:
        """
        Verifica se há um usuário logado
        
        Returns:
            True se há um usuário logado, False caso contrário
        """
        return self.usuario_atual is not None
    
    def obter_tipo_usuario(self) -> str:
        """
        Obtém o tipo do usuário logado
        
        Returns:
            Tipo do usuário ou "desconhecido" se não estiver logado
        """
        if not self.usuario_atual:
            return "desconhecido"
        return self.usuarios[self.usuario_atual].get("tipo", "cliente")
    
    def tem_permissao(self, tipo_necessario: str) -> bool:
        """
        Verifica se o usuário logado tem permissão para acessar funcionalidades do tipo especificado
        
        Args:
            tipo_necessario: Tipo mínimo necessário (cliente, funcionario, admin)
            
        Returns:
            True se tem permissão, False caso contrário
        """
        if not self.usuario_atual:
            return False
        
        hierarquia = {"cliente": 1, "funcionario": 2, "admin": 3}
        tipo_atual = self.obter_tipo_usuario()
        
        return hierarquia.get(tipo_atual, 0) >= hierarquia.get(tipo_necessario, 0)
    
    def listar_usuarios_por_tipo(self, tipo: str = None) -> list:
        """
        Lista usuários por tipo
        
        Args:
            tipo: Tipo específico para filtrar (opcional)
            
        Returns:
            Lista de usuários do tipo especificado
        """
        if tipo:
            return [usuario for usuario, dados in self.usuarios.items() 
                   if dados.get("tipo") == tipo]
        return list(self.usuarios.keys())
    
    def desativar_usuario(self, usuario: str) -> bool:
        """
        Desativa um usuário (apenas admin pode fazer isso)
        
        Args:
            usuario: Nome do usuário a ser desativado
            
        Returns:
            True se foi desativado com sucesso
        """
        if not self.tem_permissao("admin"):
            print("❌ Erro: Apenas administradores podem desativar usuários!")
            return False
        
        if usuario not in self.usuarios:
            print("❌ Erro: Usuário não encontrado!")
            return False
        
        self.usuarios[usuario]["ativo"] = False
        self.salvar_usuarios()
        print(f"✅ Usuário {usuario} desativado com sucesso!")
        return True
    
    def ativar_usuario(self, usuario: str) -> bool:
        """
        Ativa um usuário (apenas admin pode fazer isso)
        
        Args:
            usuario: Nome do usuário a ser ativado
            
        Returns:
            True se foi ativado com sucesso
        """
        if not self.tem_permissao("admin"):
            print("❌ Erro: Apenas administradores podem ativar usuários!")
            return False
        
        if usuario not in self.usuarios:
            print("❌ Erro: Usuário não encontrado!")
            return False
        
        self.usuarios[usuario]["ativo"] = True
        self.salvar_usuarios()
        print(f"✅ Usuário {usuario} ativado com sucesso!")
        return True

def exibir_menu_principal():
    """Exibe o menu principal do sistema"""
    print("\n" + "="*50)
    print("🔐 SISTEMA DE LOGIN E SENHA")
    print("="*50)
    print("1. Cadastrar novo usuário")
    print("2. Fazer login")
    print("3. Sair")
    print("="*50)

def exibir_menu_usuario(sistema):
    """Exibe o menu do usuário logado baseado no tipo"""
    tipo_usuario = sistema.obter_tipo_usuario()
    
    print("\n" + "="*50)
    print(f"👤 MENU DO {tipo_usuario.upper()}")
    print("="*50)
    print("1. Ver informações da conta")
    print("2. Alterar senha")
    
    opcao_atual = 3
    
    # Menu de estoque para funcionários e administradores
    if sistema.tem_permissao("funcionario"):
        print(f"{opcao_atual}. 📦 Gerenciar Estoque")
        opcao_atual += 1
        print(f"   └─ Cadastrar produtos, entradas e saídas")
        print(f"{opcao_atual}. 📊 Relatórios de Estoque")
        opcao_atual += 1
        print(f"   └─ Consultar estoque e movimentações")
    
    # Menu de vendas para funcionários e administradores
    if sistema.tem_permissao("funcionario"):
        print(f"{opcao_atual}. 🛒 Gerenciar Vendas")
        opcao_atual += 1
        print(f"   └─ Criar pedidos e gerenciar clientes")
        print(f"{opcao_atual}. 📋 Relatórios de Vendas")
        opcao_atual += 1
        print(f"   └─ Consultar vendas e gerar recibos")
    
    # Menu específico para funcionários (usuários)
    if sistema.tem_permissao("funcionario"):
        print(f"{opcao_atual}. Gerenciar clientes")
        opcao_atual += 1
        print(f"{opcao_atual}. Relatórios básicos")
        opcao_atual += 1
    
    # Menu específico para administradores
    if sistema.tem_permissao("admin"):
        print(f"{opcao_atual}. Gerenciar usuários")
        opcao_atual += 1
        print(f"{opcao_atual}. Relatórios avançados")
        opcao_atual += 1
        print(f"{opcao_atual}. Configurações do sistema")
        opcao_atual += 1
    
    # Menu financeiro para funcionários e administradores
    if sistema.tem_permissao("funcionario"):
        print(f"{opcao_atual}. 💰 Gerenciar Financeiro")
        opcao_atual += 1
        print(f"   └─ Contas a pagar e receber")
        print(f"{opcao_atual}. 📊 Relatórios Financeiros")
        opcao_atual += 1
        print(f"   └─ Análise financeira completa")
    
    print(f"{opcao_atual}. Fazer logout")
    opcao_atual += 1
    print(f"{opcao_atual}. Voltar ao menu principal")
    print("="*50)

def main():
    """Função principal do programa"""
    sistema = SistemaLogin()
    
    while True:
        if not sistema.esta_logado():
            exibir_menu_principal()
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                print("\n📝 CADASTRO DE USUÁRIO")
                print("-" * 30)
                usuario = input("Digite o nome de usuário: ").strip()
                senha = input("Digite a senha: ").strip()
                email = input("Digite o email (opcional): ").strip()
                
                print("\n👥 TIPOS DE USUÁRIO:")
                print("1. Cliente")
                print("2. Funcionário")
                print("3. Administrador")
                tipo_opcao = input("Escolha o tipo de usuário (1-3): ").strip()
                
                # Mapeia a opção para o tipo
                tipos = {"1": "cliente", "2": "funcionario", "3": "admin"}
                tipo_usuario = tipos.get(tipo_opcao, "cliente")
                
                if usuario and senha:
                    sistema.cadastrar_usuario(usuario, senha, email, tipo_usuario)
                else:
                    print("❌ Erro: Usuário e senha são obrigatórios!")
            
            elif opcao == "2":
                print("\n🔑 LOGIN")
                print("-" * 30)
                usuario = input("Digite o nome de usuário: ").strip()
                senha = input("Digite a senha: ").strip()
                
                if usuario and senha:
                    sistema.fazer_login(usuario, senha)
                else:
                    print("❌ Erro: Usuário e senha são obrigatórios!")
            
            elif opcao == "3":
                print("👋 Obrigado por usar o sistema!")
                break
            
            else:
                print("❌ Opção inválida!")
        
        else:
            exibir_menu_usuario(sistema)
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                print("\n📋 INFORMAÇÕES DA CONTA")
                print("=" * 40)
                info = sistema.obter_info_usuario()
                if info:
                    print(f"👤 Nome de usuário: {sistema.usuario_atual}")
                    print(f"👥 Tipo: {info.get('tipo', 'cliente').upper()}")
                    print(f"📧 Email: {info.get('email', 'Não informado')}")
                    print(f"📅 Data de cadastro: {info.get('data_cadastro', 'Não informado')}")
                    print(f"🕒 Último login: {info.get('ultimo_login', 'Primeiro login')}")
                    print(f"🟢 Status: {'Ativo' if info.get('ativo', True) else 'Inativo'}")
                    
                    # Calcular tempo desde o cadastro
                    if info.get('data_cadastro'):
                        try:
                            from datetime import datetime
                            data_cadastro = datetime.strptime(info['data_cadastro'], "%Y-%m-%d %H:%M:%S")
                            data_atual = datetime.now()
                            dias_cadastro = (data_atual - data_cadastro).days
                            print(f"⏱️  Conta criada há: {dias_cadastro} dias")
                        except:
                            pass
                    
                    # Mostrar se é o primeiro login
                    if info.get('ultimo_login') is None:
                        print("🎉 Esta é sua primeira vez no sistema!")
                    else:
                        print("✅ Conta ativa e funcionando")
                    
                    print("=" * 40)
            
            elif opcao == "2":
                print("\n🔒 ALTERAR SENHA")
                print("-" * 30)
                senha_atual = input("Digite a senha atual: ").strip()
                nova_senha = input("Digite a nova senha: ").strip()
                confirmar_senha = input("Confirme a nova senha: ").strip()
                
                if nova_senha == confirmar_senha:
                    sistema.alterar_senha(senha_atual, nova_senha)
                else:
                    print("❌ Erro: As senhas não coincidem!")
            
            # Funcionalidades de estoque (opção 3) - Gerenciar Estoque
            elif opcao == "3" and sistema.tem_permissao("funcionario"):
                menu_gerenciar_estoque(sistema)
            
            # Funcionalidades de estoque (opção 4) - Relatórios de Estoque  
            elif opcao == "4" and sistema.tem_permissao("funcionario"):
                menu_relatorios_estoque(sistema)
            
            # Funcionalidades de vendas (opção 5) - Gerenciar Vendas
            elif opcao == "5" and sistema.tem_permissao("funcionario"):
                menu_gerenciar_vendas(sistema)
            
            # Funcionalidades de vendas (opção 6) - Relatórios de Vendas
            elif opcao == "6" and sistema.tem_permissao("funcionario"):
                menu_relatorios_vendas(sistema)
            
            # Funcionalidades para funcionários (opção 7) - Gerenciar Clientes
            elif opcao == "7" and sistema.tem_permissao("funcionario"):
                print("\n👥 GERENCIAR CLIENTES")
                print("-" * 30)
                clientes = sistema.listar_usuarios_por_tipo("cliente")
                if clientes:
                    print("📋 Lista de clientes:")
                    for i, cliente in enumerate(clientes, 1):
                        print(f"  {i}. {cliente}")
                else:
                    print("❌ Nenhum cliente cadastrado!")
            
            # Funcionalidades para funcionários (opção 8) - Relatórios Básicos
            elif opcao == "8" and sistema.tem_permissao("funcionario"):
                print("\n📊 RELATÓRIOS BÁSICOS")
                print("-" * 30)
                total_clientes = len(sistema.listar_usuarios_por_tipo("cliente"))
                total_funcionarios = len(sistema.listar_usuarios_por_tipo("funcionario"))
                print(f"👥 Total de clientes: {total_clientes}")
                print(f"👨‍💼 Total de funcionários: {total_funcionarios}")
            
            # Funcionalidades para administradores (opção 9) - Gerenciar Usuários
            elif opcao == "9" and sistema.tem_permissao("admin"):
                print("\n⚙️ GERENCIAR USUÁRIOS")
                print("-" * 30)
                print("1. Listar todos os usuários")
                print("2. Desativar usuário")
                print("3. Ativar usuário")
                sub_opcao = input("Escolha uma opção: ").strip()
                
                if sub_opcao == "1":
                    print("\n📋 TODOS OS USUÁRIOS:")
                    for usuario, dados in sistema.usuarios.items():
                        status = "🟢 Ativo" if dados.get("ativo", True) else "🔴 Inativo"
                        print(f"  👤 {usuario} ({dados.get('tipo', 'cliente')}) - {status}")
                
                elif sub_opcao == "2":
                    usuario = input("Digite o nome do usuário a desativar: ").strip()
                    sistema.desativar_usuario(usuario)
                
                elif sub_opcao == "3":
                    usuario = input("Digite o nome do usuário a ativar: ").strip()
                    sistema.ativar_usuario(usuario)
            
            # Funcionalidades para administradores (opção 10) - Relatórios Avançados
            elif opcao == "10" and sistema.tem_permissao("admin"):
                print("\n📈 RELATÓRIOS AVANÇADOS")
                print("-" * 30)
                total_usuarios = len(sistema.usuarios)
                total_admins = len(sistema.listar_usuarios_por_tipo("admin"))
                usuarios_ativos = sum(1 for dados in sistema.usuarios.values() if dados.get("ativo", True))
                
                print(f"📊 Total de usuários: {total_usuarios}")
                print(f"👑 Administradores: {total_admins}")
                print(f"🟢 Usuários ativos: {usuarios_ativos}")
                print(f"🔴 Usuários inativos: {total_usuarios - usuarios_ativos}")
            
            # Funcionalidades para administradores (opção 11) - Configurações
            elif opcao == "11" and sistema.tem_permissao("admin"):
                print("\n⚙️ CONFIGURAÇÕES DO SISTEMA")
                print("-" * 30)
                print("🔐 Sistema de criptografia: PBKDF2")
                print("🛡️ Níveis de segurança: Ativo")
                print("📁 Arquivo de usuários: usuarios.json")
                print("🔑 Chave mestra: chave_mestra.key")
                print("📦 Arquivo de produtos: produtos.json")
                print("📝 Arquivo de movimentos: movimentos.json")
                print("💰 Arquivo de contas a pagar: contas_pagar.json")
                print("💰 Arquivo de contas a receber: contas_receber.json")
            
            # Funcionalidades financeiras (opção 12) - Gerenciar Financeiro
            elif opcao == "12" and sistema.tem_permissao("funcionario"):
                menu_gerenciar_financeiro(sistema)
            
            # Funcionalidades financeiras (opção 13) - Relatórios Financeiros
            elif opcao == "13" and sistema.tem_permissao("funcionario"):
                menu_relatorios_financeiros(sistema)
            
            # Logout (opção dinâmica)
            elif opcao in ["3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]:
                # Verifica se é logout baseado no tipo de usuário
                tipo_usuario = sistema.obter_tipo_usuario()
                
                if tipo_usuario == "cliente":
                    # Cliente: opção 3 = logout
                    if opcao == "3":
                        sistema.fazer_logout()
                    else:
                        print("❌ Opção inválida!")
                
                elif tipo_usuario == "funcionario":
                    # Funcionário: opção 11 = logout
                    if opcao == "11":
                        sistema.fazer_logout()
                    else:
                        print("❌ Opção inválida!")
                
                elif tipo_usuario == "admin":
                    # Admin: opção 14 = logout
                    if opcao == "14":
                        sistema.fazer_logout()
                    else:
                        print("❌ Opção inválida!")
            
            else:
                print("❌ Opção inválida!")

def menu_gerenciar_estoque(sistema):
    """Menu para gerenciar estoque"""
    while True:
        print("\n📦 GERENCIAR ESTOQUE")
        print("=" * 40)
        print("1. Cadastrar produto")
        print("2. Listar produtos")
        print("3. Buscar produto")
        print("4. Entrada de estoque")
        print("5. Saída de estoque")
        print("6. Excluir produto")
        print("7. Voltar ao menu anterior")
        print("=" * 40)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n📝 CADASTRAR PRODUTO")
            print("-" * 30)
            nome = input("Nome do produto: ").strip()
            categoria = input("Categoria: ").strip()
            try:
                preco = float(input("Preço unitário: R$ ").strip())
                estoque_minimo = int(input("Estoque mínimo (padrão 5): ").strip() or "5")
                
                sistema.estoque.cadastrar_produto(nome, categoria, preco, estoque_minimo, sistema.usuario_atual)
            except ValueError:
                print("❌ Erro: Valores numéricos inválidos!")
        
        elif opcao == "2":
            print("\n📋 LISTA DE PRODUTOS")
            print("-" * 30)
            produtos = sistema.estoque.listar_produtos()
            if produtos:
                print(f"{'Código':<8} {'Nome':<20} {'Categoria':<15} {'Preço':<10} {'Estoque':<8} {'Mín.':<5}")
                print("-" * 70)
                for produto in produtos:
                    alerta = "⚠️" if produto["quantidade"] <= produto["estoque_minimo"] else "  "
                    print(f"{produto['codigo']:<8} {produto['nome'][:19]:<20} {produto['categoria'][:14]:<15} R${produto['preco']:<9.2f} {produto['quantidade']:<8} {produto['estoque_minimo']:<5} {alerta}")
            else:
                print("❌ Nenhum produto cadastrado!")
        
        elif opcao == "3":
            print("\n🔍 BUSCAR PRODUTO")
            print("-" * 30)
            termo = input("Digite código, nome ou categoria: ").strip()
            if termo:
                produtos = sistema.estoque.buscar_produto(termo)
                if produtos:
                    print(f"{'Código':<8} {'Nome':<20} {'Categoria':<15} {'Preço':<10} {'Estoque':<8}")
                    print("-" * 65)
                    for produto in produtos:
                        print(f"{produto['codigo']:<8} {produto['nome'][:19]:<20} {produto['categoria'][:14]:<15} R${produto['preco']:<9.2f} {produto['quantidade']:<8}")
                else:
                    print("❌ Nenhum produto encontrado!")
        
        elif opcao == "4":
            print("\n📦 ENTRADA DE ESTOQUE")
            print("-" * 30)
            codigo = input("Código do produto: ").strip().upper()
            try:
                quantidade = int(input("Quantidade: ").strip())
                observacao = input("Observação (opcional): ").strip()
                
                sistema.estoque.registrar_movimento(codigo, "entrada", quantidade, observacao, sistema.usuario_atual)
            except ValueError:
                print("❌ Erro: Quantidade deve ser um número!")
        
        elif opcao == "5":
            print("\n📤 SAÍDA DE ESTOQUE")
            print("-" * 30)
            codigo = input("Código do produto: ").strip().upper()
            try:
                quantidade = int(input("Quantidade: ").strip())
                observacao = input("Observação (opcional): ").strip()
                
                sistema.estoque.registrar_movimento(codigo, "saida", quantidade, observacao, sistema.usuario_atual)
            except ValueError:
                print("❌ Erro: Quantidade deve ser um número!")
        
        elif opcao == "6" and sistema.tem_permissao("admin"):
            print("\n🗑️ EXCLUIR PRODUTO")
            print("-" * 30)
            codigo = input("Código do produto: ").strip().upper()
            confirmacao = input("Tem certeza? (s/N): ").strip().lower()
            if confirmacao == 's':
                sistema.estoque.excluir_produto(codigo, sistema.usuario_atual)
        
        elif opcao == "7":
            break
        
        else:
            print("❌ Opção inválida!")

def menu_relatorios_estoque(sistema):
    """Menu para relatórios de estoque"""
    while True:
        print("\n📊 RELATÓRIOS DE ESTOQUE")
        print("=" * 40)
        print("1. Relatório geral do estoque")
        print("2. Produtos com estoque baixo")
        print("3. Últimas movimentações")
        print("4. Buscar movimentações por produto")
        print("5. Voltar ao menu anterior")
        print("=" * 40)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n📈 RELATÓRIO GERAL DO ESTOQUE")
            print("=" * 50)
            relatorio = sistema.estoque.relatorio_estoque()
            
            print(f"📦 Total de produtos: {relatorio['total_produtos']}")
            print(f"📊 Total de itens: {relatorio['total_itens']}")
            print(f"💰 Valor total: R$ {relatorio['valor_total']:.2f}")
            print(f"⚪ Produtos zerados: {relatorio['produtos_zerados']}")
            print(f"⚠️ Produtos com estoque baixo: {relatorio['produtos_estoque_baixo']}")
            
            if relatorio['categorias']:
                print("\n📋 Por categoria:")
                for cat, dados in relatorio['categorias'].items():
                    print(f"  {cat}: {dados['produtos']} produtos, {dados['itens']} itens, R$ {dados['valor']:.2f}")
            
            print(f"\n📅 Relatório gerado em: {relatorio['data_relatorio']}")
        
        elif opcao == "2":
            print("\n⚠️ PRODUTOS COM ESTOQUE BAIXO")
            print("-" * 40)
            produtos = sistema.estoque.obter_produtos_estoque_baixo()
            if produtos:
                print(f"{'Código':<8} {'Nome':<20} {'Atual':<6} {'Mín.':<5} {'Status'}")
                print("-" * 50)
                for produto in produtos:
                    status = "ZERADO" if produto["quantidade"] == 0 else "BAIXO"
                    print(f"{produto['codigo']:<8} {produto['nome'][:19]:<20} {produto['quantidade']:<6} {produto['estoque_minimo']:<5} {status}")
            else:
                print("✅ Nenhum produto com estoque baixo!")
        
        elif opcao == "3":
            print("\n📝 ÚLTIMAS MOVIMENTAÇÕES")
            print("-" * 40)
            movimentos = sistema.estoque.relatorio_movimentos(20)
            if movimentos:
                print(f"{'Data/Hora':<17} {'Tipo':<8} {'Produto':<15} {'Qtd':<5} {'Usuário':<10}")
                print("-" * 60)
                for mov in movimentos:
                    emoji = "📦" if mov["tipo"] == "entrada" else "📤"
                    print(f"{mov['data_hora']:<17} {emoji} {mov['tipo'][:7]:<8} {mov['nome_produto'][:14]:<15} {mov['quantidade']:<5} {mov['usuario'][:9]:<10}")
            else:
                print("❌ Nenhuma movimentação registrada!")
        
        elif opcao == "4":
            print("\n🔍 MOVIMENTAÇÕES POR PRODUTO")
            print("-" * 40)
            termo = input("Digite código ou nome do produto: ").strip()
            if termo:
                produtos = sistema.estoque.buscar_produto(termo)
                if produtos:
                    codigo = produtos[0]["codigo"]
                    movimentos = [m for m in sistema.estoque.movimentos if m["codigo_produto"] == codigo]
                    
                    if movimentos:
                        print(f"\nMovimentações de {produtos[0]['nome']}:")
                        print(f"{'Data/Hora':<17} {'Tipo':<8} {'Qtd':<5} {'Ant.':<5} {'Atual':<5} {'Usuário'}")
                        print("-" * 55)
                        for mov in movimentos[-10:]:  # Últimas 10
                            emoji = "📦" if mov["tipo"] == "entrada" else "📤"
                            print(f"{mov['data_hora']:<17} {emoji} {mov['tipo'][:7]:<8} {mov['quantidade']:<5} {mov['estoque_anterior']:<5} {mov['estoque_atual']:<5} {mov['usuario']}")
                    else:
                        print("❌ Nenhuma movimentação encontrada!")
                else:
                    print("❌ Produto não encontrado!")
        
        elif opcao == "5":
            break
        
        else:
            print("❌ Opção inválida!")

def menu_gerenciar_vendas(sistema):
    """Menu para gerenciar vendas"""
    while True:
        print("\n🛒 GERENCIAR VENDAS")
        print("=" * 40)
        print("1. Cadastrar cliente")
        print("2. Listar clientes")
        print("3. Buscar cliente")
        print("4. Criar pedido")
        print("5. Listar pedidos")
        print("6. Buscar pedido")
        print("7. Atualizar status do pedido")
        print("8. Gerar recibo PDF")
        print("9. Voltar ao menu anterior")
        print("=" * 40)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n👤 CADASTRAR CLIENTE")
            print("-" * 30)
            nome = input("Nome do cliente: ").strip()
            email = input("Email: ").strip()
            telefone = input("Telefone: ").strip()
            endereco = input("Endereço (opcional): ").strip()
            
            sistema.vendas.cadastrar_cliente(nome, email, telefone, endereco, sistema.usuario_atual)
        
        elif opcao == "2":
            print("\n📋 LISTA DE CLIENTES")
            print("-" * 30)
            clientes = sistema.vendas.listar_clientes()
            if clientes:
                print(f"{'ID':<4} {'Nome':<20} {'Email':<25} {'Telefone':<15}")
                print("-" * 70)
                for cliente in clientes:
                    print(f"{cliente['id']:<4} {cliente['nome'][:19]:<20} {cliente['email'][:24]:<25} {cliente['telefone'][:14]:<15}")
            else:
                print("❌ Nenhum cliente cadastrado!")
        
        elif opcao == "3":
            print("\n🔍 BUSCAR CLIENTE")
            print("-" * 30)
            termo = input("Digite ID, nome ou email: ").strip()
            if termo:
                clientes = sistema.vendas.buscar_cliente(termo)
                if clientes:
                    print(f"{'ID':<4} {'Nome':<20} {'Email':<25} {'Telefone':<15}")
                    print("-" * 70)
                    for cliente in clientes:
                        print(f"{cliente['id']:<4} {cliente['nome'][:19]:<20} {cliente['email'][:24]:<25} {cliente['telefone'][:14]:<15}")
                else:
                    print("❌ Nenhum cliente encontrado!")
        
        elif opcao == "4":
            print("\n📝 CRIAR PEDIDO")
            print("-" * 30)
            
            # Seleciona cliente
            cliente_id = input("ID do cliente: ").strip()
            if cliente_id not in sistema.vendas.clientes:
                print("❌ Cliente não encontrado!")
                continue
            
            # Lista produtos disponíveis
            produtos_estoque = sistema.estoque.listar_produtos()
            if not produtos_estoque:
                print("❌ Nenhum produto disponível no estoque!")
                continue
            
            print("\n📦 PRODUTOS DISPONÍVEIS:")
            print(f"{'Código':<8} {'Nome':<20} {'Preço':<10} {'Estoque':<8}")
            print("-" * 50)
            for produto in produtos_estoque:
                print(f"{produto['codigo']:<8} {produto['nome'][:19]:<20} R${produto['preco']:<9.2f} {produto['quantidade']:<8}")
            
            # Adiciona produtos ao pedido
            produtos_pedido = []
            while True:
                print("\nAdicionar produto ao pedido:")
                codigo_produto = input("Código do produto (ou 'fim' para finalizar): ").strip().upper()
                
                if codigo_produto.lower() == 'fim':
                    break
                
                # Encontra o produto
                produto_encontrado = None
                for produto in produtos_estoque:
                    if produto['codigo'] == codigo_produto:
                        produto_encontrado = produto
                        break
                
                if not produto_encontrado:
                    print("❌ Produto não encontrado!")
                    continue
                
                try:
                    quantidade = int(input(f"Quantidade de {produto_encontrado['nome']}: ").strip())
                    if quantidade <= 0:
                        print("❌ Quantidade deve ser maior que zero!")
                        continue
                    
                    if quantidade > produto_encontrado['quantidade']:
                        print(f"❌ Estoque insuficiente! Disponível: {produto_encontrado['quantidade']}")
                        continue
                    
                    produtos_pedido.append({
                        "codigo": produto_encontrado['codigo'],
                        "nome": produto_encontrado['nome'],
                        "quantidade": quantidade,
                        "preco_unitario": produto_encontrado['preco']
                    })
                    
                    print(f"✅ {quantidade}x {produto_encontrado['nome']} adicionado!")
                    
                except ValueError:
                    print("❌ Quantidade inválida!")
            
            if produtos_pedido:
                observacoes = input("Observações do pedido (opcional): ").strip()
                
                # Cria o pedido
                codigo_pedido = sistema.vendas.criar_pedido(cliente_id, produtos_pedido, observacoes, sistema.usuario_atual)
                
                if codigo_pedido:
                    # Atualiza estoque (saída automática)
                    for item in produtos_pedido:
                        sistema.estoque.registrar_movimento(
                            item['codigo'], 
                            "saida", 
                            item['quantidade'], 
                            f"Venda - Pedido {codigo_pedido}", 
                            sistema.usuario_atual
                        )
            else:
                print("❌ Pedido deve ter pelo menos um produto!")
        
        elif opcao == "5":
            print("\n📋 LISTA DE PEDIDOS")
            print("-" * 30)
            pedidos = sistema.vendas.listar_pedidos()
            if pedidos:
                print(f"{'Código':<8} {'Cliente':<20} {'Total':<10} {'Status':<12} {'Data'}")
                print("-" * 65)
                for pedido in pedidos:
                    print(f"{pedido['codigo']:<8} {pedido['cliente_nome'][:19]:<20} R${pedido['total']:<9.2f} {pedido['status']:<12} {pedido['data_criacao'][:10]}")
            else:
                print("❌ Nenhum pedido encontrado!")
        
        elif opcao == "6":
            print("\n🔍 BUSCAR PEDIDO")
            print("-" * 30)
            termo = input("Digite código do pedido ou nome do cliente: ").strip()
            if termo:
                pedidos = sistema.vendas.buscar_pedido(termo)
                if pedidos:
                    print(f"{'Código':<8} {'Cliente':<20} {'Total':<10} {'Status':<12} {'Data'}")
                    print("-" * 65)
                    for pedido in pedidos:
                        print(f"{pedido['codigo']:<8} {pedido['cliente_nome'][:19]:<20} R${pedido['total']:<9.2f} {pedido['status']:<12} {pedido['data_criacao'][:10]}")
                else:
                    print("❌ Nenhum pedido encontrado!")
        
        elif opcao == "7":
            print("\n📝 ATUALIZAR STATUS DO PEDIDO")
            print("-" * 30)
            codigo_pedido = input("Código do pedido: ").strip().upper()
            print("Status disponíveis: pendente, aprovado, cancelado, finalizado")
            novo_status = input("Novo status: ").strip().lower()
            
            if novo_status in ["pendente", "aprovado", "cancelado", "finalizado"]:
                sistema.vendas.atualizar_status_pedido(codigo_pedido, novo_status, sistema.usuario_atual)
            else:
                print("❌ Status inválido!")
        
        elif opcao == "8":
            print("\n📄 GERAR RECIBO PDF")
            print("-" * 30)
            codigo_pedido = input("Código do pedido: ").strip().upper()
            
            caminho_pdf = sistema.vendas.gerar_recibo_pdf(codigo_pedido)
            if caminho_pdf:
                print(f"📄 PDF salvo em: {caminho_pdf}")
        
        elif opcao == "9":
            break
        
        else:
            print("❌ Opção inválida!")

def menu_relatorios_vendas(sistema):
    """Menu para relatórios de vendas"""
    while True:
        print("\n📋 RELATÓRIOS DE VENDAS")
        print("=" * 40)
        print("1. Relatório geral de vendas")
        print("2. Relatório por período")
        print("3. Top produtos vendidos")
        print("4. Pedidos por status")
        print("5. Voltar ao menu anterior")
        print("=" * 40)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n📈 RELATÓRIO GERAL DE VENDAS")
            print("=" * 50)
            relatorio = sistema.vendas.relatorio_vendas()
            
            print(f"📊 Total de pedidos: {relatorio['total_pedidos']}")
            print(f"💰 Total de vendas: R$ {relatorio['total_vendas']:.2f}")
            print(f"✅ Pedidos finalizados: {relatorio['pedidos_finalizados']}")
            print(f"⏳ Pedidos pendentes: {relatorio['pedidos_pendentes']}")
            
            if relatorio['top_produtos']:
                print("\n🏆 TOP 5 PRODUTOS MAIS VENDIDOS:")
                for i, (produto, dados) in enumerate(relatorio['top_produtos'], 1):
                    print(f"  {i}. {produto}: {dados['quantidade']} unidades - R$ {dados['valor']:.2f}")
            
            print(f"\n📅 Relatório gerado em: {relatorio['data_relatorio']}")
        
        elif opcao == "2":
            print("\n📅 RELATÓRIO POR PERÍODO")
            print("-" * 30)
            data_inicio = input("Data de início (YYYY-MM-DD): ").strip()
            data_fim = input("Data de fim (YYYY-MM-DD): ").strip()
            
            if data_inicio and data_fim:
                relatorio = sistema.vendas.relatorio_vendas(data_inicio, data_fim)
                
                print(f"\n📊 Relatório de {data_inicio} a {data_fim}")
                print(f"📊 Total de pedidos: {relatorio['total_pedidos']}")
                print(f"💰 Total de vendas: R$ {relatorio['total_vendas']:.2f}")
                print(f"✅ Pedidos finalizados: {relatorio['pedidos_finalizados']}")
                print(f"⏳ Pedidos pendentes: {relatorio['pedidos_pendentes']}")
            else:
                print("❌ Datas inválidas!")
        
        elif opcao == "3":
            print("\n🏆 TOP PRODUTOS VENDIDOS")
            print("-" * 30)
            relatorio = sistema.vendas.relatorio_vendas()
            
            if relatorio['produtos_vendidos']:
                print(f"{'Produto':<25} {'Quantidade':<12} {'Valor Total':<12}")
                print("-" * 50)
                for produto, dados in sorted(relatorio['produtos_vendidos'].items(), 
                                           key=lambda x: x[1]['quantidade'], reverse=True):
                    print(f"{produto[:24]:<25} {dados['quantidade']:<12} R$ {dados['valor']:<11.2f}")
            else:
                print("❌ Nenhuma venda registrada!")
        
        elif opcao == "4":
            print("\n📊 PEDIDOS POR STATUS")
            print("-" * 30)
            pedidos = sistema.vendas.listar_pedidos()
            
            if pedidos:
                status_count = {}
                for pedido in pedidos:
                    status = pedido['status']
                    status_count[status] = status_count.get(status, 0) + 1
                
                for status, count in status_count.items():
                    print(f"  {status.upper()}: {count} pedidos")
            else:
                print("❌ Nenhum pedido encontrado!")
        
        elif opcao == "5":
            break
        
        else:
            print("❌ Opção inválida!")

def menu_gerenciar_financeiro(sistema):
    """Menu para gerenciar financeiro"""
    while True:
        print("\n💰 GERENCIAR FINANCEIRO")
        print("=" * 50)
        print("1. Cadastrar conta a pagar")
        print("2. Cadastrar conta a receber")
        print("3. Listar contas a pagar")
        print("4. Listar contas a receber")
        print("5. Buscar conta a pagar")
        print("6. Buscar conta a receber")
        print("7. Registrar pagamento")
        print("8. Registrar recebimento")
        print("9. Excluir conta a pagar")
        print("10. Excluir conta a receber")
        print("11. Alertas de vencimento")
        print("12. Voltar ao menu anterior")
        print("=" * 50)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n📝 CADASTRAR CONTA A PAGAR")
            print("-" * 40)
            
            # Mostrar categorias disponíveis
            print("📋 CATEGORIAS DISPONÍVEIS:")
            for codigo, info in sistema.financeiro.categorias["contas_pagar"].items():
                print(f"  {codigo}: {info['nome']} ({info['tipo']}) {info['cor']}")
            
            descricao = input("Descrição da conta: ").strip()
            categoria = input("Categoria: ").strip().lower()
            try:
                valor = float(input("Valor: R$ ").strip())
                data_vencimento = input("Data de vencimento (YYYY-MM-DD): ").strip()
                fornecedor = input("Fornecedor (opcional): ").strip()
                observacoes = input("Observações (opcional): ").strip()
                
                sistema.financeiro.cadastrar_conta_pagar(
                    descricao, categoria, valor, data_vencimento, 
                    fornecedor, observacoes, sistema.usuario_atual
                )
            except ValueError:
                print("❌ Erro: Valor inválido!")
        
        elif opcao == "2":
            print("\n📝 CADASTRAR CONTA A RECEBER")
            print("-" * 40)
            
            # Mostrar categorias disponíveis
            print("📋 CATEGORIAS DISPONÍVEIS:")
            for codigo, info in sistema.financeiro.categorias["contas_receber"].items():
                print(f"  {codigo}: {info['nome']} ({info['tipo']}) {info['cor']}")
            
            cliente = input("Nome do cliente: ").strip()
            descricao = input("Descrição da conta: ").strip()
            categoria = input("Categoria: ").strip().lower()
            try:
                valor = float(input("Valor: R$ ").strip())
                data_vencimento = input("Data de vencimento (YYYY-MM-DD): ").strip()
                observacoes = input("Observações (opcional): ").strip()
                
                sistema.financeiro.cadastrar_conta_receber(
                    cliente, descricao, categoria, valor, data_vencimento, 
                    observacoes, sistema.usuario_atual
                )
            except ValueError:
                print("❌ Erro: Valor inválido!")
        
        elif opcao == "3":
            print("\n📋 LISTA DE CONTAS A PAGAR")
            print("-" * 40)
            print("Filtros:")
            print("1. Todas")
            print("2. Pendentes")
            print("3. Pagas")
            print("4. Atrasadas")
            filtro = input("Escolha o filtro (1-4): ").strip()
            
            status_map = {"1": None, "2": "pendente", "3": "pago", "4": "atrasado"}
            status = status_map.get(filtro)
            
            contas = sistema.financeiro.listar_contas_pagar(status)
            if contas:
                print(f"{'ID':<8} {'Descrição':<25} {'Categoria':<15} {'Valor':<12} {'Vencimento':<12} {'Status'}")
                print("-" * 85)
                for conta in contas:
                    status_emoji = "✅" if conta["status"] == "pago" else "⏳" if conta["status"] == "pendente" else "🔴"
                    print(f"{conta['id']:<8} {conta['descricao'][:24]:<25} {conta['categoria'][:14]:<15} {sistema.financeiro.formatar_valor(conta['valor']):<12} {conta['data_vencimento']:<12} {status_emoji}")
            else:
                print("❌ Nenhuma conta encontrada!")
        
        elif opcao == "4":
            print("\n📋 LISTA DE CONTAS A RECEBER")
            print("-" * 40)
            print("Filtros:")
            print("1. Todas")
            print("2. Pendentes")
            print("3. Recebidas")
            print("4. Atrasadas")
            filtro = input("Escolha o filtro (1-4): ").strip()
            
            status_map = {"1": None, "2": "pendente", "3": "recebido", "4": "atrasado"}
            status = status_map.get(filtro)
            
            contas = sistema.financeiro.listar_contas_receber(status)
            if contas:
                print(f"{'ID':<8} {'Cliente':<20} {'Descrição':<20} {'Valor':<12} {'Vencimento':<12} {'Status'}")
                print("-" * 85)
                for conta in contas:
                    status_emoji = "✅" if conta["status"] == "recebido" else "⏳" if conta["status"] == "pendente" else "🔴"
                    print(f"{conta['id']:<8} {conta['cliente'][:19]:<20} {conta['descricao'][:19]:<20} {sistema.financeiro.formatar_valor(conta['valor']):<12} {conta['data_vencimento']:<12} {status_emoji}")
            else:
                print("❌ Nenhuma conta encontrada!")
        
        elif opcao == "5":
            print("\n🔍 BUSCAR CONTA A PAGAR")
            print("-" * 40)
            termo = input("Digite ID, descrição ou fornecedor: ").strip()
            if termo:
                contas = sistema.financeiro.buscar_conta_pagar(termo)
                if contas:
                    print(f"{'ID':<8} {'Descrição':<25} {'Fornecedor':<15} {'Valor':<12} {'Vencimento':<12} {'Status'}")
                    print("-" * 85)
                    for conta in contas:
                        status_emoji = "✅" if conta["status"] == "pago" else "⏳" if conta["status"] == "pendente" else "🔴"
                        print(f"{conta['id']:<8} {conta['descricao'][:24]:<25} {conta['fornecedor'][:14]:<15} {sistema.financeiro.formatar_valor(conta['valor']):<12} {conta['data_vencimento']:<12} {status_emoji}")
                else:
                    print("❌ Nenhuma conta encontrada!")
        
        elif opcao == "6":
            print("\n🔍 BUSCAR CONTA A RECEBER")
            print("-" * 40)
            termo = input("Digite ID, cliente ou descrição: ").strip()
            if termo:
                contas = sistema.financeiro.buscar_conta_receber(termo)
                if contas:
                    print(f"{'ID':<8} {'Cliente':<20} {'Descrição':<20} {'Valor':<12} {'Vencimento':<12} {'Status'}")
                    print("-" * 85)
                    for conta in contas:
                        status_emoji = "✅" if conta["status"] == "recebido" else "⏳" if conta["status"] == "pendente" else "🔴"
                        print(f"{conta['id']:<8} {conta['cliente'][:19]:<20} {conta['descricao'][:19]:<20} {sistema.financeiro.formatar_valor(conta['valor']):<12} {conta['data_vencimento']:<12} {status_emoji}")
                else:
                    print("❌ Nenhuma conta encontrada!")
        
        elif opcao == "7":
            print("\n💰 REGISTRAR PAGAMENTO")
            print("-" * 40)
            conta_id = input("ID da conta: ").strip().upper()
            data_pagamento = input("Data do pagamento (YYYY-MM-DD, Enter para hoje): ").strip()
            if not data_pagamento:
                data_pagamento = None
            
            sistema.financeiro.registrar_pagamento(conta_id, data_pagamento, sistema.usuario_atual)
        
        elif opcao == "8":
            print("\n💰 REGISTRAR RECEBIMENTO")
            print("-" * 40)
            conta_id = input("ID da conta: ").strip().upper()
            data_recebimento = input("Data do recebimento (YYYY-MM-DD, Enter para hoje): ").strip()
            if not data_recebimento:
                data_recebimento = None
            
            sistema.financeiro.registrar_recebimento(conta_id, data_recebimento, sistema.usuario_atual)
        
        elif opcao == "9" and sistema.tem_permissao("admin"):
            print("\n🗑️ EXCLUIR CONTA A PAGAR")
            print("-" * 40)
            conta_id = input("ID da conta: ").strip().upper()
            confirmacao = input("Tem certeza? (s/N): ").strip().lower()
            if confirmacao == 's':
                sistema.financeiro.excluir_conta_pagar(conta_id, sistema.usuario_atual)
        
        elif opcao == "10" and sistema.tem_permissao("admin"):
            print("\n🗑️ EXCLUIR CONTA A RECEBER")
            print("-" * 40)
            conta_id = input("ID da conta: ").strip().upper()
            confirmacao = input("Tem certeza? (s/N): ").strip().lower()
            if confirmacao == 's':
                sistema.financeiro.excluir_conta_receber(conta_id, sistema.usuario_atual)
        
        elif opcao == "11":
            print("\n⚠️ ALERTAS DE VENCIMENTO")
            print("-" * 40)
            alertas = sistema.financeiro.obter_alertas_vencimento()
            
            if alertas["vencendo_hoje"]:
                print("🔴 VENCENDO HOJE:")
                for item in alertas["vencendo_hoje"]:
                    conta = item["conta"]
                    tipo = "PAGAR" if item["tipo"] == "pagar" else "RECEBER"
                    print(f"  {tipo}: {conta['id']} - {conta.get('descricao', conta.get('cliente', ''))} - {sistema.financeiro.formatar_valor(conta['valor'])}")
            
            if alertas["vencendo_em_7_dias"]:
                print("\n🟡 VENCENDO EM 7 DIAS:")
                for item in alertas["vencendo_em_7_dias"]:
                    conta = item["conta"]
                    tipo = "PAGAR" if item["tipo"] == "pagar" else "RECEBER"
                    print(f"  {tipo}: {conta['id']} - {conta.get('descricao', conta.get('cliente', ''))} - {sistema.financeiro.formatar_valor(conta['valor'])}")
            
            if alertas["atrasadas"]:
                print("\n🔴 ATRASADAS:")
                for item in alertas["atrasadas"]:
                    conta = item["conta"]
                    tipo = "PAGAR" if item["tipo"] == "pagar" else "RECEBER"
                    print(f"  {tipo}: {conta['id']} - {conta.get('descricao', conta.get('cliente', ''))} - {sistema.financeiro.formatar_valor(conta['valor'])}")
            
            if not any(alertas.values()):
                print("✅ Nenhum alerta de vencimento!")
        
        elif opcao == "12":
            break
        
        else:
            print("❌ Opção inválida!")

def menu_relatorios_financeiros(sistema):
    """Menu para relatórios financeiros"""
    while True:
        print("\n📊 RELATÓRIOS FINANCEIROS")
        print("=" * 50)
        print("1. Relatório financeiro geral")
        print("2. Relatório por período")
        print("3. Análise por categoria")
        print("4. Contas atrasadas")
        print("5. Fluxo de caixa básico")
        print("6. Fluxo de caixa diário")
        print("7. Fluxo de caixa mensal")
        print("8. Fluxo de caixa por período")
        print("9. Voltar ao menu anterior")
        print("=" * 50)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n📈 RELATÓRIO FINANCEIRO GERAL")
            print("=" * 60)
            relatorio = sistema.financeiro.relatorio_financeiro()
            
            resumo = relatorio["resumo"]
            print(f"💰 TOTAL A PAGAR: {sistema.financeiro.formatar_valor(resumo['total_pagar'])}")
            print(f"💰 TOTAL A RECEBER: {sistema.financeiro.formatar_valor(resumo['total_receber'])}")
            print(f"✅ TOTAL PAGO: {sistema.financeiro.formatar_valor(resumo['total_pago'])}")
            print(f"✅ TOTAL RECEBIDO: {sistema.financeiro.formatar_valor(resumo['total_recebido'])}")
            print(f"⏳ PENDENTE A PAGAR: {sistema.financeiro.formatar_valor(resumo['total_pagar_pendente'])}")
            print(f"⏳ PENDENTE A RECEBER: {sistema.financeiro.formatar_valor(resumo['total_receber_pendente'])}")
            print(f"🔴 ATRASADO A PAGAR: {sistema.financeiro.formatar_valor(resumo['total_pagar_atrasado'])}")
            print(f"🔴 ATRASADO A RECEBER: {sistema.financeiro.formatar_valor(resumo['total_receber_atrasado'])}")
            print(f"💵 SALDO ATUAL: {sistema.financeiro.formatar_valor(resumo['saldo'])}")
            print(f"🔮 SALDO FUTURO: {sistema.financeiro.formatar_valor(resumo['saldo_futuro'])}")
            
            print(f"\n📊 RESUMO DE CONTAS:")
            print(f"  Contas a pagar: {relatorio['contas_pagar']['total']} (pendentes: {relatorio['contas_pagar']['pendentes']}, pagas: {relatorio['contas_pagar']['pagas']}, atrasadas: {relatorio['contas_pagar']['atrasadas']})")
            print(f"  Contas a receber: {relatorio['contas_receber']['total']} (pendentes: {relatorio['contas_receber']['pendentes']}, recebidas: {relatorio['contas_receber']['recebidas']}, atrasadas: {relatorio['contas_receber']['atrasadas']})")
        
        elif opcao == "2":
            print("\n📅 RELATÓRIO POR PERÍODO")
            print("-" * 40)
            data_inicio = input("Data de início (YYYY-MM-DD): ").strip()
            data_fim = input("Data de fim (YYYY-MM-DD): ").strip()
            
            if data_inicio and data_fim:
                relatorio = sistema.financeiro.relatorio_financeiro(data_inicio, data_fim)
                resumo = relatorio["resumo"]
                
                print(f"\n📊 RELATÓRIO DE {data_inicio} A {data_fim}")
                print(f"💰 TOTAL A PAGAR: {sistema.financeiro.formatar_valor(resumo['total_pagar'])}")
                print(f"💰 TOTAL A RECEBER: {sistema.financeiro.formatar_valor(resumo['total_receber'])}")
                print(f"✅ TOTAL PAGO: {sistema.financeiro.formatar_valor(resumo['total_pago'])}")
                print(f"✅ TOTAL RECEBIDO: {sistema.financeiro.formatar_valor(resumo['total_recebido'])}")
                print(f"💵 SALDO: {sistema.financeiro.formatar_valor(resumo['saldo'])}")
            else:
                print("❌ Datas inválidas!")
        
        elif opcao == "3":
            print("\n📋 ANÁLISE POR CATEGORIA")
            print("-" * 40)
            relatorio = sistema.financeiro.relatorio_financeiro()
            
            print("📤 CONTAS A PAGAR POR CATEGORIA:")
            for cat, dados in relatorio["categorias_pagar"].items():
                cat_info = sistema.financeiro.categorias["contas_pagar"].get(cat, {"nome": cat})
                print(f"  {cat_info['nome']}: {sistema.financeiro.formatar_valor(dados['total'])} (pago: {sistema.financeiro.formatar_valor(dados['pago'])}, pendente: {sistema.financeiro.formatar_valor(dados['pendente'])})")
            
            print("\n📥 CONTAS A RECEBER POR CATEGORIA:")
            for cat, dados in relatorio["categorias_receber"].items():
                cat_info = sistema.financeiro.categorias["contas_receber"].get(cat, {"nome": cat})
                print(f"  {cat_info['nome']}: {sistema.financeiro.formatar_valor(dados['total'])} (recebido: {sistema.financeiro.formatar_valor(dados['recebido'])}, pendente: {sistema.financeiro.formatar_valor(dados['pendente'])})")
        
        elif opcao == "4":
            print("\n🔴 CONTAS ATRASADAS")
            print("-" * 40)
            relatorio = sistema.financeiro.relatorio_financeiro()
            
            if relatorio["contas_atrasadas"]["pagar"]:
                print("📤 CONTAS A PAGAR ATRASADAS:")
                for conta in relatorio["contas_atrasadas"]["pagar"]:
                    print(f"  {conta['id']}: {conta['descricao']} - {sistema.financeiro.formatar_valor(conta['valor'])} (vencimento: {conta['data_vencimento']})")
            
            if relatorio["contas_atrasadas"]["receber"]:
                print("\n📥 CONTAS A RECEBER ATRASADAS:")
                for conta in relatorio["contas_atrasadas"]["receber"]:
                    print(f"  {conta['id']}: {conta['cliente']} - {conta['descricao']} - {sistema.financeiro.formatar_valor(conta['valor'])} (vencimento: {conta['data_vencimento']})")
            
            if not relatorio["contas_atrasadas"]["pagar"] and not relatorio["contas_atrasadas"]["receber"]:
                print("✅ Nenhuma conta atrasada!")
        
        elif opcao == "5":
            print("\n💵 FLUXO DE CAIXA BÁSICO")
            print("-" * 40)
            relatorio = sistema.financeiro.relatorio_financeiro()
            resumo = relatorio["resumo"]
            
            print(f"💰 ENTRADAS:")
            print(f"  Recebido: {sistema.financeiro.formatar_valor(resumo['total_recebido'])}")
            print(f"  A receber: {sistema.financeiro.formatar_valor(resumo['total_receber_pendente'])}")
            print(f"  Total entradas: {sistema.financeiro.formatar_valor(resumo['total_recebido'] + resumo['total_receber_pendente'])}")
            
            print(f"\n💸 SAÍDAS:")
            print(f"  Pago: {sistema.financeiro.formatar_valor(resumo['total_pago'])}")
            print(f"  A pagar: {sistema.financeiro.formatar_valor(resumo['total_pagar_pendente'])}")
            print(f"  Total saídas: {sistema.financeiro.formatar_valor(resumo['total_pago'] + resumo['total_pagar_pendente'])}")
            
            print(f"\n💵 SALDO:")
            print(f"  Atual: {sistema.financeiro.formatar_valor(resumo['saldo'])}")
            print(f"  Projetado: {sistema.financeiro.formatar_valor(resumo['saldo_futuro'])}")
        
        elif opcao == "6":
            print("\n📊 FLUXO DE CAIXA DIÁRIO")
            print("-" * 40)
            data = input("Data (YYYY-MM-DD) ou Enter para hoje: ").strip()
            if not data:
                data = None
            
            relatorio = sistema.financeiro.relatorio_fluxo_caixa_completo("dia", data=data)
            print(relatorio)
        
        elif opcao == "7":
            print("\n📊 FLUXO DE CAIXA MENSAL")
            print("-" * 40)
            try:
                ano = int(input("Ano (Enter para atual): ").strip() or datetime.now().year)
                mes = int(input("Mês (1-12, Enter para atual): ").strip() or datetime.now().month)
                
                if 1 <= mes <= 12:
                    relatorio = sistema.financeiro.relatorio_fluxo_caixa_completo("mes", ano=ano, mes=mes)
                    print(relatorio)
                else:
                    print("❌ Mês inválido! Use valores de 1 a 12.")
            except ValueError:
                print("❌ Valores inválidos! Use números.")
        
        elif opcao == "8":
            print("\n📊 FLUXO DE CAIXA POR PERÍODO")
            print("-" * 40)
            data_inicio = input("Data inicial (YYYY-MM-DD): ").strip()
            data_fim = input("Data final (YYYY-MM-DD): ").strip()
            
            if data_inicio and data_fim:
                relatorio = sistema.financeiro.relatorio_fluxo_caixa_completo("periodo", data_inicio=data_inicio, data_fim=data_fim)
                print(relatorio)
            else:
                print("❌ Datas inválidas!")
        
        elif opcao == "9":
            break
        
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main()
