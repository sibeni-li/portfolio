# Deployment

## Server
- Ubuntu 24.04 VPS
- User: `flaskapp`
- App: `/home/flaskapp/portfolio`

## Services
| Service | Config Location |
|---------|-----------------|
| Flask app | `/etc/systemd/system/flaskapp.service` |
| Caddy | `/etc/caddy/Caddyfile` |

**Check:**
```bash
sudo systemctl status caddy
sudo systemctl status flaskapp
```

## Commands

**Restart app after code changes:**
```bash
cd ~/portfolio && git pull && sudo systemctl restart flaskapp
```

**Reload Caddy after config changes:**
```bash
sudo systemctl reload caddy
```

**View logs:**
```bash
journalctl -u flaskapp -f
journalctl -u caddy -f
```

## Environment
Create `/home/flaskapp/portfolio/.env` with:
```sh
ADMIN_USERNAME=xxxxx
ADMIN_PASSWORD=scrypt:xxxx
SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#FLASK_ENV=development
FLASK_ENV=prod
#REDIS_URL=redis://localhost:6379
```

## Ports
- 22: SSH
- 80/443: HTTP/HTTPS (Caddy)
- 8000: Gunicorn (localhost only)

## Certificate
Auto-renewed by Caddy via Let's Encrypt. Check with:
```bash
echo | openssl s_client -servername sibeni.dev -connect sibeni.dev:443 2>/dev/null | openssl x509 -noout -dates
```
