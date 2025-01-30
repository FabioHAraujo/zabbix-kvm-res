#!/bin/bash

# Atualiza pacotes e instala Python 3 com venv
echo "Instalando Python 3 e venv..."
apt update && apt install -y python3-venv

# Cria o ambiente virtual no local correto
echo "Criando o ambiente virtual em /usr/local/bin/ping_venv..."
python3 -m venv /usr/local/bin/ping_venv

# Cria o arquivo /usr/local/bin/pinga.py com o conteúdo fornecido
echo "Criando o arquivo /usr/local/bin/pinga.py..."
cat <<EOF > /usr/local/bin/pinga.py
#!/usr/local/bin/ping_venv/bin/python3
import subprocess
import sys
import re

def ping(host):
    try:
        # Executa o comando ping com 1 pacote no Linux
        output = subprocess.run(['ping', '-c', '1', host],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        # Verifica se o ping foi bem-sucedido
        if output.returncode == 0:
            # Usa expressão regular para extrair o tempo do ping
            match = re.search(r"time=(\d+\.?\d*) ms", output.stdout)
            if match:
                ping_time = match.group(1)
                print(f"{ping_time}")
            else:
                print("Tempo não encontrado na saída do ping.")
        else:
            print(f"Falha ao pingar {host}.")
            print(output.stderr)

    except Exception as e:
        print(f"Erro ao executar o ping: {e}")

if __name__ == "__main__":
    # Verifica se um argumento foi passado
    if len(sys.argv) != 2:
        print("Uso: python pinga.py <endereço_ip_ou_domínio>")
    else:
        host = sys.argv[1]
        ping(host)
EOF

# Dá permissão de execução ao script pinga.py
chmod +x /usr/local/bin/pinga.py

# Cria o diretório de configuração do Zabbix Agent se não existir
echo "Criando diretório de configuração do Zabbix Agent..."
mkdir -p /etc/zabbix/zabbix_agent2.d/plugins.d/

# Cria o arquivo de configuração do Zabbix Agent
echo "Criando o arquivo de configuração do Zabbix Agent..."
cat <<EOF > /etc/zabbix/zabbix_agent2.d/plugins.d/pinga.conf
UserParameter=pinga.custom[*],/usr/bin/python3 /usr/local/bin/pinga.py \$1
EOF

# Reinicia o serviço do Zabbix Agent para aplicar as mudanças
echo "Reiniciando o Zabbix Agent..."
systemctl restart zabbix-agent2

echo "Configuração concluída! O script pinga.py e a configuração do Zabbix estão prontos."
