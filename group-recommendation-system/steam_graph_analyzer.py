#!/usr/bin/env python3
"""
Steam Graph Analyzer

Analisa os dados coletados do Steam para criar grupos de afinidade
e gerar recomendações de jogos baseadas nos clusters de usuários.

Autor: Sistema automatizado
Data: 2025-06-28
"""

import json
import math
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class SteamGraphAnalyzer:
    """Analisador de grafo de usuários Steam para clustering e recomendações."""
    
    def __init__(self, data_file: str = "steam_user_data.json"):
        """
        Inicializa o analisador com os dados do Steam.
        
        Args:
            data_file: Arquivo JSON com dados dos usuários
        """
        self.data_file = data_file
        self.users_data = []
        self.game_database = {}
        self.user_similarity_matrix = {}
        self.clusters = []
        self.game_recommendations = {}
        
    def load_data(self) -> bool:
        """Carrega os dados dos usuários do arquivo JSON."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.users_data = json.load(f)
            
            logger.info(f"Carregados {len(self.users_data)} usuários")
            self._build_game_database()
            return True
            
        except FileNotFoundError:
            logger.error(f"Arquivo {self.data_file} não encontrado")
            return False
        except json.JSONDecodeError:
            logger.error("Erro ao decodificar arquivo JSON")
            return False
    
    def _build_game_database(self):
        """Constrói um banco de dados de jogos únicos."""
        self.game_database = {}
        
        for user in self.users_data:
            games = user.get('owned_games', {}).get('games', [])
            for game in games:
                app_id = str(game.get('appid', ''))
                if app_id and app_id not in self.game_database:
                    self.game_database[app_id] = {
                        'appid': app_id,
                        'name': game.get('name', f'Game {app_id}'),
                        'owners': [],
                        'total_playtime': 0,
                        'avg_playtime': 0
                    }
                
                if app_id:
                    self.game_database[app_id]['owners'].append(user['steam_id'])
                    self.game_database[app_id]['total_playtime'] += game.get('playtime_forever', 0)
        
        # Calcular tempo médio de jogo
        for game in self.game_database.values():
            if len(game['owners']) > 0:
                game['avg_playtime'] = game['total_playtime'] / len(game['owners'])
    
    def calculate_user_similarity(self, user1: Dict, user2: Dict) -> float:
        """
        Calcula similaridade entre dois usuários baseada em:
        - Jogos em comum
        - Tempo de jogo similar
        - Localização geográfica
        - Conexões de amizade
        """
        similarity = 0.0
        
        # Jogos em comum (peso: 40%)
        games1 = {str(g['appid']): g['playtime_forever'] for g in user1.get('owned_games', {}).get('games', [])}
        games2 = {str(g['appid']): g['playtime_forever'] for g in user2.get('owned_games', {}).get('games', [])}
        
        common_games = set(games1.keys()) & set(games2.keys())
        total_games = set(games1.keys()) | set(games2.keys())
        
        if total_games:
            jaccard_similarity = len(common_games) / len(total_games)
            similarity += 0.4 * jaccard_similarity
            
            # Similaridade de tempo de jogo nos jogos em comum (peso: 20%)
            if common_games:
                time_similarities = []
                for game in common_games:
                    time1 = games1[game]
                    time2 = games2[game]
                    if time1 + time2 > 0:
                        time_sim = 1 - abs(time1 - time2) / (time1 + time2)
                        time_similarities.append(time_sim)
                
                if time_similarities:
                    similarity += 0.2 * (sum(time_similarities) / len(time_similarities))
        
        # Localização geográfica (peso: 15%)
        country1 = user1.get('profile_info', {}).get('loccountrycode', '')
        country2 = user2.get('profile_info', {}).get('loccountrycode', '')
        if country1 and country2 and country1 == country2:
            similarity += 0.15
        
        # Conexão de amizade direta (peso: 25%)
        friends1 = set(user1.get('friends_list', {}).get('friends', []))
        if user2['steam_id'] in friends1:
            similarity += 0.25
        
        return min(similarity, 1.0)
    
    def create_similarity_matrix(self):
        """Cria matriz de similaridade entre todos os usuários."""
        logger.info("Calculando matriz de similaridade...")
        
        self.user_similarity_matrix = {}
        
        for i, user1 in enumerate(self.users_data):
            self.user_similarity_matrix[user1['steam_id']] = {}
            
            for j, user2 in enumerate(self.users_data):
                if i != j:
                    similarity = self.calculate_user_similarity(user1, user2)
                    self.user_similarity_matrix[user1['steam_id']][user2['steam_id']] = similarity
                else:
                    self.user_similarity_matrix[user1['steam_id']][user2['steam_id']] = 1.0
    
    def cluster_users(self, num_clusters: int = 5, similarity_threshold: float = 0.3):
        """
        Agrupa usuários em clusters baseado em similaridade.
        Usa um algoritmo de clustering baseado em densidade.
        """
        logger.info(f"Criando {num_clusters} clusters de usuários...")
        
        # Inicializar clusters
        self.clusters = []
        unassigned_users = set(user['steam_id'] for user in self.users_data)
        
        # Para cada cluster desejado
        for cluster_id in range(num_clusters):
            if not unassigned_users:
                break
                
            # Escolher usuário seed (mais conectado entre os não assignados)
            seed_user = max(unassigned_users, 
                          key=lambda u: sum(1 for other in unassigned_users 
                                          if other != u and 
                                          self.user_similarity_matrix[u][other] > similarity_threshold))
            
            # Criar cluster começando com o seed
            cluster = {
                'id': cluster_id,
                'users': [seed_user],
                'characteristics': {},
                'recommended_games': []
            }
            
            unassigned_users.remove(seed_user)
            
            # Adicionar usuários similares ao cluster
            for user_id in list(unassigned_users):
                # Calcular similaridade média com usuários já no cluster
                avg_similarity = sum(self.user_similarity_matrix[user_id][cluster_user] 
                                   for cluster_user in cluster['users']) / len(cluster['users'])
                
                if avg_similarity > similarity_threshold:
                    cluster['users'].append(user_id)
                    unassigned_users.remove(user_id)
            
            self.clusters.append(cluster)
        
        # Adicionar usuários não assignados ao cluster mais similar
        for user_id in unassigned_users:
            best_cluster = max(self.clusters, 
                             key=lambda c: max(self.user_similarity_matrix[user_id][cu] for cu in c['users']))
            best_cluster['users'].append(user_id)
    
    def analyze_cluster_characteristics(self):
        """Analisa características de cada cluster."""
        for cluster in self.clusters:
            cluster_users = [user for user in self.users_data if user['steam_id'] in cluster['users']]
            
            # Jogos mais populares no cluster
            game_popularity = Counter()
            total_playtime_by_game = defaultdict(int)
            
            for user in cluster_users:
                games = user.get('owned_games', {}).get('games', [])
                for game in games:
                    app_id = str(game.get('appid', ''))
                    if app_id:
                        game_popularity[app_id] += 1
                        total_playtime_by_game[app_id] += game.get('playtime_forever', 0)
            
            # Características do cluster
            characteristics = {
                'size': len(cluster['users']),
                'avg_games_per_user': sum(len(u.get('owned_games', {}).get('games', [])) for u in cluster_users) / len(cluster_users),
                'most_popular_games': game_popularity.most_common(10),
                'countries': Counter(u.get('profile_info', {}).get('loccountrycode', 'Unknown') for u in cluster_users),
                'avg_playtime_per_user': sum(sum(g.get('playtime_forever', 0) for g in u.get('owned_games', {}).get('games', [])) for u in cluster_users) / len(cluster_users)
            }
            
            cluster['characteristics'] = characteristics
    
    def generate_game_recommendations(self):
        """Gera recomendações de jogos para cada cluster."""
        for cluster in self.clusters:
            cluster_users = [user for user in self.users_data if user['steam_id'] in cluster['users']]
            
            # Jogos que o cluster possui
            cluster_games = set()
            for user in cluster_users:
                user_games = {str(g['appid']) for g in user.get('owned_games', {}).get('games', [])}
                cluster_games.update(user_games)
            
            # Calcular score de recomendação para cada jogo não possuído
            recommendations = []
            
            for app_id, game_info in self.game_database.items():
                if app_id not in cluster_games and len(game_info['owners']) > 1:
                    # Score baseado em:
                    # 1. Popularidade geral do jogo
                    # 2. Tempo médio de jogo (jogos mais envolventes)
                    # 3. Posse por usuários similares
                    
                    popularity_score = len(game_info['owners']) / len(self.users_data)
                    engagement_score = min(game_info['avg_playtime'] / 1000, 1.0)  # Normalizar
                    
                    # Verificar se usuários similares possuem o jogo
                    similarity_score = 0
                    similar_owners = 0
                    
                    for owner_id in game_info['owners']:
                        if owner_id not in cluster['users']:
                            # Calcular similaridade média com o cluster
                            avg_sim = sum(self.user_similarity_matrix.get(owner_id, {}).get(cluster_user, 0) 
                                        for cluster_user in cluster['users']) / len(cluster['users'])
                            similarity_score += avg_sim
                            similar_owners += 1
                    
                    if similar_owners > 0:
                        similarity_score /= similar_owners
                    
                    total_score = (0.3 * popularity_score + 
                                 0.3 * engagement_score + 
                                 0.4 * similarity_score)
                    
                    recommendations.append({
                        'appid': app_id,
                        'name': game_info['name'],
                        'score': total_score,
                        'popularity': popularity_score,
                        'engagement': engagement_score,
                        'similarity': similarity_score
                    })
            
            # Ordenar por score e pegar top 10
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            cluster['recommended_games'] = recommendations[:10]
    
    def export_for_visualization(self, output_file: str = "steam_graph_data.json"):
        """Exporta dados processados para visualização."""
        
        # Preparar dados dos nós (usuários)
        nodes = []
        for user in self.users_data:
            # Encontrar cluster do usuário
            user_cluster = next((i for i, c in enumerate(self.clusters) if user['steam_id'] in c['users']), 0)
            
            node = {
                'id': user['steam_id'],
                'name': user.get('profile_info', {}).get('personaname', 'Unknown'),
                'country': user.get('profile_info', {}).get('loccountrycode', 'Unknown'),
                'games_count': len(user.get('owned_games', {}).get('games', [])),
                'total_playtime': sum(g.get('playtime_forever', 0) for g in user.get('owned_games', {}).get('games', [])),
                'friends_count': user.get('friends_list', {}).get('friend_count', 0),
                'cluster': user_cluster
            }
            nodes.append(node)
        
        # Preparar dados das arestas (amizades)
        edges = []
        user_ids = {user['steam_id'] for user in self.users_data}
        
        for user in self.users_data:
            user_id = user['steam_id']
            friends = user.get('friends_list', {}).get('friends', [])
            
            for friend_id in friends:
                if friend_id in user_ids and user_id < friend_id:  # Evitar duplicatas
                    similarity = self.user_similarity_matrix.get(user_id, {}).get(friend_id, 0)
                    
                    edge = {
                        'source': user_id,
                        'target': friend_id,
                        'similarity': similarity
                    }
                    edges.append(edge)
        
        # Dados para exportação
        export_data = {
            'nodes': nodes,
            'edges': edges,
            'clusters': self.clusters,
            'statistics': {
                'total_users': len(self.users_data),
                'total_games': len(self.game_database),
                'total_friendships': len(edges),
                'clusters_count': len(self.clusters)
            }
        }
        
        # Salvar arquivo
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dados exportados para {output_file}")
        return export_data
    
    def analyze(self, num_clusters: int = 5):
        """Executa análise completa dos dados."""
        logger.info("Iniciando análise do grafo Steam...")
        
        if not self.load_data():
            return False
        
        self.create_similarity_matrix()
        self.cluster_users(num_clusters)
        self.analyze_cluster_characteristics()
        self.generate_game_recommendations()
        
        # Exportar dados
        data = self.export_for_visualization()
        
        logger.info("Análise concluída!")
        logger.info(f"Clusters criados: {len(self.clusters)}")
        for i, cluster in enumerate(self.clusters):
            logger.info(f"  Cluster {i}: {len(cluster['users'])} usuários")
        
        return data


def main():
    """Função principal para análise dos dados."""
    logging.basicConfig(level=logging.INFO)
    
    analyzer = SteamGraphAnalyzer()
    data = analyzer.analyze(num_clusters=6)
    
    if data:
        print(f"\n📊 Análise Concluída:")
        print(f"   Usuários: {data['statistics']['total_users']}")
        print(f"   Jogos únicos: {data['statistics']['total_games']}")
        print(f"   Amizades: {data['statistics']['total_friendships']}")
        print(f"   Clusters: {data['statistics']['clusters_count']}")
        
        print(f"\n🎯 Clusters de Usuários:")
        for i, cluster in enumerate(data['clusters']):
            chars = cluster['characteristics']
            print(f"   Cluster {i}: {chars['size']} usuários")
            print(f"     - Jogos médios por usuário: {chars['avg_games_per_user']:.1f}")
            print(f"     - Tempo médio de jogo: {chars['avg_playtime_per_user']:.0f} min")
            print(f"     - Top países: {dict(chars['countries'].most_common(3))}")
            
            if cluster['recommended_games']:
                print(f"     - Top recomendação: {cluster['recommended_games'][0]['name']}")


if __name__ == "__main__":
    main()
