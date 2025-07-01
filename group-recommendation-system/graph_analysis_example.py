#!/usr/bin/env python3
"""
Exemplo de Análise de Grafo de Amizades da Steam

Este script demonstra como analisar os dados coletados pelo steam_user_miner
para criar e analisar o grafo de relacionamentos entre usuários.

Dependências adicionais:
pip install networkx matplotlib pandas seaborn
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
import numpy as np


def load_steam_data(filename: str = 'steam_user_data.json') -> list:
    """Carrega os dados coletados do arquivo JSON."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado!")
        return []


def create_friendship_graph(users_data: list) -> nx.Graph:
    """
    Cria um grafo de amizades a partir dos dados coletados.
    
    Args:
        users_data: Lista de dados de usuários do steam_user_miner
        
    Returns:
        Grafo NetworkX com usuários como nós e amizades como arestas
    """
    G = nx.Graph()
    
    # Criar conjunto de todos os usuários coletados
    collected_users = {user['steam_id'] for user in users_data}
    
    # Adicionar nós com atributos do perfil
    for user in users_data:
        user_id = user['steam_id']
        profile = user['profile_info']
        
        # Adicionar nó com atributos úteis
        G.add_node(user_id, 
                  name=profile.get('personaname', 'Unknown'),
                  country=profile.get('loccountrycode', 'Unknown'),
                  game_count=user['owned_games'].get('game_count', 0),
                  friend_count=user['friends_list'].get('friend_count', 0))
    
    # Adicionar arestas de amizade (apenas entre usuários coletados)
    for user in users_data:
        user_id = user['steam_id']
        friends = user['friends_list'].get('friends', [])
        
        for friend_id in friends:
            # Só criar aresta se ambos os usuários estão no dataset
            if friend_id in collected_users and user_id != friend_id:
                G.add_edge(user_id, friend_id)
    
    return G


def analyze_graph_metrics(G: nx.Graph) -> dict:
    """Calcula métricas básicas do grafo."""
    metrics = {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'is_connected': nx.is_connected(G),
        'connected_components': nx.number_connected_components(G)
    }
    
    if metrics['is_connected']:
        metrics['diameter'] = nx.diameter(G)
        metrics['avg_path_length'] = nx.average_shortest_path_length(G)
    else:
        # Para grafos desconectados, usar o maior componente
        largest_cc = max(nx.connected_components(G), key=len)
        subgraph = G.subgraph(largest_cc)
        metrics['largest_component_size'] = len(largest_cc)
        metrics['largest_component_diameter'] = nx.diameter(subgraph)
        metrics['largest_component_avg_path'] = nx.average_shortest_path_length(subgraph)
    
    metrics['avg_clustering'] = nx.average_clustering(G)
    
    return metrics


def find_influential_users(G: nx.Graph, top_n: int = 10) -> dict:
    """Encontra usuários mais influentes usando diferentes métricas de centralidade."""
    
    # Diferentes métricas de centralidade
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)
    
    # Top usuários por cada métrica
    top_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_closeness = sorted(closeness_centrality.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    return {
        'degree_centrality': top_degree,
        'betweenness_centrality': top_betweenness,
        'closeness_centrality': top_closeness
    }


def analyze_communities(G: nx.Graph):
    """Detecta comunidades no grafo."""
    try:
        # Usar algoritmo de Louvain para detecção de comunidades
        import community as community_louvain
        partition = community_louvain.best_partition(G)
        
        # Contar tamanho das comunidades
        community_sizes = Counter(partition.values())
        
        return {
            'num_communities': len(community_sizes),
            'community_sizes': dict(community_sizes),
            'partition': partition
        }
    except ImportError:
        print("Para análise de comunidades, instale: pip install python-louvain")
        return None


def visualize_graph(G: nx.Graph, filename: str = 'steam_friendship_graph.png'):
    """Cria visualização básica do grafo."""
    plt.figure(figsize=(12, 8))
    
    # Layout do grafo
    if G.number_of_nodes() < 100:
        pos = nx.spring_layout(G, k=1, iterations=50)
    else:
        # Para grafos grandes, usar layout mais rápido
        pos = nx.spring_layout(G, k=3, iterations=20)
    
    # Tamanho dos nós baseado no número de amigos
    node_sizes = [G.nodes[node].get('friend_count', 1) * 2 for node in G.nodes()]
    
    # Desenhar o grafo
    nx.draw(G, pos, 
            node_size=node_sizes,
            node_color='lightblue',
            edge_color='gray',
            alpha=0.7,
            with_labels=False)
    
    plt.title(f"Grafo de Amizades da Steam\n{G.number_of_nodes()} usuários, {G.number_of_edges()} conexões")
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()


def create_statistics_report(users_data: list, G: nx.Graph):
    """Cria relatório estatístico dos dados."""
    # Estatísticas gerais
    total_users = len(users_data)
    total_games = sum(user['owned_games'].get('game_count', 0) for user in users_data)
    total_friends = sum(user['friends_list'].get('friend_count', 0) for user in users_data)
    
    # Distribuição de países
    countries = [user['profile_info'].get('loccountrycode', 'Unknown') for user in users_data]
    country_dist = Counter(countries)
    
    # Estatísticas de jogos
    game_counts = [user['owned_games'].get('game_count', 0) for user in users_data]
    friend_counts = [user['friends_list'].get('friend_count', 0) for user in users_data]
    
    print("=== RELATÓRIO DE ESTATÍSTICAS ===")
    print(f"Total de usuários coletados: {total_users}")
    print(f"Total de jogos (somados): {total_games}")
    print(f"Média de jogos por usuário: {total_games/total_users:.1f}")
    print(f"Total de amizades (somadas): {total_friends}")
    print(f"Média de amigos por usuário: {total_friends/total_users:.1f}")
    print()
    
    print("Top 5 países por número de usuários:")
    for country, count in country_dist.most_common(5):
        print(f"  {country}: {count} usuários")
    print()
    
    print("Estatísticas de jogos:")
    print(f"  Mínimo: {min(game_counts)} jogos")
    print(f"  Máximo: {max(game_counts)} jogos")
    print(f"  Mediana: {np.median(game_counts):.1f} jogos")
    print()
    
    print("Estatísticas de amigos:")
    print(f"  Mínimo: {min(friend_counts)} amigos")
    print(f"  Máximo: {max(friend_counts)} amigos")
    print(f"  Mediana: {np.median(friend_counts):.1f} amigos")


def main():
    """Função principal para executar todas as análises."""
    print("🔍 Carregando dados da Steam...")
    users_data = load_steam_data()
    
    if not users_data:
        print("❌ Nenhum dado encontrado. Execute primeiro o steam_user_miner.py")
        return
    
    print(f"✅ {len(users_data)} usuários carregados")
    
    print("\n📊 Criando relatório estatístico...")
    create_statistics_report(users_data, None)
    
    print("\n🕸️ Construindo grafo de amizades...")
    G = create_friendship_graph(users_data)
    
    print(f"✅ Grafo criado com {G.number_of_nodes()} nós e {G.number_of_edges()} arestas")
    
    print("\n📈 Calculando métricas do grafo...")
    metrics = analyze_graph_metrics(G)
    
    print("=== MÉTRICAS DO GRAFO ===")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")
    
    print("\n🌟 Encontrando usuários influentes...")
    influential = find_influential_users(G, top_n=5)
    
    print("\nTop 5 usuários por centralidade de grau:")
    for user_id, centrality in influential['degree_centrality']:
        name = G.nodes[user_id].get('name', 'Unknown')
        print(f"  {name} ({user_id}): {centrality:.4f}")
    
    print("\n🏘️ Analisando comunidades...")
    communities = analyze_communities(G)
    if communities:
        print(f"Número de comunidades detectadas: {communities['num_communities']}")
        print("Tamanho das maiores comunidades:")
        sorted_communities = sorted(communities['community_sizes'].items(), 
                                   key=lambda x: x[1], reverse=True)
        for comm_id, size in sorted_communities[:5]:
            print(f"  Comunidade {comm_id}: {size} usuários")
    
    print("\n🎨 Criando visualização...")
    if G.number_of_nodes() <= 500:  # Só visualizar se não for muito grande
        visualize_graph(G)
        print("✅ Visualização salva como 'steam_friendship_graph.png'")
    else:
        print("⚠️ Grafo muito grande para visualização (>500 nós)")
    
    print("\n✅ Análise completa!")


if __name__ == "__main__":
    main()
