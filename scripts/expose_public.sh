#!/bin/bash

echo "🌐 Configurando URLs públicas..."

ngrok http 8000 --log=stdout > ngrok_api.log &
API_PID=$!

ngrok http 8050 --log=stdout > ngrok_dash.log &
DASH_PID=$!

sleep 10

API_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
DASH_URL=$(curl -s http://localhost:4041/api/tunnels | jq -r '.tunnels[0].public_url')

echo "✅ URLs PÚBLICAS CONFIGURADAS:"
echo "📊 API FastAPI: $API_URL"
echo "🎨 Dashboard: $DASH_URL"
echo "📋 API Docs: $API_URL/docs"
echo "💾 Prometheus: $API_URL:9090"

cat > public_urls.json << EOF
{
  "api_url": "$API_URL",
  "dashboard_url": "$DASH_URL", 
  "docs_url": "$API_URL/docs",
  "timestamp": "$(date -Iseconds)"
}
EOF

echo "📁 URLs salvas em public_urls.json"
