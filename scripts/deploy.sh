#!/bin/bash

set -e

echo "🚀 Iniciando deploy do CryptoBot Supremo Global..."

if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

echo "🔨 Building Docker images..."
docker compose build

echo "🗄️ Initializing database..."
if [ -f "sql/init.sql" ]; then
    echo "Database initialization script found"
fi

echo "⏹️ Stopping existing containers..."
docker compose down

echo "🚀 Starting services..."
docker compose up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "🔍 Running health checks..."

echo "Testing API health endpoint..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed"
    docker compose logs analysissupreme
    exit 1
fi

echo "Testing API metrics endpoint..."
if curl -f http://localhost:8000/api/dashboard/metrics > /dev/null 2>&1; then
    echo "✅ API metrics endpoint working"
else
    echo "⚠️ API metrics endpoint not responding (may be normal during startup)"
fi

echo "Testing dashboard..."
if curl -f http://localhost:8050 > /dev/null 2>&1; then
    echo "✅ Dashboard is accessible"
else
    echo "⚠️ Dashboard not responding (may be normal during startup)"
fi

echo "Testing Prometheus..."
if curl -f http://localhost:9090 > /dev/null 2>&1; then
    echo "✅ Prometheus is accessible"
else
    echo "⚠️ Prometheus not responding"
fi

echo "Testing Grafana..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Grafana is accessible"
else
    echo "⚠️ Grafana not responding"
fi

echo ""
echo "🎉 Deploy concluído!"
echo ""
echo "📊 Serviços disponíveis:"
echo "- API: http://localhost:8000/docs"
echo "- Dashboard: http://localhost:8050"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "🔍 Para verificar logs:"
echo "- docker compose logs analysissupreme"
echo "- docker compose logs dashboard"
echo ""
echo "⏹️ Para parar os serviços:"
echo "- docker compose down"
