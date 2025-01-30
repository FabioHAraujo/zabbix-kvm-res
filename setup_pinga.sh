#!/bin/bash

# Atualiza pacotes e instala Python 3 com venv
echo "Instalando Python 3 e venv..."
apt update && apt install -y python3-venv

# Cria o ambiente virtual no local correto
echo "Criando o ambiente virtual em /usr/local/bin/ping_venv..."
python3 -m venv /usr/local/bin/ping_venv

# Cria o arquivo /usr/local/bin/pinga.py para medir latência
echo "Criando o arquivo /usr/local/bin/pinga.py..."
cat <<EOF > /usr/local/bin/pinga.py
#!/usr/local/bin/ping_venv/bin/python3
import subprocess
import sys
import re

def ping(host):
    try:
        output = subprocess.run(['ping', '-c', '1', host],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        if output.returncode == 0:
            match = re.search(r"time=(\d+\.?\d*) ms", output.stdout)
            if match:
                ping_time = match.group(1)
                print(f"{ping_time}")
            else:
                print("Tempo não encontrado na saída do ping.")
        else:
            print("Falha ao pingar {host}.")
            print(output.stderr)

    except Exception as e:
        print(f"Erro ao executar o ping: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python pinga.py <endereço_ip_ou_domínio>")
    else:
        ping(sys.argv[1])
EOF

# Cria o arquivo /usr/local/bin/packet_loss.py para medir perda de pacotes
echo "Criando o arquivo /usr/local/bin/packet_loss.py..."
cat <<EOF > /usr/local/bin/packet_loss.py
#!/usr/local/bin/ping_venv/bin/python3
import subprocess
import sys
import re

def packet_loss(host):
    try:
        output = subprocess.run(['ping', '-c', '10', host],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        if output.returncode == 0:
            match = re.search(r"(\d+\.?\d*)% packet loss", output.stdout)
            if match:
                loss = match.group(1)
                print(loss)
            else:
                print("Erro ao analisar perda de pacotes.")
        else:
            print("100.0")

    except Exception as e:
        print("100.0")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python packet_loss.py <endereço_ip_ou_domínio>")
    else:
        packet_loss(sys.argv[1])
EOF

# Dá permissão de execução aos scripts
chmod +x /usr/local/bin/pinga.py
chmod +x /usr/local/bin/packet_loss.py

# Cria o diretório de configuração do Zabbix Agent se não existir
echo "Criando diretório de configuração do Zabbix Agent..."
mkdir -p /etc/zabbix/zabbix_agent2.d/plugins.d/

# Cria o arquivo de configuração do Zabbix Agent
echo "Criando o arquivo de configuração do Zabbix Agent..."
cat <<EOF > /etc/zabbix/zabbix_agent2.d/plugins.d/pinga.conf
UserParameter=pinga.custom[*],/usr/bin/python3 /usr/local/bin/pinga.py \$1
UserParameter=packet.loss[*],/usr/bin/python3 /usr/local/bin/packet_loss.py \$1
EOF

# Reinicia o serviço do Zabbix Agent para aplicar as mudanças
echo "Reiniciando o Zabbix Agent..."
systemctl restart zabbix-agent2

echo "Configuração concluída! Os scripts pinga.py e packet_loss.py estão prontos para uso."
