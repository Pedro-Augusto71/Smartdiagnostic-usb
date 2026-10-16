# 🛠️ Sistema Portátil de Diagnóstico de Hardware (Live USB)

Um sistema de diagnóstico de hardware plug-and-play desenvolvido em Python para ser executado num ambiente Linux Live USB (Lubuntu). Este projeto automatiza testes de estresse em componentes físicos e envia um laudo técnico completo via e-mail, sem necessidade de interagir com o disco rígido principal da máquina.

## 🚀 Funcionalidades

- Boot Autônomo Configurado via Autostart (`.desktop`) para rodar automaticamente assim que o sistema operativo é carregado.
- Filtro Inteligente de Armazenamento Isola o disco físico real (SATANVMe) e ignora volumes virtuais gerados pelo Live USB (zram, loop).
- Testes de Estresse Físico
  - CPU Análise de desempenho e carga bruta utilizando `stress-ng`.
  - RAM Alocação dinâmica de 80% da memória livre e varredura de erros físicos com `memtester`.
  - Disco Leitura de métricas vitais de saúde S.M.A.R.T. (temperaturas, avisos) via `smartctl`.
- Entrega Segura Formatação do laudo em modo texto e envio automatizado por e-mail utilizando SMTPSSL nativo do Python.

## 📋 Pré-requisitos

Para rodar este script, o ambiente Linux (Lubuntu) precisa ter as seguintes ferramentas instaladas
```bash
sudo apt-get update
sudo apt-get install python3 stress-ng memtester smartmontools

## ⚙️ Instalação e Configuração

1. Clone o repositório para o seu Live USB:
   ```bash
   git clone [https://github.com/Pedro-Augusto71/Smartdiagnostic-usb.git](https://github.com/Pedro-Augusto71/Smartdiagnostic-usb.git)

Configure as credenciais de e-mail no ficheiro diagnostico.py (insira o seu e-mail e a Senha de App do Gmail nas variáveis remetente e senha_app).

Configurar o Autostart (Arranque Automático):
Crie o atalho na pasta oculta do sistema:
mkdir -p ~/.config/autostart
nano ~/.config/autostart/diagnostico.desktop

E cole a seguinte configuração:
[Desktop Entry]
Type=Application
Name=Diagnostico Automatico
Comment=Testador de Hardware USB
Exec=qterminal -e bash -c "sudo python3 /home/lubuntu/diagnostico.py; echo ''; read -p 'Pressione ENTER para fechar a janela...' -r"
Terminal=false

💻 Como Usar
Com o Autostart configurado, basta dar boot pelo Live USB. O terminal abrirá automaticamente solicitando o e-mail do técnico:

Digite o e-mail para receber o laudo.

Aguarde a execução dos testes (CPU, RAM, Disco).

O laudo será salvo localmente em /home/lubuntu/laudo_diagnostico.txt e enviado por e-mail automaticamente.

👨‍💻 Autor
Desenvolvido por Pedro Augusto da Silva Abreu e Bruno Cruz Voltezou como Projeto em Engenharia da Computação I
