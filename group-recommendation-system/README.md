# Steam User Data Miner 🎮

Este projeto é um script robusto em Python para mineração automatizada de dados de usuários da Steam Web API. Utiliza algoritmo de busca em largura (BFS) para coletar informações detalhadas de 1.000 usuários únicos através do grafo de amizades da Steam.

## 🚀 Funcionalidades

- **Coleta de Dados em Grafo**: Inicia com um SteamID e navega pela rede de amizades
- **Dados Completos**: Perfil, jogos possuídos e tempo de jogo de cada usuário
- **Tratamento Robusto de Erros**: Lida com perfis privados, rate limiting e erros de rede
- **Progresso Visual**: Barra de progresso em tempo real com tqdm
- **Backup Automático**: Salva progresso a cada 50 usuários processados
- **Configuração Flexível**: Variáveis de ambiente ou entrada interativa

## 📋 Pré-requisitos

1. **Python 3.7+**
2. **Steam Web API Key**: Obtenha em [Steam Web API Key](https://steamcommunity.com/dev/apikey)
3. **SteamID inicial**: Um SteamID de 64 bits para começar a coleta

## 🛠️ Instalação

1. **Clone ou baixe o projeto**:
```bash
git clone <repository-url>
cd steam-user-miner
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente** (opcional):
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

## ⚙️ Configuração

### Opção 1: Variáveis de Ambiente
Edite o arquivo `.env`:
```
STEAM_API_KEY=sua_chave_da_api_aqui
INITIAL_STEAM_ID=76561197960287930
```

### Opção 2: Entrada Interativa
Se não configurar as variáveis de ambiente, o script solicitará as informações quando executado.

## 🎯 Uso

### Opção 1: Pipeline Completa (Recomendado)
Execute o script completo que inclui coleta, análise e visualização:
```bash
python run_analysis.py
```

### Opção 2: Execução Manual
1. **Colete os dados**:
```bash
python steam_user_miner.py
```

2. **Analise e gere visualização**:
```bash
python steam_graph_analyzer.py
```

3. **Abra a visualização**:
   - Abra `steam_graph_visualization.html` no navegador, ou
   - Execute um servidor local: `python -m http.server 8000`

### 🌐 Visualização Interativa

A visualização HTML oferece:
- **Grafo Interativo**: Navegue pelo grafo de usuários com zoom e pan
- **Filtros Dinâmicos**: Filtre por cluster, país, número de jogos e similaridade
- **Clusters Visuais**: Cada cluster tem cor única e pode ser destacado
- **Recomendações**: Veja jogos recomendados para cada cluster
- **Métricas em Tempo Real**: Estatísticas atualizadas conforme os filtros
- **Tooltips Informativos**: Detalhes de cada usuário ao passar o mouse

O script irá:
1. Solicitar/carregar a API Key e SteamID inicial
2. Começar a coleta de dados com barra de progresso
3. Salvar backups a cada 50 usuários
4. Analisar dados e criar clusters de afinidade
5. Gerar recomendações de jogos por cluster
6. Criar visualização interativa do grafo
7. Gerar o arquivo final `steam_user_data.json`

## 📊 Dados Coletados

Para cada usuário, o script coleta:

### Informações do Perfil
- SteamID, nome de usuário, URL do perfil
- Avatar, nome real, localização
- Status da conta e visibilidade

### Jogos Possuídos
- Lista completa de jogos
- Tempo de jogo (em minutos e horas)
- AppID de cada jogo

### Lista de Amigos
- SteamIDs de todos os amigos
- Contagem total de amigos
- Dados para construção de grafo de relacionamentos

### Estrutura do JSON de Saída
```json
[
  {
    "steam_id": "76561197960287930",
    "profile_info": {
      "personaname": "username",
      "profileurl": "https://steamcommunity.com/id/username/",
      "avatarfull": "https://avatars.steamstatic.com/...",
      "loccountrycode": "US"
    },
    "owned_games": {
      "game_count": 550,
      "games": [
        {
          "appid": 400,
          "playtime_forever": 1200,
          "playtime_forever_hr": 20.0
        }
      ]
    },
    "friends_list": {
      "friend_count": 150,
      "friends": [
        "76561197960287931",
        "76561197960287932",
        "76561197960287933"
      ]
    }
  }
]
```

## 🔧 Configurações Avançadas

### Parâmetros Ajustáveis (no código)
- `target_users`: Número de usuários a coletar (padrão: 1000)
- `request_delay`: Delay entre requisições (padrão: 0.5s)
- `max_retries`: Tentativas de retry (padrão: 3)

### Rate Limiting
O script inclui delays automáticos para evitar bloqueios da API:
- 0.5s entre requisições diferentes
- 1s entre tentativas de retry
- Backoff exponencial em caso de erros

## 🛡️ Tratamento de Erros

- **Perfis Privados**: Detecta e pula automaticamente
- **Erros de Rede**: Retry automático com backoff
- **Rate Limiting**: Delays preventivos
- **Interrupção**: Salva dados parciais em caso de Ctrl+C

## 📁 Arquivos Gerados

### Dados Brutos
- `steam_user_data.json`: Dados finais de todos os usuários
- `steam_user_data_backup_N.json`: Backups automáticos a cada 50 usuários
- `steam_user_data_partial.json`: Dados parciais se interrompido

### Análise e Visualização
- `steam_graph_data.json`: Dados processados para visualização (nós, arestas, clusters)
- `steam_graph_visualization.html`: Página HTML interativa com o grafo
- `steam_graph_data_example.json`: Arquivo de exemplo para testar a visualização

### Scripts Auxiliares
- `run_analysis.py`: Pipeline completa de análise
- `steam_graph_analyzer.py`: Algoritmos de clustering e recomendação
- `examples.py`: Exemplos de uso e análise simples

## 📊 Análise de Grafo de Amizades

Com os dados coletados, você pode criar um grafo de relacionamentos usando a `friends_list` de cada usuário:

### Exemplo de Análise com NetworkX
```python
import json
import networkx as nx

# Carregar dados
with open('steam_user_data.json', 'r') as f:
    users_data = json.load(f)

# Criar grafo
G = nx.Graph()

# Adicionar nós e arestas
for user in users_data:
    user_id = user['steam_id']
    G.add_node(user_id, **user['profile_info'])
    
    # Adicionar conexões de amizade
    for friend_id in user['friends_list']['friends']:
        if friend_id in [u['steam_id'] for u in users_data]:
            G.add_edge(user_id, friend_id)

# Análises possíveis
print(f"Número de nós: {G.number_of_nodes()}")
print(f"Número de arestas: {G.number_of_edges()}")
print(f"Densidade do grafo: {nx.density(G):.4f}")

# Centralidade
centrality = nx.degree_centrality(G)
most_connected = max(centrality, key=centrality.get)
print(f"Usuário mais conectado: {most_connected}")
```

### Métricas de Grafo Disponíveis
- **Centralidade de grau**: Usuários com mais amigos
- **Centralidade de proximidade**: Usuários mais próximos de outros
- **Detecção de comunidades**: Grupos de amigos conectados
- **Caminho mais curto**: Distância entre usuários
- **Coeficiente de clustering**: Densidade de conexões locais

## 🐛 Troubleshooting

### Erro de API Key Inválida
- Verifique se a API Key está correta
- Confirme que você tem uma conta Steam válida

### SteamID Inválido
- Use SteamID de 64 bits (17 dígitos)
- Teste com: 76561197960287930 (Gabe Newell)

### Rate Limiting
- O script já inclui delays apropriados
- Se persistir, aumente `request_delay` no código

### Poucos Dados Coletados
- Alguns usuários têm perfis privados
- O script continuará até encontrar usuários públicos

## 📝 Logs

O script gera logs detalhados incluindo:
- Progresso da coleta
- Usuários com perfis privados
- Erros de rede e recuperação
- Estatísticas finais

## 🤝 Contribuições

Melhorias são bem-vindas! Áreas de interesse:
- Otimização de performance
- Coleta de dados adicionais da Steam API
- Análises avançadas de grafo e comunidades
- Interface gráfica para visualização
- Algoritmos de recomendação baseados em amizades
- Detecção de padrões de comportamento de jogadores
- Machine Learning para melhor clustering
- Análise temporal de dados de jogos
- Integração com outras APIs de jogos
- Métricas avançadas de engajamento

## 📄 Licença

Este projeto é de uso educacional e deve respeitar os Termos de Serviço da Steam.

## ⚠️ Avisos Importantes

1. **Respeite os Termos da Steam**: Use os dados coletados de forma ética
2. **Rate Limiting**: Não remova os delays para evitar bloqueios
3. **Dados Privados**: O script respeita perfis privados automaticamente
4. **Backup**: Sempre mantenha backups dos dados coletados
