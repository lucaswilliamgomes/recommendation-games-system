#!/usr/bin/env python3
"""
Exemplo de uso do Steam User Miner com configurações personalizadas.
"""

from steam_user_miner import SteamUserMiner
import os

def example_basic_usage():
    """Exemplo básico de uso do minerador."""
    
    # Configurações
    api_key = "YOUR_STEAM_API_KEY_HERE"
    initial_steam_id = "76561197960287930"  # Gabe Newell
    
    # Criar instância do minerador
    miner = SteamUserMiner(api_key, initial_steam_id)
    
    # Configurações personalizadas (opcional)
    miner.target_users = 100  # Coletar apenas 100 usuários
    miner.request_delay = 1.0  # Delay maior entre requisições
    
    # Executar mineração
    miner.mine_users()


def example_custom_configuration():
    """Exemplo com configurações personalizadas."""
    
    api_key = os.getenv('STEAM_API_KEY')
    initial_steam_id = os.getenv('INITIAL_STEAM_ID')
    
    if not api_key or not initial_steam_id:
        print("Configure as variáveis de ambiente STEAM_API_KEY e INITIAL_STEAM_ID")
        return
    
    miner = SteamUserMiner(api_key, initial_steam_id)
    
    # Configurações para coleta mais conservadora
    miner.target_users = 50
    miner.request_delay = 2.0
    miner.max_retries = 5
    
    print(f"Coletando {miner.target_users} usuários com delay de {miner.request_delay}s")
    miner.mine_users()


def analyze_collected_data():
    """Exemplo de análise dos dados coletados."""
    import json
    
    try:
        with open('steam_user_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Total de usuários coletados: {len(data)}")
        
        # Estatísticas básicas
        total_games = sum(user['owned_games']['game_count'] for user in data)
        total_friends = sum(user['friends_list']['friend_count'] for user in data)
        avg_games = total_games / len(data) if data else 0
        avg_friends = total_friends / len(data) if data else 0
        
        print(f"Total de jogos encontrados: {total_games}")
        print(f"Média de jogos por usuário: {avg_games:.2f}")
        print(f"Total de amizades: {total_friends}")
        print(f"Média de amigos por usuário: {avg_friends:.2f}")
        
        # Usuário com mais jogos
        max_games_user = max(data, key=lambda x: x['owned_games']['game_count'])
        print(f"Usuário com mais jogos: {max_games_user['profile_info']['personaname']} ({max_games_user['owned_games']['game_count']} jogos)")
        
        # Usuário com mais amigos
        max_friends_user = max(data, key=lambda x: x['friends_list']['friend_count'])
        print(f"Usuário com mais amigos: {max_friends_user['profile_info']['personaname']} ({max_friends_user['friends_list']['friend_count']} amigos)")
        
        # Top 5 países
        countries = {}
        for user in data:
            country = user['profile_info'].get('loccountrycode', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        
        print("\nTop 5 países:")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {country}: {count} usuários")
            
    except FileNotFoundError:
        print("Arquivo steam_user_data.json não encontrado. Execute o minerador primeiro.")
    except json.JSONDecodeError:
        print("Erro ao ler o arquivo JSON.")


def simple_friendship_analysis():
    """Exemplo simples de análise de amizades sem bibliotecas externas."""
    import json
    
    try:
        with open('steam_user_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Analisando amizades de {len(data)} usuários...")
        
        # Criar mapa de usuários coletados
        collected_users = {user['steam_id']: user for user in data}
        
        # Contar conexões mútuas (amizades bidirecionais)
        mutual_friendships = 0
        friendship_pairs = set()
        
        for user in data:
            user_id = user['steam_id']
            friends = user['friends_list']['friends']
            
            for friend_id in friends:
                if friend_id in collected_users:
                    # Verificar se é amizade mútua
                    friend_data = collected_users[friend_id]
                    if user_id in friend_data['friends_list']['friends']:
                        # Criar par ordenado para evitar duplicatas
                        pair = tuple(sorted([user_id, friend_id]))
                        friendship_pairs.add(pair)
        
        mutual_friendships = len(friendship_pairs)
        
        print(f"Amizades mútuas encontradas: {mutual_friendships}")
        print(f"Densidade de conexões: {(mutual_friendships * 2) / (len(data) * (len(data) - 1)) * 100:.2f}%")
        
        # Encontrar usuários mais conectados no dataset
        internal_connections = {}
        for user in data:
            user_id = user['steam_id']
            friends_in_dataset = sum(1 for friend_id in user['friends_list']['friends'] 
                                   if friend_id in collected_users)
            internal_connections[user_id] = friends_in_dataset
        
        # Top 5 usuários mais conectados
        top_connected = sorted(internal_connections.items(), key=lambda x: x[1], reverse=True)[:5]
        
        print("\nTop 5 usuários mais conectados no dataset:")
        for user_id, connections in top_connected:
            user_data = collected_users[user_id]
            name = user_data['profile_info']['personaname']
            print(f"  {name}: {connections} amigos no dataset")
            
    except FileNotFoundError:
        print("Arquivo steam_user_data.json não encontrado. Execute o minerador primeiro.")
    except json.JSONDecodeError:
        print("Erro ao ler o arquivo JSON.")


if __name__ == "__main__":
    print("Exemplos de uso do Steam User Miner")
    print("1. Uso básico")
    print("2. Configuração personalizada") 
    print("3. Análise de dados coletados")
    print("4. Análise simples de amizades")
    
    choice = input("Escolha uma opção (1-4): ")
    
    if choice == "1":
        example_basic_usage()
    elif choice == "2":
        example_custom_configuration()
    elif choice == "3":
        analyze_collected_data()
    elif choice == "4":
        simple_friendship_analysis()
    else:
        print("Opção inválida!")
