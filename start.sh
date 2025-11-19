#!/bin/bash
# Script shell para iniciar o DeltaScope Flask app
# Resolve automaticamente conflitos de porta 5000

PORT=5000
DEFAULT_PORT=5000

echo "======================================================================"
echo "DeltaScope - Iniciando Servidor Flask"
echo "======================================================================"
echo ""

# Verifica se a porta está em uso
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "⚠️  Porta $PORT está em uso!"
    echo ""
    
    # Obtém informações do processo
    PID=$(lsof -ti:$PORT | head -n 1)
    if [ ! -z "$PID" ]; then
        COMMAND=$(ps -p $PID -o command= 2>/dev/null)
        echo "Processo encontrado:"
        echo "  PID: $PID"
        echo "  Comando: $COMMAND"
        echo ""
        
        # Verifica se é Flask/Python
        if echo "$COMMAND" | grep -qiE "(flask|python|run\.py)"; then
            echo "Parece ser outro processo Flask/Python."
            read -p "Deseja encerrar este processo? (s/N): " response
            if [[ "$response" =~ ^[sS][iI][mM]?$|^[yY][eE][sS]?$ ]]; then
                echo "Encerrando processo $PID..."
                kill -9 $PID 2>/dev/null
                sleep 1
                
                if ! lsof -ti:$PORT > /dev/null 2>&1; then
                    echo "✓ Porta $PORT liberada!"
                else
                    echo "⚠️  Porta $PORT ainda está em uso. Tentando outra porta..."
                    PORT=$((PORT + 1))
                    while lsof -ti:$PORT > /dev/null 2>&1 && [ $PORT -lt 5010 ]; do
                        PORT=$((PORT + 1))
                    done
                    if [ $PORT -lt 5010 ]; then
                        echo "✓ Usando porta alternativa: $PORT"
                    else
                        echo "✗ Não foi possível encontrar uma porta livre."
                        exit 1
                    fi
                fi
            else
                read -p "Deseja usar outra porta? (s/N): " response
                if [[ "$response" =~ ^[sS][iI][mM]?$|^[yY][eE][sS]?$ ]]; then
                    PORT=$((PORT + 1))
                    while lsof -ti:$PORT > /dev/null 2>&1 && [ $PORT -lt 5010 ]; do
                        PORT=$((PORT + 1))
                    done
                    if [ $PORT -lt 5010 ]; then
                        echo "✓ Usando porta alternativa: $PORT"
                    else
                        echo "✗ Não foi possível encontrar uma porta livre."
                        exit 1
                    fi
                else
                    echo "Cancelando inicialização..."
                    exit 1
                fi
            fi
        else
            echo "⚠️  ATENÇÃO: Este não parece ser um processo Flask."
            echo "   Pode ser o AirPlay Receiver do macOS ou outro serviço."
            echo ""
            echo "Soluções:"
            echo "  1. Desabilite o AirPlay Receiver:"
            echo "     Preferências do Sistema > Geral > AirDrop e Handoff"
            echo "     Desmarque 'Receptor AirPlay'"
            echo ""
            read -p "Deseja usar outra porta? (s/N): " response
            if [[ "$response" =~ ^[sS][iI][mM]?$|^[yY][eE][sS]?$ ]]; then
                PORT=$((PORT + 1))
                while lsof -ti:$PORT > /dev/null 2>&1 && [ $PORT -lt 5010 ]; do
                    PORT=$((PORT + 1))
                done
                if [ $PORT -lt 5010 ]; then
                    echo "✓ Usando porta alternativa: $PORT"
                else
                    echo "✗ Não foi possível encontrar uma porta livre."
                    exit 1
                fi
            else
                echo "Cancelando inicialização..."
                exit 1
            fi
        fi
    else
        echo "Não foi possível identificar o processo usando a porta."
        read -p "Deseja usar outra porta? (s/N): " response
        if [[ "$response" =~ ^[sS][iI][mM]?$|^[yY][eE][sS]?$ ]]; then
            PORT=$((PORT + 1))
            while lsof -ti:$PORT > /dev/null 2>&1 && [ $PORT -lt 5010 ]; do
                PORT=$((PORT + 1))
            done
            if [ $PORT -lt 5010 ]; then
                echo "✓ Usando porta alternativa: $PORT"
            else
                echo "✗ Não foi possível encontrar uma porta livre."
                exit 1
            fi
        else
            echo "Cancelando inicialização..."
            exit 1
        fi
    fi
else
    echo "✓ Porta $PORT está livre!"
fi

echo ""
echo "----------------------------------------------------------------------"
echo "Iniciando Flask na porta $PORT..."
echo "----------------------------------------------------------------------"
echo ""

# Verifica se run.py existe
if [ ! -f "run.py" ]; then
    echo "✗ Arquivo run.py não encontrado"
    exit 1
fi

# Define a porta via variável de ambiente e executa
export FLASK_RUN_PORT=$PORT
python3 run.py

