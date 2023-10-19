import os
import requests
from dotenv import load_dotenv

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

        for container in self.containers:
            container_id = container.short_id
            informations_container += "##############\n"
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
                informations_container += "Alcançou o limite!\n"
                container.update(cpu_shares=int((cpu_shares + 20) / 100))
                self.new_interval = 100

            elif cpu_percent >= int(cpu_max):
                # Crie um novo container com base na imagem
                new_container = self.containers.create(image=container.attrs['Config']['Image'])
                new_container.start()
                self.new_interval = 100

            # Métricas de memória
            memory_stats = stats['memory_stats']
            memory_usage = memory_stats['usage']
            memory_limit = memory_stats['limit']
            
            # Métricas de rede
            network_stats = stats['networks']

            informations_container += f'Uso de CPU em porcentagem: {cpu_percent:.2f}%\n'
            informations_container += f'Uso de memória: {memory_usage} bytes\n'
            informations_container += "\r"
            informations_container += f'Limite de CPU (shares): {cpu_shares}\n'
            informations_container += f'Limite de memória: {memory_limit} bytes\n'
            
            for network_interface, network_info in network_stats.items():
                informations_container += f'Rede {network_interface}:\n'
                informations_container += f'  Bytes enviados: {network_info["tx_bytes"]} bytes\n'
                informations_container += f'  Bytes enviados: {network_info["tx_bytes"]} bytes\n'

        return informations_container