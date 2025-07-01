#!/usr/bin/env python3
"""
Teste de Visualização Steam Graph

Script para testar a visualização com dados de exemplo.
"""

import json
import webbrowser
import http.server
import socketserver
import threading
import time
import shutil

def create_test_data():
    """Cria dados de teste mais robustos para a visualização."""
    
    print("📊 Gerando dados de teste...")
    
    # Carregar dados exemplo
    with open('steam_graph_data_example.json', 'r', encoding='utf-8') as f:
        example_data = json.load(f)
    
    # Copiar para arquivo principal se não existir
    if not os.path.exists('steam_graph_data.json'):
        shutil.copy('steam_graph_data_example.json', 'steam_graph_data.json')
        print("✅ Dados de exemplo copiados para steam_graph_data.json")
    
    return True

def start_server_and_open():
    """Inicia servidor local e abre a visualização."""
    
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    def start_server():
        try:
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                print(f"🌐 Servidor iniciado em http://localhost:{PORT}")
                httpd.serve_forever()
        except OSError:
            print(f"❌ Porta {PORT} já está em uso. Tente uma porta diferente.")
    
    # Iniciar servidor em thread separada
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    time.sleep(2)  # Aguardar servidor iniciar
    
    # Abrir navegador
    url = f"http://localhost:{PORT}/steam_graph_visualization.html"
    webbrowser.open(url)
    
    print("🖥️  Visualização aberta no navegador!")
    print("🎮 Teste as funcionalidades:")
    print("   • Zoom e pan no grafo")
    print("   • Clique nos nós para ver detalhes")
    print("   • Use os filtros na barra lateral")
    print("   • Selecione clusters para ver recomendações")
    print()
    print("⚠️  Pressione Ctrl+C para parar o servidor")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Servidor parado!")

def main():
    """Função principal do teste."""
    
    print("🎮" + "="*50 + "🎮")
    print("    TESTE DE VISUALIZAÇÃO STEAM GRAPH")
    print("🎮" + "="*50 + "🎮")
    print()
    
    # Verificar arquivos necessários
    required_files = [
        'steam_graph_visualization.html',
        'steam_graph_data_example.json'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("❌ Arquivos necessários não encontrados:")
        for f in missing_files:
            print(f"   - {f}")
        print()
        print("📋 Certifique-se de que todos os arquivos estão presentes.")
        return
    
    # Criar dados de teste
    if not create_test_data():
        return
    
    print("🚀 Iniciando servidor de teste...")
    print("   A visualização será aberta automaticamente no navegador.")
    print()
    
    start_server_and_open()

if __name__ == "__main__":
    import os
    main()
