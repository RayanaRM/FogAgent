import os
import requests
from dotenv import load_dotenv
import docker

class Validador:
    def __init__(self, containers):
        self.containers = containers
        self._new_interval = None 
        load_dotenv()

    @property
    def new_interval(self):
        return self._new_interval 

    @new_interval.setter
    def new_interval(self, valor):
        self._new_interval = valor 

    def validate_container_limits(self):
        cpu_limit = os.getenv("CPU_LIMIT")
        cpu_max = os.getenv("CPU_MAX")

        mem_limit = os.getenv("MEM_LIMIT")
        informations_container = ""

        # Crie uma instância do cliente Docker
        client = docker.from_env()

        for container in self.containers:
            container_id = container.short_id
            informations_container += "\n\n"
            informations_container += f"Container ID: {container_id}\n"
            
            # 'stats' contém informações de uso de CPU e memória
            stats = container.stats(stream=False)

            cpu_stats = stats['cpu_stats']
            precpu_stats = stats['precpu_stats']
            
            cpu_delta = cpu_stats['cpu_usage']['total_usage'] - precpu_stats['cpu_usage']['total_usage']
            system_delta = cpu_stats['system_cpu_usage'] - precpu_stats['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0

            container_info = container.attrs
            cpu_shares = container_info['HostConfig']['CpuShares']

            ############# CONTROLES DE LIMITES ###############
            if int(cpu_percent) >= int(cpu_limit) and int(cpu_percent) < int(cpu_max):
                print(int(cpu_percent))

                cpu_limit=int(int(cpu_limit) + int(int(cpu_limit) * 0.1))
                informations_container += "Alcançou o limite, container redimensionado!\n"
                self.new_interval = 5

            elif int(cpu_percent) >= int(cpu_max):
                print(int(cpu_percent))
                # Crie um novo container com base na imagem
                new_container = client.containers.create(image=container.attrs['Config']['Image'])
                new_container.start()
                informations_container += f'Alcançou o limite da máquina física, novo container criado com ID: {new_container.short_id}\n'
                self.new_interval = 5
                cpu_percent=100.12

            # Métricas de memória
            memory_stats = stats['memory_stats']
            memory_usage = memory_stats['usage'] / (1024 ** 2)
            memory_limit = memory_stats['limit'] / (1024 ** 2)
            
            # Métricas de rede
            network_stats = stats['networks']

            informations_container += f'Uso de CPU em porcentagem: {cpu_percent:.2f}%\n'
            informations_container += f'Uso de memória: {memory_usage} megabytes\n'
            informations_container += "\n"
            informations_container += f'Limite de CPU (%): {0}\n'
            informations_container += f'Limite de memória: {memory_limit} megabytes\n'
            
            for network_interface, network_info in network_stats.items():
                informations_container += f'Rede {network_interface}:\n'
                informations_container += f' Bytes enviados: {network_info["tx_bytes"] / 1024:.2f} KB\n'
                informations_container += f' Bytes recebidos: {network_info["rx_bytes"] / 1024:.2f} KB\n'

        return informations_container