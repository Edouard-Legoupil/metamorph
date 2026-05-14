# SSL Certificate Setup

This directory should contain your SSL certificates for production deployment.

## Certificate Files Required

- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key
- `chain.pem` - Intermediate certificate chain

## Generating Certificates

### Option 1: Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d metamorph.example.com -d www.metamorph.example.com

# Copy certificates to this directory
sudo cp /etc/letsencrypt/live/metamorph.example.com/fullchain.pem ./fullchain.pem
sudo cp /etc/letsencrypt/live/metamorph.example.com/privkey.pem ./privkey.pem
sudo cp /etc/letsencrypt/live/metamorph.example.com/chain.pem ./chain.pem

# Set proper permissions
sudo chmod 600 privkey.pem
sudo chown root:root *.pem
```

### Option 2: Self-Signed Certificates (for testing only)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout privkey.pem \
  -out fullchain.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=metamorph.example.com"

# Create chain.pem (same as fullchain.pem for self-signed)
cp fullchain.pem chain.pem
```

## Certificate Renewal

For Let's Encrypt certificates, set up automatic renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Set up cron job for automatic renewal
sudo crontab -e

# Add this line to run renewal twice daily
0 */12 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

## Security Best Practices

1. **Never commit private keys** to version control
2. **Use strong permissions**: `chmod 600` for private keys
3. **Rotate certificates** regularly (every 90 days recommended)
4. **Use HSTS** headers (already configured in production.conf)
5. **Monitor certificate expiration** dates

## Troubleshooting

**Common SSL issues:**

- **Mixed content warnings**: Ensure all resources use HTTPS
- **Certificate name mismatch**: Verify CN/SAN matches your domain
- **Expired certificates**: Set up automatic renewal
- **Permission issues**: Ensure nginx user can read certificate files

**Check SSL configuration:**

```bash
# Test SSL configuration
nginx -t

# Check certificate details
openssl x509 -in fullchain.pem -text -noout

# Test SSL connection
openssl s_client -connect metamorph.example.com:443 -servername metamorph.example.com
```
