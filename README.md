# Monitor de Servidor PostgreSQL

Ferramenta de monitoramento que verifica o load average do sistema a cada 10 segundos e, quando este ultrapassa um limiar definido pelo usuário, captura e salva as consultas ativas do PostgreSQL em arquivos de log a cada minuto até que o load volte ao normal.

## Características

- Monitoramento contínuo do load average do sistema
- Interface de terminal interativa construída com a biblioteca Textual
- Captura automática de consultas ativas do PostgreSQL durante períodos de load elevado
- Visualização fácil dos logs de consultas coletados
- Configuração do limiar de load average diretamente na interface

## Requisitos

- Python 3.8 ou superior
- PostgreSQL com acesso para consultar `pg_stat_activity`
- Dependências Python (instaladas automaticamente com uv):
  - textual
  - psycopg2-binary
  - psutil

## Instalação

Recomendamos o uso do `uv` para gerenciar o ambiente virtual e instalar dependências:

```bash
# Criar e ativar um ambiente virtual (opcional mas recomendado)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate.bat  # Windows

# Instalar dependências usando uv
uv pip install -e .
```

## Uso

Execute o programa diretamente:

```bash
python main.py
```

Ou use argumentos de linha de comando para configuração:

```bash
python main.py --threshold 3.0 --host localhost --port 5432 --user postgres --database mydb
```

Argumentos disponíveis:

- `-t, --threshold`: Limiar de load average (padrão: 2.0)
- `--host`: Host do PostgreSQL (padrão: localhost)
- `--port`: Porta do PostgreSQL (padrão: 5432)
- `--user`: Usuário do PostgreSQL (padrão: postgres)
- `--database`: Banco de dados do PostgreSQL (padrão: postgres)

## Interface

A interface é dividida em duas seções principais:

### Seção esquerda:

1. **Status do Sistema**: Exibe informações sobre o load average atual, uso de CPU e memória.
2. **Configurações de Monitoramento**: Permite configurar o limiar de load average e iniciar/parar o monitoramento.

### Seção direita:

1. **Logs de Consultas PostgreSQL**: Exibe uma lista dos arquivos de log gerados durante períodos de load elevado. Clique em um arquivo para visualizar seu conteúdo.

## Funcionamento

1. O programa verifica o load average do sistema a cada 10 segundos.
2. Quando o load average de 1 minuto ultrapassa o limiar configurado, o programa entra em modo de "load alto".
3. No modo de "load alto", o programa captura e salva as consultas ativas do PostgreSQL a cada minuto.
4. Os logs são armazenados no diretório `logs/` com timestamp no formato `pg_queries_YYYYMMDD_HHMMSS.log`.
5. Quando o load average volta a ficar abaixo do limiar, o programa retoma o monitoramento normal.

## Comandos rápidos

- `q`: Sair da aplicação