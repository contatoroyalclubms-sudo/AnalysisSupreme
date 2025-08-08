#!/bin/bash

set -e

echo "📦 EMPACOTAMENTO DE RELEASE - CRYPTOBOT SUPREMO GLOBAL"
echo "====================================================="

VERSION=$(date +%Y.%m.%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RELEASE_NAME="cryptobot-supremo-global-v${VERSION}-${TIMESTAMP}"

echo "🏷️  Versão: $VERSION"
echo "📅 Timestamp: $TIMESTAMP"

mkdir -p releases/$RELEASE_NAME

echo "📋 Copiando arquivos essenciais..."
cp -r src/ releases/$RELEASE_NAME/
cp -r scripts/ releases/$RELEASE_NAME/
cp -r config/ releases/$RELEASE_NAME/
cp -r tests/ releases/$RELEASE_NAME/
cp -r docs/ releases/$RELEASE_NAME/

cp main.py releases/$RELEASE_NAME/
cp requirements.txt releases/$RELEASE_NAME/
cp Makefile releases/$RELEASE_NAME/
cp installer.sh releases/$RELEASE_NAME/
cp README.md releases/$RELEASE_NAME/
cp .env.example releases/$RELEASE_NAME/

if [ -f "docker-compose.yml" ]; then
    cp docker-compose.yml releases/$RELEASE_NAME/
fi

if [ -f "Dockerfile" ]; then
    cp Dockerfile releases/$RELEASE_NAME/
fi

cat > releases/$RELEASE_NAME/RELEASE_NOTES.md << EOF


- **Versão:** ${VERSION}
- **Data:** $(date)
- **Timestamp:** ${TIMESTAMP}


\`\`\`bash
unzip ${RELEASE_NAME}.zip
cd ${RELEASE_NAME}

bash installer.sh

nano .env

make test

bash scripts/run_paper.sh
\`\`\`


1. **Arbitragem** - 3 casos de uso
2. **Grid Trading** - 3 casos de uso  
3. **Momentum** - 3 casos de uso
4. **Scalping** - 3 casos de uso
5. **Mean Reversion** - 3 casos de uso
6. **Swing Trading** - 3 casos de uso


- ✅ 6 bots de trading automatizado
- ✅ 18 casos de uso implementados
- ✅ Sistema de IA avançado
- ✅ Observabilidade completa
- ✅ Paper trading seguro
- ✅ Backtest histórico
- ✅ Documentação em português


- Python 3.9+
- 1GB de espaço em disco
- Conexão com internet
- Chaves API das exchanges


Para suporte, consulte a documentação em docs/ ou entre em contato.
EOF

chmod +x releases/$RELEASE_NAME/installer.sh
chmod +x releases/$RELEASE_NAME/scripts/*.sh

echo "🗜️  Criando arquivo ZIP..."
cd releases
zip -r ${RELEASE_NAME}.zip ${RELEASE_NAME}/
cd ..

echo "🔐 Gerando checksums..."
cd releases
sha256sum ${RELEASE_NAME}.zip > SHA256SUMS.txt
md5sum ${RELEASE_NAME}.zip > MD5SUMS.txt
cd ..

cat > releases/release_info.json << EOF
{
    "nome": "${RELEASE_NAME}",
    "versao": "${VERSION}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "arquivos": {
        "release_zip": "${RELEASE_NAME}.zip",
        "sha256": "SHA256SUMS.txt",
        "md5": "MD5SUMS.txt"
    },
    "tamanho_mb": $(du -m releases/${RELEASE_NAME}.zip | cut -f1),
    "componentes": [
        "6 bots de trading",
        "18 casos de uso",
        "Sistema de IA",
        "Documentação completa",
        "Scripts operacionais"
    ],
    "status": "pronto_para_distribuicao"
}
EOF

echo "✅ Release empacotado com sucesso!"
echo "📦 Arquivo: releases/${RELEASE_NAME}.zip"
echo "🔐 Checksums: releases/SHA256SUMS.txt"
echo "📋 Info: releases/release_info.json"
echo "📊 Tamanho: $(du -h releases/${RELEASE_NAME}.zip | cut -f1)"
