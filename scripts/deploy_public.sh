#!/bin/bash

echo "🚀 INICIANDO DEPLOY PÚBLICO DO CRYPTOBOT SUPREMO..."

echo "📦 Iniciando serviços Docker..."
docker-compose up -d

echo "⏳ Aguardando inicialização completa..."
sleep 30

echo "🔍 Verificando saúde dos serviços..."
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:8050 || exit 1

echo "🌐 Configurando URLs públicas..."

./scripts/expose_public.sh

echo "✅ DEPLOY PÚBLICO CONCLUÍDO COM SUCESSO!"
echo ""
echo "🎯 URLS DE VERIFICAÇÃO:"
cat public_urls.json
echo ""
echo "🔗 FUNCIONALIDADES DISPONÍVEIS:"
echo "   ✅ API REST completa"
echo "   ✅ Dashboard interativo"  
echo "   ✅ Monitoramento Grafana"
echo "   ✅ Métricas Prometheus"
echo "   ✅ Documentação automática"
echo "   ✅ Health checks"
echo ""
echo "🏆 SISTEMA PRONTO PARA DEMONSTRAÇÃO PÚBLICA!"
