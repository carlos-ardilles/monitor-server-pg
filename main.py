#!/usr/bin/env python3
"""
Monitor de Servidor PostgreSQL
------------------------------

Este programa monitora o load average do sistema e, quando ultrapassa
um limiar definido pelo usuário, captura e salva as consultas ativas
do PostgreSQL em arquivos de log.

Autor: Equipe de Desenvolvimento
Data: Abril 2025
"""

import sys
import os
import argparse
from src.ui import MonitorApp
from dotenv import load_dotenv


def main():
    """Função principal que inicia a aplicação de monitoramento"""
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()

    parser = argparse.ArgumentParser(
        description='Monitor de Load Average e Queries PostgreSQL'
    )

    parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=float(os.environ.get('MONITOR_THRESHOLD', '2.0')),
        help=f'Limiar de load average para ativar o monitoramento (padrão: {os.environ.get("MONITOR_THRESHOLD", "2.0")})'
    )

    parser.add_argument(
        '--host',
        default=os.environ.get('PGHOST', 'localhost'),
        help=f'Host do PostgreSQL (padrão: {os.environ.get("PGHOST", "localhost")})'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=int(os.environ.get('PGPORT', '5432')),
        help=f'Porta do PostgreSQL (padrão: {os.environ.get("PGPORT", "5432")})'
    )

    parser.add_argument(
        '--user',
        default=os.environ.get('PGUSER', 'postgres'),
        help=f'Usuário do PostgreSQL (padrão: {os.environ.get("PGUSER", "postgres")})'
    )

    parser.add_argument(
        '--database',
        default=os.environ.get('PGDATABASE', 'postgres'),
        help=f'Banco de dados do PostgreSQL (padrão: {os.environ.get("PGDATABASE", "postgres")})'
    )

    args = parser.parse_args()

    # Atualiza as variáveis de ambiente para conexão com o PostgreSQL
    os.environ['PGHOST'] = args.host
    os.environ['PGPORT'] = str(args.port)
    os.environ['PGUSER'] = args.user
    os.environ['PGDATABASE'] = args.database

    # Define o valor de MONITOR_THRESHOLD para que outros módulos possam acessá-lo
    os.environ['MONITOR_THRESHOLD'] = str(args.threshold)

    # Define os intervalos de verificação e captura
    os.environ['MONITOR_CHECK_INTERVAL'] = os.environ.get(
        'MONITOR_CHECK_INTERVAL', '10')
    os.environ['MONITOR_CAPTURE_INTERVAL'] = os.environ.get(
        'MONITOR_CAPTURE_INTERVAL', '60')

    # Cria o diretório de logs se não existir
    os.makedirs(os.path.join(os.getcwd(), "logs"), exist_ok=True)

    # Inicia a aplicação
    app = MonitorApp()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAplicação encerrada pelo usuário.")
        sys.exit(0)
