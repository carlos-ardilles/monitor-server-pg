#!/usr/bin/env python
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Input, Label, DataTable
from textual.reactive import reactive
from textual import work
import time
import os
from datetime import datetime


class SystemInfoWidget(Static):
    """Widget para exibir informações do sistema"""

    cpu_load = reactive("0.00, 0.00, 0.00")
    cpu_percent = reactive("0%")
    memory_percent = reactive("0%")
    status = reactive("Normal")
    status_color = reactive("green")
    last_update = reactive("Nunca")

    def on_mount(self):
        """Chamado quando o widget é montado na interface"""
        # Agora é seguro atualizar os widgets
        self.update_status_display()

    def update_info(self, info):
        """Atualiza as informações de sistema exibidas"""
        self.cpu_load = f"{info['load_average'][0]:.2f}, {info['load_average'][1]:.2f}, {info['load_average'][2]:.2f}"
        self.cpu_percent = f"{info['cpu_percent']:.1f}%"
        self.memory_percent = f"{info['memory_percent']:.1f}%"
        self.last_update = info['time']

        if info['is_high_load']:
            self.status = "ALTO LOAD!"
            self.status_color = "red"
        else:
            self.status = "Normal"
            self.status_color = "green"

        self.update_status_display()

    def update_status_display(self):
        """Atualiza a exibição do status (chamado quando status ou status_color mudam)"""
        if self.is_mounted:
            status_widget = self.query_one("#status")
            status_widget.remove_class("status-green")
            status_widget.remove_class("status-red")
            status_widget.add_class(f"status-{self.status_color}")
            status_widget.update(self.status)

    def compose(self) -> ComposeResult:
        """Compõe o widget de informações do sistema"""
        yield Container(
            Label("Status do Sistema", classes="section-title"),
            Horizontal(
                Label("Status:", classes="info-label"),
                Static(self.status, id="status",
                       classes=f"status-{self.status_color}"),
                classes="info-row"
            ),
            Horizontal(
                Label("Load Average:", classes="info-label"),
                Static(self.cpu_load, id="load-avg"),
                classes="info-row"
            ),
            Horizontal(
                Label("CPU:", classes="info-label"),
                Static(self.cpu_percent, id="cpu-percent"),
                classes="info-row"
            ),
            Horizontal(
                Label("Memória:", classes="info-label"),
                Static(self.memory_percent, id="memory-percent"),
                classes="info-row"
            ),
            Horizontal(
                Label("Atualizado:", classes="info-label"),
                Static(self.last_update, id="last-update"),
                classes="info-row"
            ),
            id="system-info",
        )

    def watch_status(self, status):
        """Chamado quando o status muda"""
        if self.is_mounted:
            self.update_status_display()

    def watch_status_color(self, color):
        """Chamado quando a cor do status muda"""
        if self.is_mounted:
            self.update_status_display()

    def watch_cpu_load(self, cpu_load):
        """Chamado quando o load average muda"""
        if self.is_mounted:
            self.query_one("#load-avg").update(cpu_load)

    def watch_cpu_percent(self, cpu_percent):
        """Chamado quando a % de CPU muda"""
        if self.is_mounted:
            self.query_one("#cpu-percent").update(cpu_percent)

    def watch_memory_percent(self, memory_percent):
        """Chamado quando a % de memória muda"""
        if self.is_mounted:
            self.query_one("#memory-percent").update(memory_percent)

    def watch_last_update(self, last_update):
        """Chamado quando o timestamp de última atualização muda"""
        if self.is_mounted:
            self.query_one("#last-update").update(last_update)


class QueryLogWidget(Static):
    """Widget para exibir logs de consultas salvas"""
    log_files = reactive([])
    # Contador para garantir IDs de botão únicos
    _button_counter = 0

    def on_mount(self):
        self.update_logs()

    def update_logs(self):
        """Atualiza a lista de arquivos de log"""
        log_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(log_dir):
            self.log_files = []
            return

        files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        files.sort(reverse=True)  # Ordena do mais recente para o mais antigo
        self.log_files = files[:20]  # Limita para os 20 mais recentes

    def add_log_file(self, filename):
        """Adiciona um novo arquivo de log à lista"""
        basename = os.path.basename(filename)
        if basename not in self.log_files:
            self.log_files = [basename] + self.log_files[:19]

    def compose(self) -> ComposeResult:
        """Compõe o widget de logs"""
        yield Container(
            Label("Logs de Consultas PostgreSQL", classes="section-title"),
            Static("Nenhum log de consulta encontrado",
                   id="log-list-empty", classes="log-empty"),
            Container(id="log-list"),
            id="log-container"
        )

    def watch_log_files(self, log_files):
        """Atualizado quando a lista de logs muda"""
        log_list = self.query_one("#log-list")

        # Limpa completamente a lista de logs existentes
        log_list.remove_children()

        empty_msg = self.query_one("#log-list-empty")
        if not log_files:
            empty_msg.display = True
            return

        empty_msg.display = False

        # Adiciona os arquivos de log à lista com IDs realmente únicos usando timestamp
        for index, log_file in enumerate(log_files):
            timestamp = " ".join(log_file.replace(
                "pg_queries_", "").replace(".log", "").split("_"))

            # Usa um contador global para garantir IDs únicos mesmo em atualizações simultâneas
            self._button_counter += 1
            unique_id = f"log-{index}-{self._button_counter}"

            # Monta o botão com o ID único
            log_button = Button(f"{timestamp}", id=unique_id)
            # Adiciona o índice como um atributo para identificação posterior
            log_button.log_index = index

            # Monta o botão na interface
            log_list.mount(log_button)


class MonitorConfigWidget(Static):
    """Widget para configurações de monitoramento"""

    def compose(self) -> ComposeResult:
        """Compõe o widget de configurações"""
        # Lê o threshold atual da variável de ambiente
        current_threshold = os.environ.get('MONITOR_THRESHOLD', '2.0')

        yield Container(
            Label("Configurações de Monitoramento", classes="section-title"),
            Horizontal(
                Label("Limiar de Load Average:", classes="info-label"),
                Input(placeholder=current_threshold,
                      id="load-threshold", value=current_threshold),
                Button("Aplicar", id="apply-threshold"),
                classes="config-row"
            ),
            # Linha de informações do banco de dados
            Horizontal(
                Label("Banco de Dados:", classes="info-label"),
                Static(f"{os.environ.get('PGHOST', 'localhost')}:{os.environ.get('PGPORT', '5432')}/{os.environ.get('PGDATABASE', 'postgres')}", id="db-info"),
                classes="info-row"
            ),
            # Botão de teste de conexão em uma linha separada
            Horizontal(
                Button("Testar Conexão", id="test-connection", variant="primary"),
                classes="test-button-row"
            ),
            # Status do monitoramento
            Horizontal(
                Label("Status:", classes="info-label"),
                Static("Monitoramento parado", id="monitor-status"),
                classes="info-row"
            ),
            # Resultados do teste de conexão
            Static("", id="connection-status", classes="connection-status"),
            # Botões de controle do monitoramento
            Horizontal(
                Button("Iniciar Monitoramento",
                       id="start-monitor", variant="success"),
                Button("Parar Monitoramento", id="stop-monitor",
                       variant="error", disabled=True),
                classes="monitor-buttons-row"
            ),
            id="config-container"
        )


class MonitorApp(App):
    """Aplicação principal de monitoramento"""
    CSS = """
    Screen {
        background: #0f1419;
    }
    
    #main-container {
        height: 100%;
        padding: 1;
    }
    
    #left-panel {
        width: 60%;
        height: 100%;
        margin-right: 1;
    }
    
    #right-panel {
        width: 40%;
        height: 100%;
    }
    
    .section-title {
        background: #1f2933;
        color: #e4e7eb;
        padding: 1;
        text-align: center;
        /* Removendo font-weight: bold que não é suportado */
        margin-bottom: 1;
    }
    
    .info-row {
        height: 1;
        margin-bottom: 1;
    }
    
    .info-label {
        width: 40%;
        color: #a0aec0;
    }
    
    .config-row {
        margin-bottom: 1;
        height: 3;
    }
    
    .db-row {
        margin-bottom: 1;
        height: 1;
    }
    
    .test-button-row {
        margin-top: 1;
        margin-bottom: 1;
        align: center middle;
        height: 3;
    }
    
    .monitor-buttons-row {
        margin-top: 1;
        align: center middle;
        height: 3;
    }
    
    .button-row {
        margin-top: 1;
        align: center middle;
    }
    
    .connection-status {
        margin-top: 1;
        margin-bottom: 1;
        height: auto;
        padding: 1;
    }
    
    .connection-success {
        color: #48bb78;
    }
    
    .connection-error {
        color: #f56565;
    }
    
    #system-info {
        background: #1a202c;
        padding: 1;
        margin-bottom: 1;
        height: auto;
    }
    
    .status-red {
        color: #f56565;
        /* Removendo font-weight: bold que não é suportado */
    }
    
    .status-green {
        color: #48bb78;
    }
    
    #config-container {
        background: #1a202c;
        padding: 1;
        margin-bottom: 1;
        height: auto;
    }
    
    #log-container {
        background: #1a202c;
        padding: 1;
        height: 1fr;
    }
    
    #log-list {
        margin-top: 1;
        overflow-y: auto;
        height: auto;
        max-height: 35;
    }
    
    .log-empty {
        color: #a0aec0;
        text-align: center;
        margin-top: 2;
    }
    
    Button {
        margin-right: 1;
    }
    
    #log-list Button {
        width: 100%;
        margin-bottom: 1;
    }

    .config-info {
        margin-top: 1;
        color: #a0aec0;
        text-align: center;
    }
    """

    TITLE = "Monitor de Servidor PostgreSQL"
    BINDINGS = [("q", "quit", "Sair")]

    # Referência para os workers
    _monitor_worker = None

    def __init__(self):
        super().__init__()
        self.monitoring = False
        # Lê o threshold da variável de ambiente
        self.load_threshold = float(os.environ.get('MONITOR_THRESHOLD', '2.0'))
        # Lê os intervalos de verificação e captura
        self.check_interval = int(
            os.environ.get('MONITOR_CHECK_INTERVAL', '10'))
        self.capture_interval = int(
            os.environ.get('MONITOR_CAPTURE_INTERVAL', '60'))

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                Vertical(
                    SystemInfoWidget(),
                    MonitorConfigWidget(),
                    id="left-panel"
                ),
                Vertical(
                    QueryLogWidget(),
                    id="right-panel"
                ),
                id="main-container"
            )
        )
        yield Footer()

    def on_mount(self):
        """Chamado quando a aplicação é montada"""
        # Configurações iniciais
        self.query_one("#stop-monitor").disabled = True

    def on_button_pressed(self, event: Button.Pressed):
        """Manipula eventos de pressionamento de botão"""
        button_id = event.button.id

        if button_id == "start-monitor":
            self.start_monitoring()
        elif button_id == "stop-monitor":
            self.stop_monitoring()
        elif button_id == "apply-threshold":
            self.update_threshold()
        elif button_id == "test-connection":
            self.test_database_connection()
        elif button_id and button_id.startswith("log-"):
            # Visualizar um arquivo de log
            self.view_log_file(button_id.replace("log-", ""))

    def test_database_connection(self):
        """Testa a conexão com o banco de dados PostgreSQL"""
        from src.postgresql import PostgresMonitor

        # Atualiza o status da conexão para "Testando..."
        conn_status = self.query_one("#connection-status")
        conn_status.remove_class("connection-success")
        conn_status.remove_class("connection-error")
        conn_status.update("Testando conexão...")

        # Desabilita o botão durante o teste
        test_btn = self.query_one("#test-connection")
        test_btn.disabled = True

        # Cria um worker para testar a conexão sem bloquear a interface
        self._test_connection_worker()

    @work
    async def _test_connection_worker(self):
        """Worker para testar a conexão com o banco de dados"""
        import asyncio
        from src.postgresql import PostgresMonitor

        # Dá tempo para a interface se atualizar
        await asyncio.sleep(0.5)

        # Testa a conexão
        pg_monitor = PostgresMonitor()
        result = pg_monitor.test_connection()

        # Atualiza a interface com o resultado
        conn_status = self.query_one("#connection-status")
        start_btn = self.query_one("#start-monitor")
        test_btn = self.query_one("#test-connection")

        if result["success"]:
            conn_status.add_class("connection-success")
            conn_status.update(result["message"])
            start_btn.disabled = False
        else:
            conn_status.add_class("connection-error")
            conn_status.update(result["message"])
            start_btn.disabled = True

        # Reativa o botão de teste
        test_btn.disabled = False

    def update_threshold(self):
        """Atualiza o limiar de carga do sistema"""
        threshold_input = self.query_one("#load-threshold")
        try:
            value = float(threshold_input.value)
            if value <= 0:
                self.notify(
                    "O valor do limiar deve ser maior que zero", severity="error")
                return

            self.load_threshold = value
            # Atualiza a variável de ambiente para que outros módulos possam acessá-la
            os.environ['MONITOR_THRESHOLD'] = str(value)
            self.notify(f"Limiar de carga atualizado para {value}")

            # Atualiza o limiar no monitor caso esteja em execução
            if self.monitoring:
                self.stop_monitoring()
                self.start_monitoring()

        except ValueError:
            self.notify("Por favor, insira um número válido", severity="error")

    def start_monitoring(self):
        """Inicia o monitoramento do sistema"""
        if self.monitoring:
            self.notify("O monitoramento já está ativo!", severity="warning")
            return

        self.monitoring = True
        self.query_one("#monitor-status").update("Monitoramento ativo")
        self.query_one("#start-monitor").disabled = True
        self.query_one("#stop-monitor").disabled = False
        self.notify("Monitoramento iniciado. Verificando load average a cada " +
                    f"{self.check_interval} segundos.")

        # Inicia o worker de monitoramento
        if self._monitor_worker is None:
            self._monitor_worker = self._monitor_system()

    def stop_monitoring(self):
        """Para o monitoramento do sistema"""
        if not self.monitoring:
            return

        self.monitoring = False
        self.query_one("#monitor-status").update("Monitoramento parado")
        self.query_one("#start-monitor").disabled = False
        self.query_one("#stop-monitor").disabled = True

    def view_log_file(self, log_id):
        """Visualiza o conteúdo de um arquivo de log"""
        try:
            # O log_id agora é algo como "0-123" (índice-contador)
            log_id_parts = log_id.split("-")
            if len(log_id_parts) >= 1:
                index = int(log_id_parts[0])
            else:
                self.notify("Formato de ID de log inválido", severity="error")
                return

            # Obtém o nome do arquivo de log a partir do índice
            log_files = self.query_one(QueryLogWidget).log_files
            if index < 0 or index >= len(log_files):
                self.notify("Índice de log inválido", severity="error")
                return

            filename = log_files[index]

            filepath = os.path.join(os.getcwd(), "logs", filename)
            if not os.path.exists(filepath):
                self.notify(
                    f"Arquivo não encontrado: {filename}", severity="error")
                return

            # Abre o arquivo em um visualizador less/more dependendo do sistema
            if os.name == 'posix':
                os.system(f"less '{filepath}'")
            else:
                os.system(f"more \"{filepath}\"")

        except ValueError as e:
            self.notify(f"Erro ao abrir log: {str(e)}", severity="error")
        except Exception as e:
            self.notify(f"Erro desconhecido: {str(e)}", severity="error")

    @work(exclusive=True)
    async def _monitor_system(self):
        """Worker para monitorar o sistema em segundo plano"""
        from src.monitor import LoadMonitor
        from src.postgresql import PostgresMonitor
        import asyncio

        # Configuração inicial
        load_monitor = LoadMonitor(self.load_threshold)
        pg_monitor = PostgresMonitor()
        system_info_widget = self.query_one(SystemInfoWidget)
        query_log_widget = self.query_one(QueryLogWidget)

        # Loop de monitoramento
        high_load_time = None
        last_log_time = None

        while True:
            if not self.monitoring:
                # Usamos asyncio.sleep ao invés de self.sleep
                await asyncio.sleep(1)
                continue

            # Verifica o load average e atualiza o status
            status_changed = load_monitor.check_load_status()
            system_info = load_monitor.get_system_info()

            # Atualiza a interface
            system_info_widget.update_info(system_info)

            # Verificamos is_high_load através do system_info que já tem o valor atualizado
            if system_info['is_high_load']:
                # Marca quando começou o load alto
                if high_load_time is None:
                    high_load_time = datetime.now()
                    last_log_time = None
                    # Log inicial imediato quando detectamos load alto
                    self.notify(
                        f"Load alto detectado: {system_info['load_average'][0]:.2f} (threshold: {self.load_threshold})")

                # Se é a primeira vez ou se passou o intervalo de captura desde o último log
                current_time = datetime.now()
                if last_log_time is None or (current_time - last_log_time).total_seconds() >= self.capture_interval:
                    # Obtém e salva as consultas ativas
                    queries = pg_monitor.get_active_queries()
                    if queries:
                        log_path = pg_monitor.save_queries_to_file(queries)
                        if log_path:
                            query_log_widget.add_log_file(log_path)
                            query_log_widget.update_logs()
                            self.notify(
                                f"Novas consultas PostgreSQL salvas em {os.path.basename(log_path)}")
                    else:
                        self.notify(
                            "Nenhuma consulta ativa encontrada no PostgreSQL")

                    last_log_time = current_time
            else:
                # Se o load estava alto e agora está normal
                if high_load_time is not None:
                    duration = datetime.now() - high_load_time
                    self.notify(
                        f"Load normalizado após {duration.total_seconds():.0f} segundos")
                    high_load_time = None

            # Espera o intervalo de verificação antes da próxima verificação
            await asyncio.sleep(self.check_interval)
