import os
from dotenv import load_dotenv

class Validador:
    def __init__(self, containers):
        self.containers = containers
        load_dotenv()

    def validate_container_limits(self):
        cpu_limit = os.getenv("CPU_LIMIT")
        mem_limit = os.getenv("MEM_LIMIT")

        for container in self.containers:
            informations_container = "##############\n"
            informations_container += "\r"
            informations_container += f"Container ID: {container.short_id}\n"
            
            # 'stats' contém informações de uso de CPU e memória
            stats = container.stats(stream=False)

            cpu_stats = stats['cpu_stats']
            precpu_stats = stats['precpu_stats']
            
            cpu_delta = cpu_stats['cpu_usage']['total_usage'] - precpu_stats['cpu_usage']['total_usage']
            system_delta = cpu_stats['system_cpu_usage'] - precpu_stats['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0

            container_info = container.attrs
            cpu_shares = container_info['HostConfig']['CpuShares']

            #if cpu_percent >= int(cpu_limit):
            #    informations_container += "Alcançou o limite!\n"

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
    