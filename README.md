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
