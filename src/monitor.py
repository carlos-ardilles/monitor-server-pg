#!/usr/bin/env python
import os
import time
from datetime import datetime
import psutil


class LoadMonitor:
    def __init__(self, threshold=None):
        """
        Inicializa o monitor de carga do sistema

        Args:
            threshold: Se fornecido, usa este valor como limiar.
                      Se None, lê do ambiente MONITOR_THRESHOLD
        """
        if threshold is None:
            # Lê o limiar da variável de ambiente ou usa 2.0 como padrão
            self.threshold = float(os.environ.get('MONITOR_THRESHOLD', '2.0'))
        else:
            self.threshold = threshold

        # Lê os intervalos de verificação e captura
        self.check_interval = int(
            os.environ.get('MONITOR_CHECK_INTERVAL', '10'))
        self.capture_interval = int(
            os.environ.get('MONITOR_CAPTURE_INTERVAL', '60'))

        self.is_load_high = False
        self.monitoring = False

    def get_load_average(self):
        """Retorna o load average do sistema (1, 5, 15 minutos)"""
        return os.getloadavg()

    def is_above_threshold(self):
        """Verifica se o load average de 1 minuto está acima do limite definido"""
        load_1min, _, _ = self.get_load_average()
        return load_1min >= self.threshold

    def check_load_status(self):
        """Verifica o status do load e retorna se houve mudança de estado"""
        previous_state = self.is_load_high
        self.is_load_high = self.is_above_threshold()

        # Retorna True se houve mudança de estado
        return previous_state != self.is_load_high

    def get_current_time(self):
        """Retorna a hora atual formatada"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_system_info(self):
        """Retorna informações do sistema"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        return {
            "load_average": self.get_load_average(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "time": self.get_current_time(),
            "is_high_load": self.is_load_high
        }
