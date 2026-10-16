import subprocess
import sys
import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def encontrar_disco_principal():
    # Lista discos fixos e filtra explicitamente para ignorar volumes virtuais (zram e loop)
    resultado = subprocess.run(['lsblk', '-d', '-n', '-o', 'NAME,RM,TYPE'], capture_output=True, text=True)
    
    for linha in resultado.stdout.splitlines():
        colunas = linha.split()
        if len(colunas) >= 3:
            nome = colunas[0]
            removivel = colunas[1]
            tipo = colunas[2]
            
            # Regista apenas se for disco físico real, ignorando USBs e zram/loop
            if tipo == 'disk' and removivel == '0' and 'zram' not in nome and 'loop' not in nome:
                return f"/dev/{nome}"
                
    return None

def executar_comando(comando):
    """Executa um comando no terminal do Linux e retorna o resultado (stdout e stderr)."""
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return resultado.returncode, resultado.stdout, resultado.stderr
    except Exception as erro_fatal:
        return -1, "", str(erro_fatal)

def testar_cpu():
    """Inicia o teste de estresse no processador usando o stress-ng."""
    print("[*] Iniciando teste de CPU. Aguarde...")
    comando = "stress-ng --cpu 0 --timeout 10s --metrics-brief"
    
    codigo, saida, erro = executar_comando(comando)
    
    detalhes = "FALHA"
    if codigo == 0:
         detalhes = "OK\n"
         # Extraindo métricas (bogo ops) da saída stderr
         for linha in erro.splitlines():
             if "bogo ops" in linha:
                 detalhes += " "*15 + linha.strip() + "\n"
    
    return detalhes

def obter_ram_livre_mb():
    """Lê a quantidade de memória RAM disponível no sistema."""
    codigo, saida, erro = executar_comando("free -m")
    
    if codigo == 0:
        for linha in saida.splitlines():
            if linha.startswith("Mem:"):
                partes = linha.split()
                if len(partes) >= 7:
                    return int(partes[6])
                    
    return 512 

def testar_ram():
    """Inicia o teste de RAM. Aloca 80% da RAM disponível."""
    ram_disponivel = obter_ram_livre_mb()
    ram_para_teste = int(ram_disponivel * 0.8)
    
    print(f"[*] Iniciando teste de RAM ({ram_para_teste} MB alocados)...")
    
    comando = f"memtester {ram_para_teste}M 1"
    codigo, saida, erro = executar_comando(comando)
    
    detalhes = ""
    if codigo == 0:
        detalhes = "OK\n"
        erros_fisicos = 0
        for linha in saida.splitlines():
             if "FAILURE" in linha or "error" in linha.lower():
                 detalhes += " "*15 + f"[!] {linha.strip()}\n"
                 erros_fisicos += 1
        if erros_fisicos == 0:
            detalhes += " "*15 + "Nenhum erro físico detectado na memória."
        
        return detalhes
        
    elif codigo == 1:
        return "ERRO ALOCAÇÃO"
    else:
        if "FAILURE" in saida.upper():
            return "FALHA FÍSICA"
        return "FALHA DESCONHECIDA"

def testar_disco():
    """Inicia a leitura S.M.A.R.T. do disco principal automaticamente e extrai dados vitais."""
    print("[*] Iniciando leitura S.M.A.R.T. do disco principal...")
    
    disco_alvo = encontrar_disco_principal()
    
    if disco_alvo:
        print(f"[*] Disco principal detetado: {disco_alvo}")
        comando = f"sudo smartctl -A {disco_alvo}"
        codigo, saida, erro = executar_comando(comando)
        
        if codigo == 0:
            detalhes = f"OK ({disco_alvo})\n"
            tem_dados = False
            for linha in saida.splitlines():
                if any(termo in linha for termo in ["Temperature", "Power_On_Hours", "Reallocated_Sector", "Available_Reserv"]):
                    detalhes += " "*15 + linha.strip() + "\n"
                    tem_dados = True
            
            if not tem_dados:
                detalhes += " "*15 + "Disco não fornece métricas S.M.A.R.T. visíveis."
                
            return detalhes
        else:
             return f"ERRO S.M.A.R.T ({disco_alvo})"
    else:
        return "DISCO NÃO ENCONTRADO/ERRO"

def exibir_laudo_final(resultados):
    """Gera a interface visual em modo texto para o usuário."""
    print("\n" + "="*70)
    print("      LAUDO DE DIAGNÓSTICO TÉCNICO      ")
    print("="*70)
    for componente, status in resultados.items():
        # Separa o texto em linhas para isolar o "OK" ou "FALHA" das métricas
        linhas = status.strip().split('\n')
        
        # Coloca os colchetes apenas na primeira linha
        texto_final = f"[{linhas[0]}]"
        if len(linhas) > 1:
            # Anexa as restantes linhas por baixo sem colchetes
            texto_final += "\n" + "\n".join(linhas[1:])
            
        print(f" {componente.ljust(10)} : {texto_final}")
        print("-" * 70) # Adiciona uma linha subtil entre componentes para melhor leitura
    print("="*70)

def salvar_laudo_txt(resultados, caminho_arquivo="laudo_diagnostico.txt"):
    """Gera um arquivo .txt com os resultados do teste e a data/hora."""
    try:
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write("="*70 + "\n")
            arquivo.write("      LAUDO DE DIAGNÓSTICO TÉCNICO      \n")
            arquivo.write("="*70 + "\n")
            arquivo.write(f" Data/Hora: {agora}\n")
            arquivo.write("="*70 + "\n")
            
            for componente, status in resultados.items():
                linhas = status.strip().split('\n')
                texto_final = f"[{linhas[0]}]"
                if len(linhas) > 1:
                    texto_final += "\n" + "\n".join(linhas[1:])
                    
                arquivo.write(f" {componente.ljust(10)} : {texto_final}\n")
                arquivo.write("-" * 70 + "\n")
                
            arquivo.write("="*70 + "\n")
            
        print(f"\n[*] Laudo técnico salvo com sucesso em: {caminho_arquivo}")
    except Exception as e:
        print(f"\n[!] Erro ao salvar o laudo no arquivo: {str(e)}")
        
def enviar_laudo_email(caminho_arquivo, email_destino):
    """Lê o laudo salvo e envia como anexo para o e-mail inserido pelo utilizador."""
    if not email_destino or "@" not in email_destino:
        print("[!] Endereço de e-mail inválido. O envio foi ignorado.")
        return

    print(f"[*] A preparar o envio do laudo para {email_destino}...")

    # ==========================================================
    remetente = "seu_email_aqui@gmail.com" 
    senha_app = "sua_senha_de_app_aqui"
    # ==========================================================

    try:
        # Cria a estrutura do e-mail
        mensagem = MIMEMultipart()
        mensagem['From'] = remetente
        mensagem['To'] = email_destino
        mensagem['Subject'] = "Laudo de Diagnóstico de Hardware - Ferramenta USB"

        corpo = "Olá,\n\nSegue em anexo o laudo técnico detalhado referente ao diagnóstico de hardware realizado na máquina.\n\nCumprimentos,\nTestador de Hardware USB"
        mensagem.attach(MIMEText(corpo, 'plain'))

        # Lê o ficheiro local e anexa-o ao e-mail
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            anexo = MIMEText(f.read())
        anexo.add_header('Content-Disposition', 'attachment', filename="laudo_diagnostico.txt")
        mensagem.attach(anexo)

        # Estabelece ligação segura com os servidores da Google
        contexto = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as servidor:
            servidor.login(remetente, senha_app)
            servidor.sendmail(remetente, email_destino, mensagem.as_string())
            
        print("[+] Sucesso! O laudo foi enviado por e-mail com sucesso.")

    except Exception as erro:
        print(f"[!] Erro crítico ao enviar o e-mail: {str(erro)}")

if __name__ == "__main__":
    print("="*70)
    print("INICIANDO TESTADOR DE HARDWARE TÉCNICO VIA USB")
    print("="*70)
    
    # 1. Solicita o e-mail do cliente ANTES de começar os testes demorados
    email_cliente = input("\n[?] Introduza o e-mail para receber o laudo (ou prima Enter para ignorar): ").strip()
    print("")
    
    dicionario_resultados = {}
    
    # 2. Executa a bateria de testes sequencialmente
    dicionario_resultados["CPU"] = testar_cpu()
    dicionario_resultados["RAM"] = testar_ram()
    dicionario_resultados["DISCO"] = testar_disco()
    
    # 3. Renderiza o ecrã final e salva o ficheiro localmente
    exibir_laudo_final(dicionario_resultados)
    caminho_laudo = "/home/lubuntu/laudo_diagnostico.txt"
    salvar_laudo_txt(dicionario_resultados, caminho_laudo)
    
    # 4. Faz o envio do e-mail caso o utilizador tenha digitado um endereço válido
    if email_cliente:
        enviar_laudo_email(caminho_laudo, email_cliente)