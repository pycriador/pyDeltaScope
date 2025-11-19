#!/usr/bin/env python3
"""
Script para iniciar o DeltaScope Flask app
Resolve automaticamente conflitos de porta 5000
"""

import os
import sys
import subprocess
import socket
import time
from pathlib import Path


def check_port_in_use(port: int) -> bool:
    """Verifica se uma porta está em uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except OSError:
            return True


def get_process_using_port(port: int):
    """Encontra o processo que está usando a porta especificada"""
    try:
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pid = result.stdout.strip().split('\n')[0]
            
            cmd_result = subprocess.run(
                ['ps', '-p', pid, '-o', 'command='],
                capture_output=True,
                text=True,
                check=False
            )
            
            command = cmd_result.stdout.strip() if cmd_result.returncode == 0 else 'Unknown'
            return (pid, command)
        
        return (None, None)
    except Exception:
        return (None, None)


def kill_process(pid: str) -> bool:
    """Mata um processo pelo PID"""
    try:
        subprocess.run(['kill', '-9', pid], check=True, capture_output=True)
        return True
    except Exception:
        return False


def find_free_port(start_port: int = 5000, max_attempts: int = 10) -> int:
    """Encontra uma porta livre começando de start_port"""
    for port in range(start_port, start_port + max_attempts):
        if not check_port_in_use(port):
            return port
    return None


def main():
    """Função principal"""
    port = 5000
    
    print("=" * 70)
    print("DeltaScope - Iniciando Servidor Flask")
    print("=" * 70)
    print()
    
    # Verifica se a porta está em uso
    if check_port_in_use(port):
        print(f"⚠️  Porta {port} está em uso!")
        print()
        
        # Tenta encontrar o processo
        pid, command = get_process_using_port(port)
        
        if pid:
            print(f"Processo encontrado:")
            print(f"  PID: {pid}")
            print(f"  Comando: {command}")
            print()
            
            # Verifica se é outro Flask app
            is_flask = any(keyword in command.lower() for keyword in ['flask', 'python', 'run.py'])
            
            if is_flask:
                print("Parece ser outro processo Flask/Python.")
                print("Tentando encerrar automaticamente...")
                print()
                
                if kill_process(pid):
                    print(f"✓ Processo {pid} encerrado!")
                    time.sleep(2)  # Aguarda liberação da porta
                    
                    # Verifica se a porta foi liberada
                    if not check_port_in_use(port):
                        print(f"✓ Porta {port} liberada!")
                    else:
                        print(f"⚠️  Porta {port} ainda está em uso.")
                        print("Procurando porta alternativa...")
                        free_port = find_free_port(port + 1)
                        if free_port:
                            port = free_port
                            print(f"✓ Usando porta alternativa: {port}")
                        else:
                            print("✗ Não foi possível encontrar uma porta livre.")
                            sys.exit(1)
                else:
                    print(f"✗ Não foi possível encerrar o processo {pid}.")
                    print("Procurando porta alternativa...")
                    free_port = find_free_port(port + 1)
                    if free_port:
                        port = free_port
                        print(f"✓ Usando porta alternativa: {port}")
                    else:
                        print("✗ Não foi possível encontrar uma porta livre.")
                        print()
                        print("Soluções:")
                        print("  1. Encerre manualmente o processo:")
                        print(f"     kill -9 {pid}")
                        print("  2. Desabilite o AirPlay Receiver:")
                        print("     Preferências do Sistema > Geral > AirDrop e Handoff")
                        sys.exit(1)
            else:
                # Não é processo Flask - provavelmente AirPlay ou outro serviço
                print("⚠️  Este não parece ser um processo Flask.")
                print("Pode ser o AirPlay Receiver do macOS ou outro serviço.")
                print()
                print("Procurando porta alternativa automaticamente...")
                free_port = find_free_port(port + 1)
                if free_port:
                    port = free_port
                    print(f"✓ Usando porta alternativa: {port}")
                else:
                    print("✗ Não foi possível encontrar uma porta livre.")
                    print()
                    print("Soluções:")
                    print("  1. Desabilite o AirPlay Receiver:")
                    print("     Preferências do Sistema > Geral > AirDrop e Handoff")
                    print("     Desmarque 'Receptor AirPlay'")
                    print("  2. Ou encerre o processo manualmente:")
                    if pid:
                        print(f"     kill -9 {pid}")
                    sys.exit(1)
        else:
            # Não conseguiu identificar o processo
            print("Não foi possível identificar o processo usando a porta.")
            print("Procurando porta alternativa automaticamente...")
            free_port = find_free_port(port + 1)
            if free_port:
                port = free_port
                print(f"✓ Usando porta alternativa: {port}")
            else:
                print("✗ Não foi possível encontrar uma porta livre.")
                sys.exit(1)
    else:
        print(f"✓ Porta {port} está livre!")
    
    print()
    print("-" * 70)
    print(f"Iniciando Flask na porta {port}...")
    print("-" * 70)
    print()
    
    # Verifica se run.py existe
    run_py = Path(__file__).parent / 'run.py'
    if not run_py.exists():
        print(f"✗ Arquivo run.py não encontrado em {run_py.parent}")
        sys.exit(1)
    
    # Define a porta via variável de ambiente
    os.environ['FLASK_RUN_PORT'] = str(port)
    
    # Executa o run.py
    try:
        # Muda para o diretório do projeto
        os.chdir(Path(__file__).parent)
        
        # Executa o run.py usando subprocess para manter o ambiente
        subprocess.run([sys.executable, str(run_py)], check=True)
        
    except KeyboardInterrupt:
        print("\n\nServidor interrompido pelo usuário.")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Erro ao iniciar servidor (código {e.returncode})")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
