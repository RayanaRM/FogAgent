# python3 Agent.py
import docker
import Validator
import os
from dotenv import load_dotenv
import time
from flask import Flask, jsonify
from threading import Thread
from flask_cors import CORS

load_dotenv()
client = docker.from_env()
interval = int(os.getenv("INTERVAL"))
informations_of_container = ""

app = Flask(__name__)
CORS(app)  # Habilita o CORS para todas as rotas da aplicação

def fetch_info_from_containers():
  while True:
    containers = client.containers.list()
    validator = Validator.Validador(containers)
    global informations_of_container
    informations_of_container = validator.validate_container_limits()
    # Aguarde o intervalo de tempo
    time.sleep(interval)

thread_info_fecther = Thread(target=fetch_info_from_containers)
thread_info_fecther.start()

# Rota para retornar o valor da variável
@app.route('/obter-variavel', methods=['GET'])
def obter_variavel():
    return jsonify({'valor': informations_of_container})

if __name__ == '__main__':
    # Inicializa o servidor Flask em uma thread separada
    thread_servidor = Thread(target=app.run)
    thread_servidor.daemon = True
    thread_servidor.start()