# 🚀 CryptoBot Supremo - Deployment Guide

## Quick Deploy Options

### 1. Railway (Recommended - Easiest)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway up
```

### 2. DigitalOcean App Platform
```bash
# Install doctl
# Configure app.yaml and deploy
doctl apps create --spec app.yaml
```

### 3. Heroku
```bash
# Install Heroku CLI
heroku create cryptobot-supremo
heroku config:set $(cat .env.production | grep -v '^#' | xargs)
git push heroku main
```

### 4. Docker Compose (Local/VPS)
```bash
# Copy and configure environment
cp .env.production.example .env.production
# Edit .env.production with your values

# Deploy
./deploy.sh docker
```

## Configuration Files

| File | Purpose |
|------|---------|
| `Dockerfile.prod` | Production Docker image |
| `docker-compose.prod.yml` | Full stack with PostgreSQL, Redis, nginx |
| `railway.json` | Railway platform configuration |
| `app.yaml` | DigitalOcean App Platform spec |
| `Procfile` | Heroku process configuration |
| `.env.production` | Production environment variables |
| `nginx.conf` | Reverse proxy and SSL configuration |
| `requirements.prod.txt` | Optimized production dependencies |
| `gunicorn.conf.py` | WSGI server configuration |
| `deploy.sh` | Automated deployment script |

## Environment Variables

Copy `.env.production.example` to `.env.production` and configure:

### Required Variables
- `SECRET_KEY` - Strong secret key (32+ characters)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `API_KEY_BINANCE` - Binance API key
- `API_SECRET_BINANCE` - Binance API secret

### Security Variables
- `JWT_SECRET_KEY` - JWT signing key
- `CORS_ORIGINS` - Allowed origins for CORS
- `ALLOWED_HOSTS` - Allowed hostnames

## Deployment Process

1. **Configure Environment**
   ```bash
   cp .env.production.example .env.production
   # Edit .env.production with your values
   ```

2. **Choose Platform and Deploy**
   ```bash
   # Interactive deployment
   ./deploy.sh
   
   # Or specific platform
   ./deploy.sh railway
   ./deploy.sh heroku
   ./deploy.sh digitalocean
   ./deploy.sh docker
   ```

3. **Verify Deployment**
   ```bash
   # Health check
   ./deploy.sh health https://your-app-url.com
   ```

## Monitoring

- **Prometheus**: Metrics collection on port 9090
- **Grafana**: Dashboards on port 3000
- **Health Check**: `/health` endpoint
- **Metrics**: `/metrics` endpoint (restricted access)

## Security Features

- HTTPS/SSL termination
- Rate limiting (60 req/min)
- CORS protection
- Security headers
- JWT authentication
- Environment-based secrets

## Performance Optimizations

- Gunicorn with 4 workers
- Redis caching
- Connection pooling
- Gzip compression
- Static file serving
- Health checks

## Troubleshooting

### Common Issues

1. **Environment Variables Not Set**
   ```bash
   # Check required variables
   ./deploy.sh
   ```

2. **Database Connection Issues**
   ```bash
   # Verify DATABASE_URL format
   postgresql://user:password@host:port/database
   ```

3. **Redis Connection Issues**
   ```bash
   # Verify REDIS_URL format
   redis://host:port/db
   ```

### Logs

```bash
# Docker Compose logs
docker-compose -f docker-compose.prod.yml logs -f

# Railway logs
railway logs

# Heroku logs
heroku logs --tail
```

## Scaling

### Horizontal Scaling
- Increase worker count in `gunicorn.conf.py`
- Use load balancer for multiple instances
- Scale database with read replicas

### Vertical Scaling
- Increase instance size on platform
- Adjust worker count based on CPU cores
- Monitor memory usage and adjust

## Backup Strategy

- Automated database backups (daily at 2 AM)
- 30-day retention policy
- Redis persistence enabled
- Application logs rotation

## Support

For deployment issues:
1. Check logs for error messages
2. Verify environment variables
3. Test health check endpoint
4. Review platform-specific documentation
