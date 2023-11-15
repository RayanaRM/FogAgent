# python3 Agent.py
import docker
import Validator
import os
from dotenv import load_dotenv
import time
from threading import Thread
from flask_cors import CORS
from flask import Flask, request, jsonify

load_dotenv()
client = docker.from_env()
informations_of_container = ""
CPU_LIMIT=50
CPU_MAX=100
MEM_LIMIT=1000000

interval = 0

app = Flask(__name__)
CORS(app)  # Habilita o CORS para todas as rotas da aplicação

def fetch_info_from_containers():
  global interval
  interval = int(os.getenv("INTERVAL"))
  while True:
    containers = client.containers.list()
    validator = Validator.Validador(containers)
    global informations_of_container
    informations_of_container = validator.validate_container_limits()
    
    if validator.new_interval != None:
      interval = validator.new_interval
    
    time.sleep(interval)

thread_info_fecther = Thread(target=fetch_info_from_containers)
thread_info_fecther.start()

# Rota para retornar o valor da variável
@app.route('/obter-variavel', methods=['GET'])
def obter_variavel():
    return jsonify({'valor': informations_of_container + f'Intervalo de Monitoramento (min): {interval}\n'})

# Rota para retornar o valor da variável
@app.route('/update-variavel', methods=['PUT'])
def update_variavel():
    global CPU_LIMIT
    global MEM_LIMIT
    # Obtenha os valores do corpo da solicitação JSON
    data = request.get_json()

    if 'cpuLimit' in data and 'memoryLimit' in data:
      # Atualize as variáveis globais
      CPU_LIMIT = data['cpuLimit']
      MEM_LIMIT = data['memoryLimit']

if __name__ == '__main__':
    # Inicializa o servidor Flask em uma thread separada
    thread_servidor = Thread(target=app.run(host='0.0.0.0', port=80))
    thread_servidor.daemon = True
    thread_servidor.start()