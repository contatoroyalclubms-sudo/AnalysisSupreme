#!/bin/bash

set -e

echo "🔍 INICIANDO PRÉ-CHECAGENS DO SISTEMA"
echo "======================================"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 encontrado: $(command -v $1)${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 não encontrado${NC}"
        return 1
    fi
}

check_python_version() {
    if python3 --version &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}✅ Python encontrado: $PYTHON_VERSION${NC}"
        
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
            echo -e "${GREEN}✅ Versão Python compatível (3.9+)${NC}"
        else
            echo -e "${YELLOW}⚠️  Versão Python pode ser incompatível (recomendado 3.9+)${NC}"
        fi
    else
        echo -e "${RED}❌ Python3 não encontrado${NC}"
        return 1
    fi
}

check_ports() {
    echo "🔍 Verificando portas disponíveis..."
    
    PORTS=(8000 8080 6379 5432)
    for port in "${PORTS[@]}"; do
        if netstat -tuln 2>/dev/null | grep ":$port " &> /dev/null; then
            echo -e "${YELLOW}⚠️  Porta $port em uso${NC}"
        else
            echo -e "${GREEN}✅ Porta $port disponível${NC}"
        fi
    done
}

check_permissions() {
    echo "🔍 Verificando permissões..."
    
    if [ -w "." ]; then
        echo -e "${GREEN}✅ Permissão de escrita no diretório atual${NC}"
    else
        echo -e "${RED}❌ Sem permissão de escrita no diretório atual${NC}"
        return 1
    fi
    
    if [ -w "/tmp" ]; then
        echo -e "${GREEN}✅ Permissão de escrita em /tmp${NC}"
    else
        echo -e "${RED}❌ Sem permissão de escrita em /tmp${NC}"
        return 1
    fi
}

check_disk_space() {
    echo "🔍 Verificando espaço em disco..."
    
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    REQUIRED_SPACE=1048576  # 1GB em KB
    
    if [ "$AVAILABLE_SPACE" -gt "$REQUIRED_SPACE" ]; then
        echo -e "${GREEN}✅ Espaço em disco suficiente: $(($AVAILABLE_SPACE/1024/1024))GB disponível${NC}"
    else
        echo -e "${YELLOW}⚠️  Pouco espaço em disco: $(($AVAILABLE_SPACE/1024/1024))GB disponível${NC}"
    fi
}

echo "📋 VERIFICAÇÕES OBRIGATÓRIAS:"
echo "----------------------------"

FAILED_CHECKS=0

echo "🖥️  Sistema Operacional:"
uname -a

echo -e "\n🐍 Python:"
if ! check_python_version; then
    ((FAILED_CHECKS++))
fi

echo -e "\n📦 Git:"
if ! check_command git; then
    ((FAILED_CHECKS++))
fi

echo -e "\n🐳 Docker:"
if ! check_command docker; then
    echo -e "${YELLOW}⚠️  Docker não encontrado (opcional)${NC}"
fi

echo -e "\n📊 Ferramentas de Sistema:"
check_command curl || echo -e "${YELLOW}⚠️  curl não encontrado (será instalado)${NC}"
check_command wget || echo -e "${YELLOW}⚠️  wget não encontrado (será instalado)${NC}"
check_command pip3 || echo -e "${YELLOW}⚠️  pip3 não encontrado (será instalado)${NC}"

echo -e "\n🔌 Portas:"
check_ports

echo -e "\n🔐 Permissões:"
if ! check_permissions; then
    ((FAILED_CHECKS++))
fi

echo -e "\n💾 Espaço em Disco:"
check_disk_space

echo -e "\n📁 Usuário e Diretório:"
echo "Usuário: $(whoami)"
echo "Diretório: $(pwd)"
echo "HOME: $HOME"

echo -e "\n🐍 Verificando dependências Python críticas:"
python3 -c "
try:
    import asyncio
    print('✅ asyncio disponível')
except ImportError:
    print('❌ asyncio não disponível')

try:
    import json
    print('✅ json disponível')
except ImportError:
    print('❌ json não disponível')

try:
    import ssl
    print('✅ ssl disponível')
except ImportError:
    print('❌ ssl não disponível')
"

echo -e "\n📊 RESULTADO DAS PRÉ-CHECAGENS:"
echo "==============================="

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}🎉 TODAS AS VERIFICAÇÕES PASSARAM!${NC}"
    echo -e "${GREEN}✅ Sistema pronto para instalação do CRYPTOBOT SUPREMO GLOBAL${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILED_CHECKS verificação(ões) falharam${NC}"
    echo -e "${YELLOW}⚠️  Corrija os problemas antes de continuar${NC}"
    exit 1
fi
