#!/usr/bin/env python3
"""
Steam Graph Pipeline

Script completo para executar a análise de dados Steam e gerar visualização.

Autor: Sistema automatizado
Data: 2025-06-28
"""

import os
import sys
import logging
from steam_graph_analyzer import SteamGraphAnalyzer

def main():
    """Executa a pipeline completa de análise."""
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🎮" + "="*60 + "🎮")
    print("    STEAM GRAPH ANALYSIS & VISUALIZATION PIPELINE")
    print("🎮" + "="*60 + "🎮")
    print()
    
    # Verificar se arquivo de dados existe
    data_file = "steam_user_data.json"
    if not os.path.exists(data_file):
        print("❌ Arquivo steam_user_data.json não encontrado!")
        print("   Execute primeiro o steam_user_miner.py para coletar os dados.")
        print()
        
        # Perguntar se quer executar o minerador
        response = input("🤔 Deseja executar o minerador agora? (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            print("🚀 Iniciando minerador de dados Steam...")
            try:
                from steam_user_miner import main as miner_main
                miner_main()
            except ImportError:
                print("❌ Erro ao importar steam_user_miner.py")
                return
        else:
            print("📋 Para executar o minerador manualmente:")
            print("   python steam_user_miner.py")
            return
    
    # Configurar parâmetros de análise
    print("⚙️  Configurando análise...")
    
    # Perguntar número de clusters
    try:
        num_clusters = int(input("📊 Quantos clusters deseja criar? (padrão: 6): ") or "6")
        if num_clusters < 2 or num_clusters > 20:
            num_clusters = 6
            print(f"   Usando {num_clusters} clusters (valor ajustado)")
    except ValueError:
        num_clusters = 6
        print(f"   Usando {num_clusters} clusters (valor padrão)")
    
    print()
    print("🔍 Iniciando análise dos dados...")
    
    # Executar análise
    analyzer = SteamGraphAnalyzer(data_file)
    result = analyzer.analyze(num_clusters=num_clusters)
    
    if not result:
        print("❌ Erro na análise dos dados!")
        return
    
    # Mostrar estatísticas
    print()
    print("📊 RESULTADOS DA ANÁLISE:")
    print("="*50)
    
    stats = result['statistics']
    print(f"👥 Total de usuários: {stats['total_users']}")
    print(f"🎮 Jogos únicos: {stats['total_games']}")
    print(f"🤝 Conexões de amizade: {stats['total_friendships']}")
    print(f"📈 Clusters criados: {stats['clusters_count']}")
    print()
    
    # Mostrar informações dos clusters
    print("🎯 CLUSTERS DE USUÁRIOS:")
    print("-"*40)
    
    for i, cluster in enumerate(result['clusters']):
        chars = cluster['characteristics']
        top_country = chars['countries'].most_common(1)[0] if chars['countries'] else ('N/A', 0)
        
        print(f"🔹 Cluster {i}:")
        print(f"   Usuários: {chars['size']}")
        print(f"   Jogos médios: {chars['avg_games_per_user']:.1f}")
        print(f"   Tempo médio: {chars['avg_playtime_per_user']:.0f} min")
        print(f"   País principal: {top_country[0]} ({top_country[1]} usuários)")
        
        if cluster['recommended_games']:
            top_rec = cluster['recommended_games'][0]
            print(f"   Top recomendação: {top_rec['name']} (score: {top_rec['score']:.2f})")
        print()
    
    # Verificar se a visualização já existe
    viz_file = "steam_graph_visualization.html"
    if not os.path.exists(viz_file):
        print("❌ Arquivo de visualização não encontrado!")
        print("   Certifique-se de que steam_graph_visualization.html existe.")
        return
    
    # Instruções para visualização
    print("🌐 VISUALIZAÇÃO INTERATIVA:")
    print("="*50)
    print(f"✅ Dados processados salvos em: steam_graph_data.json")
    print(f"✅ Visualização disponível em: {viz_file}")
    print()
    print("📋 Para abrir a visualização:")
    print("   1. Abra o arquivo steam_graph_visualization.html em um navegador")
    print("   2. Ou execute um servidor local:")
    print("      python -m http.server 8000")
    print("      Depois acesse: http://localhost:8000/steam_graph_visualization.html")
    print()
    
    # Perguntar se quer abrir automaticamente
    response = input("🚀 Deseja abrir a visualização agora? (s/n): ").lower()
    if response in ['s', 'sim', 'y', 'yes']:
        try:
            import webbrowser
            import http.server
            import socketserver
            import threading
            import time
            
            # Iniciar servidor local
            PORT = 8000
            Handler = http.server.SimpleHTTPRequestHandler
            
            def start_server():
                with socketserver.TCPServer(("", PORT), Handler) as httpd:
                    httpd.serve_forever()
            
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            
            time.sleep(2)  # Aguardar servidor iniciar
            
            # Abrir navegador
            url = f"http://localhost:{PORT}/steam_graph_visualization.html"
            webbrowser.open(url)
            
            print(f"🌐 Servidor iniciado em http://localhost:{PORT}")
            print("🖥️  Visualização aberta no navegador!")
            print("⚠️  Pressione Ctrl+C para parar o servidor")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Servidor parado!")
                
        except Exception as e:
            print(f"❌ Erro ao abrir visualização: {e}")
            print("   Abra manualmente o arquivo steam_graph_visualization.html")
    
    print()
    print("🎉 PIPELINE CONCLUÍDA COM SUCESSO!")
    print("="*50)
    
    # Resumo final
    print("📁 Arquivos gerados:")
    print(f"   📊 steam_user_data.json - Dados brutos dos usuários")
    print(f"   🔍 steam_graph_data.json - Dados processados para visualização")
    print(f"   🌐 steam_graph_visualization.html - Visualização interativa")
    print()
    print("🎯 Próximos passos:")
    print("   • Explore os clusters na visualização interativa")
    print("   • Analise as recomendações de jogos por cluster")
    print("   • Use os filtros para focar em grupos específicos")
    print("   • Examine as métricas de similaridade entre usuários")


if __name__ == "__main__":
    main()
