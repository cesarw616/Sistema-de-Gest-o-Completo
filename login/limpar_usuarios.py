import json
import os

def limpar_usuarios_antigos():
    """
    Remove usuários que usam o sistema antigo de hash SHA-256
    e mantém apenas os que usam a nova criptografia PBKDF2
    """
    arquivo_usuarios = "usuarios.json"
    
    if not os.path.exists(arquivo_usuarios):
        print("❌ Arquivo de usuários não encontrado!")
        return
    
    # Carrega os usuários
    with open(arquivo_usuarios, 'r', encoding='utf-8') as arquivo:
        usuarios = json.load(arquivo)
    
    print("🔍 Analisando usuários...")
    print(f"📊 Total de usuários encontrados: {len(usuarios)}")
    
    # Lista para armazenar usuários que serão removidos
    usuarios_para_remover = []
    usuarios_para_manter = []
    
    for usuario, dados in usuarios.items():
        senha = dados.get('senha', '')
        
        # Verifica se é o formato antigo (SHA-256 - 64 caracteres hex)
        if len(senha) == 64 and all(c in '0123456789abcdef' for c in senha):
            usuarios_para_remover.append(usuario)
            print(f"❌ {usuario} - Formato antigo (será removido)")
        else:
            usuarios_para_manter.append(usuario)
            print(f"✅ {usuario} - Formato novo (será mantido)")
    
    if not usuarios_para_remover:
        print("\n🎉 Nenhum usuário antigo encontrado! Todos já estão no formato novo.")
        return
    
    print(f"\n⚠️  Usuários que serão removidos: {len(usuarios_para_remover)}")
    print(f"✅ Usuários que serão mantidos: {len(usuarios_para_manter)}")
    
    # Confirma a remoção
    confirmacao = input("\n🔴 Tem certeza que deseja remover os usuários antigos? (s/N): ").strip().lower()
    
    if confirmacao == 's':
        # Remove os usuários antigos
        for usuario in usuarios_para_remover:
            del usuarios[usuario]
        
        # Salva o arquivo atualizado
        with open(arquivo_usuarios, 'w', encoding='utf-8') as arquivo:
            json.dump(usuarios, arquivo, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Removidos {len(usuarios_para_remover)} usuários antigos!")
        print(f"📊 Restaram {len(usuarios)} usuários no sistema.")
        
        if usuarios_para_manter:
            print("\n👥 Usuários mantidos:")
            for usuario in usuarios_para_manter:
                print(f"  - {usuario}")
    else:
        print("❌ Operação cancelada!")

if __name__ == "__main__":
    print("🧹 LIMPEZA DE USUÁRIOS ANTIGOS")
    print("=" * 40)
    limpar_usuarios_antigos()
