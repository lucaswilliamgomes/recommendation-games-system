#!/usr/bin/env python3
"""
Steam User Data Miner

Este script coleta dados de usuários da Steam usando a Steam Web API.
Utiliza travessia em grafo (BFS) para coletar dados de 1.000 usuários únicos.

Autor: Sistema automatizado
Data: 2025-06-28
"""

import os
import time
import json
import requests
from collections import deque
from typing import Dict, List, Optional, Set, Tuple
from dotenv import load_dotenv
from tqdm import tqdm
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SteamUserMiner:
    """Classe principal para mineração de dados de usuários da Steam."""
    
    def __init__(self, api_key: str, initial_steam_id: str):
        """
        Inicializa o minerador com a chave da API e SteamID inicial.
        
        Args:
            api_key: Chave da Steam Web API
            initial_steam_id: SteamID de 64 bits para começar a coleta
        """
        self.api_key = api_key
        self.initial_steam_id = initial_steam_id
        self.base_url = "https://api.steampowered.com"
        
        # Estruturas de dados para BFS
        self.users_queue = deque([initial_steam_id])
        self.visited_users: Set[str] = set()
        self.users_data: List[Dict] = []
        self.processed_count = 0
        
        # Configurações
        self.target_users = 1000
        self.request_delay = 0.5
        self.max_retries = 3
        
    def get_player_summary(self, steam_id: str) -> Optional[Dict]:
        """
        Obtém informações do perfil do usuário.
        
        Args:
            steam_id: SteamID de 64 bits do usuário
            
        Returns:
            Dict com informações do perfil ou None se falhar
        """
        url = f"{self.base_url}/ISteamUser/GetPlayerSummaries/v0002/"
        params = {
            'key': self.api_key,
            'steamids': steam_id
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                players = data.get('response', {}).get('players', [])
                
                if players:
                    return players[0]
                else:
                    logger.warning(f"Nenhum jogador encontrado para SteamID: {steam_id}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentativa {attempt + 1}/{self.max_retries} falhou para GetPlayerSummaries {steam_id}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    logger.error(f"Falha ao obter perfil do usuário {steam_id} após {self.max_retries} tentativas")
                    return None
        
        return None
    
    def get_owned_games(self, steam_id: str) -> Optional[Dict]:
        """
        Obtém lista de jogos possuídos pelo usuário.
        
        Args:
            steam_id: SteamID de 64 bits do usuário
            
        Returns:
            Dict com jogos possuídos ou None se falhar/perfil privado
        """
        url = f"{self.base_url}/IPlayerService/GetOwnedGames/v0001/"
        params = {
            'key': self.api_key,
            'steamid': steam_id,
            'format': 'json',
            'include_appinfo': True,
            'include_played_free_games': True
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                games_data = data.get('response', {})
                
                if 'games' in games_data:
                    # Adiciona tempo de jogo em horas para cada jogo
                    for game in games_data['games']:
                        playtime_minutes = game.get('playtime_forever', 0)
                        game['playtime_forever_hr'] = round(playtime_minutes / 60, 2)
                    
                    return games_data
                else:
                    logger.info(f"Usuário {steam_id} tem perfil privado ou não possui jogos")
                    return {'game_count': 0, 'games': []}
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentativa {attempt + 1}/{self.max_retries} falhou para GetOwnedGames {steam_id}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    logger.error(f"Falha ao obter jogos do usuário {steam_id} após {self.max_retries} tentativas")
                    return None
        
        return None
    
    def get_friend_list(self, steam_id: str) -> List[str]:
        """
        Obtém lista de amigos do usuário.
        
        Args:
            steam_id: SteamID de 64 bits do usuário
            
        Returns:
            Lista de SteamIDs dos amigos
        """
        url = f"{self.base_url}/ISteamUser/GetFriendList/v0001/"
        params = {
            'key': self.api_key,
            'steamid': steam_id,
            'relationship': 'friend'
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                friends_data = data.get('friendslist', {}).get('friends', [])
                
                return [friend['steamid'] for friend in friends_data]
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentativa {attempt + 1}/{self.max_retries} falhou para GetFriendList {steam_id}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    logger.warning(f"Não foi possível obter lista de amigos do usuário {steam_id}")
                    return []
        
        return []
    
    def process_user(self, steam_id: str) -> bool:
        """
        Processa um usuário: coleta dados e adiciona amigos à fila.
        
        Args:
            steam_id: SteamID de 64 bits do usuário
            
        Returns:
            True se o usuário foi processado com sucesso, False caso contrário
        """
        logger.info(f"Processando usuário {steam_id}...")
        
        # Obter informações do perfil
        profile_info = self.get_player_summary(steam_id)
        if not profile_info:
            logger.warning(f"Não foi possível obter informações do perfil para {steam_id}")
            return False
        
        # Delay para evitar rate limiting
        time.sleep(self.request_delay)
        
        # Obter jogos possuídos
        owned_games = self.get_owned_games(steam_id)
        if owned_games is None:
            logger.warning(f"Não foi possível obter jogos para {steam_id}")
            return False
        
        # Delay para evitar rate limiting
        time.sleep(self.request_delay)
        
        # Obter lista de amigos para expandir o grafo
        friends = self.get_friend_list(steam_id)
        
        # Adicionar novos amigos à fila (que ainda não foram visitados)
        for friend_id in friends:
            if friend_id not in self.visited_users and friend_id not in self.users_queue:
                self.users_queue.append(friend_id)
        
        # Compilar dados do usuário
        user_data = {
            'steam_id': steam_id,
            'profile_info': profile_info,
            'owned_games': owned_games,
            'friends_list': {
                'friend_count': len(friends),
                'friends': friends
            }
        }
        
        self.users_data.append(user_data)
        self.processed_count += 1
        
        logger.info(f"✓ Usuário {steam_id} processado com sucesso! ({self.processed_count}/{self.target_users})")
        
        return True
    
    def save_data(self, filename: str = "steam_user_data.json") -> None:
        """
        Salva os dados coletados em um arquivo JSON.
        
        Args:
            filename: Nome do arquivo para salvar os dados
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.users_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Dados salvos com sucesso em {filename}")
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")
    
    def mine_users(self) -> None:
        """
        Executa o processo de mineração de dados dos usuários.
        Utiliza BFS para coletar dados de usuários através do grafo de amizades.
        """
        logger.info(f"Iniciando mineração de dados da Steam...")
        logger.info(f"Meta: {self.target_users} usuários únicos")
        logger.info(f"SteamID inicial: {self.initial_steam_id}")
        
        # Barra de progresso
        with tqdm(total=self.target_users, desc="Coletando dados", unit="usuários") as pbar:
            
            while self.processed_count < self.target_users and self.users_queue:
                # Pegar próximo usuário da fila
                current_user = self.users_queue.popleft()
                
                # Pular se já foi visitado
                if current_user in self.visited_users:
                    continue
                
                # Marcar como visitado
                self.visited_users.add(current_user)
                
                # Processar usuário
                success = self.process_user(current_user)
                
                if success:
                    pbar.update(1)
                    pbar.set_postfix({
                        'Atual': current_user[-6:],  # Últimos 6 dígitos do SteamID
                        'Fila': len(self.users_queue)
                    })
                
                # Delay adicional entre usuários
                time.sleep(self.request_delay)
                
                # Salvar progresso a cada 50 usuários
                if self.processed_count % 50 == 0:
                    self.save_data(f"steam_user_data_backup_{self.processed_count}.json")
        
        # Salvar dados finais
        self.save_data()
        
        logger.info(f"Mineração concluída!")
        logger.info(f"Usuários processados: {self.processed_count}")
        logger.info(f"Usuários únicos visitados: {len(self.visited_users)}")
        logger.info(f"Dados salvos em steam_user_data.json")


def get_env_or_input(env_var: str, prompt: str, secret: bool = False) -> str:
    """
    Obtém uma variável de ambiente ou solicita entrada do usuário.
    
    Args:
        env_var: Nome da variável de ambiente
        prompt: Prompt para solicitar entrada do usuário
        secret: Se True, usa getpass para entrada oculta
        
    Returns:
        Valor da variável ou entrada do usuário
    """
    value = os.getenv(env_var)
    if value:
        return value
    
    if secret:
        import getpass
        return getpass.getpass(prompt)
    else:
        return input(prompt)


def main():
    """Função principal do script."""
    print("=" * 60)
    print("🎮 STEAM USER DATA MINER 🎮")
    print("=" * 60)
    print()
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    try:
        # Obter configurações
        api_key = get_env_or_input(
            'STEAM_API_KEY',
            'Digite sua Steam API Key: ',
            secret=True
        )
        
        initial_steam_id = get_env_or_input(
            'INITIAL_STEAM_ID',
            'Digite o SteamID inicial (64-bit): '
        )
        
        # Validar entradas
        if not api_key or not initial_steam_id:
            logger.error("API Key e SteamID inicial são obrigatórios!")
            return
        
        if not initial_steam_id.isdigit() or len(initial_steam_id) != 17:
            logger.error("SteamID deve ser um número de 17 dígitos!")
            return
        
        # Criar e executar minerador
        miner = SteamUserMiner(api_key, initial_steam_id)
        miner.mine_users()
        
    except KeyboardInterrupt:
        logger.info("\nProcesso interrompido pelo usuário.")
        if 'miner' in locals() and miner.users_data:
            logger.info("Salvando dados coletados até agora...")
            miner.save_data("steam_user_data_partial.json")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        raise


if __name__ == "__main__":
    main()
