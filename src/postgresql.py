#!/usr/bin/env python
import os
import psycopg2
from datetime import datetime


class PostgresMonitor:
    def __init__(self, connection_params=None):
        """
        Inicializa o monitor PostgreSQL com os parâmetros de conexão
        Se connection_params for None, tentará usar variáveis de ambiente do arquivo .env
        """
        self.connection_params = connection_params or {
            'host': os.getenv('PGHOST', 'localhost'),
            'port': os.getenv('PGPORT', '5432'),
            'database': os.getenv('PGDATABASE', 'postgres'),
            'user': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', '')
        }
        self.conn = None

        # Define o diretório para salvar os logs
        self.log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(self.log_dir, exist_ok=True)

    def connect(self):
        """Estabelece conexão com o banco de dados PostgreSQL"""
        try:
            if self.conn is None or self.conn.closed:
                self.conn = psycopg2.connect(**self.connection_params)
            return True
        except Exception as e:
            print(f"Erro ao conectar ao PostgreSQL: {e}")
            self.conn = None
            return False

    def disconnect(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn and not self.conn.closed:
            self.conn.close()

    def get_active_queries(self):
        """Obtém as consultas ativas no PostgreSQL"""
        if not self.connect():
            return []

        try:
            cursor = self.conn.cursor()

            # Consulta para obter queries ativas no PostgreSQL
            query = """
            SELECT pid, usename, datname, client_addr,
                   state, query_start, now() - query_start AS duration,
                   wait_event_type, wait_event, query
            FROM pg_stat_activity
            WHERE state != 'idle'
              AND pid != pg_backend_pid()
            ORDER BY duration DESC;
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            # Transformar dados em dicionários para facilitar o uso
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]

            cursor.close()
            return result

        except Exception as e:
            print(f"Erro ao obter consultas ativas: {e}")
            return []

    def save_queries_to_file(self, queries, filename=None):
        """Salva as consultas em um arquivo"""
        if not queries:
            return False

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pg_queries_{timestamp}.log"

        try:
            full_path = os.path.join(self.log_dir, filename)

            with open(full_path, 'w') as f:
                f.write(
                    f"--- Consultas PostgreSQL Ativas em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")
                f.write(
                    f"Servidor: {self.connection_params['host']}:{self.connection_params['port']}\n")
                f.write(
                    f"Banco de dados: {self.connection_params['database']}\n")
                f.write(
                    f"Load Average atual: {os.getloadavg()[0]:.2f}, {os.getloadavg()[1]:.2f}, {os.getloadavg()[2]:.2f}\n\n")

                for i, query_data in enumerate(queries, 1):
                    f.write(f"[Query {i}]\n")
                    f.write(f"PID: {query_data.get('pid')}\n")
                    f.write(f"Usuário: {query_data.get('usename')}\n")
                    f.write(f"Banco: {query_data.get('datname')}\n")
                    f.write(f"Endereço: {query_data.get('client_addr')}\n")
                    f.write(f"Estado: {query_data.get('state')}\n")
                    f.write(f"Início: {query_data.get('query_start')}\n")
                    f.write(f"Duração: {query_data.get('duration')}\n")
                    f.write(
                        f"Aguardando: {query_data.get('wait_event_type')} - {query_data.get('wait_event')}\n")
                    f.write(f"SQL: {query_data.get('query')}\n")
                    f.write("-" * 80 + "\n\n")

            return full_path
        except Exception as e:
            print(f"Erro ao salvar consultas em arquivo: {e}")
            return False

    def test_connection(self):
        """Testa a conexão com o PostgreSQL e retorna detalhes da versão ou erro"""
        try:
            if self.connect():
                cursor = self.conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                cursor.close()
                self.disconnect()
                return {
                    "success": True,
                    "message": f"Conexão estabelecida com sucesso!\n{version}",
                    "version": version
                }
            else:
                return {
                    "success": False,
                    "message": "Falha ao conectar. Verifique as credenciais e se o servidor está online."
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao testar conexão: {str(e)}"
            }
