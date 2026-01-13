#!/bin/bash
# Generate self-signed SSL certificates for development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="$SCRIPT_DIR/../nginx/ssl"
DAYS_VALID=365

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

echo "Generating self-signed SSL certificate..."

openssl req -x509 -nodes -days $DAYS_VALID -newkey rsa:2048 \
  -keyout "$SSL_DIR/key.pem" \
  -out "$SSL_DIR/cert.pem" \
  -subj "/C=ID/ST=Jakarta/L=Jakarta/O=SIMRS/OU=Development/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"

chmod 600 "$SSL_DIR/key.pem"
chmod 644 "$SSL_DIR/cert.pem"

echo "SSL certificate generated successfully!"
echo "Certificate: $SSL_DIR/cert.pem"
echo "Private key: $SSL_DIR/key.pem"
echo "Valid for: $DAYS_VALID days"
echo ""
echo "WARNING: This is a self-signed certificate for development only."
echo "For production, use Let's Encrypt or a proper CA-signed certificate."
