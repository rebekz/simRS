#!/bin/bash
# =============================================================================
# SIMRS One-Command Installation Script
# This script sets up the complete SIMRS development environment
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}=== SIMRS Installation Script ===${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not available${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"

# Create logs directory
mkdir -p backend/logs
echo -e "${GREEN}✓ Created logs directory${NC}"

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}Please review and update .env with your configuration${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Generate SSL certificates
echo ""
echo -e "${YELLOW}Generating SSL certificates...${NC}"
./scripts/generate-ssl.sh

# Pull Docker images
echo ""
echo -e "${YELLOW}Pulling Docker images...${NC}"
docker compose pull

# Build and start services
echo ""
echo -e "${YELLOW}Building and starting services...${NC}"
docker compose up -d --build

# Wait for services to be healthy
echo ""
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker compose ps | grep -q "healthy"; then
        echo -e "${GREEN}✓ Services are starting up${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -n "."
    sleep 2
done

echo ""

# Run database migrations
echo ""
echo -e "${YELLOW}Running database migrations...${NC}"
docker compose exec backend alembic upgrade head
echo -e "${GREEN}✓ Database migrations completed${NC}"

# Prompt for admin user creation
echo ""
echo -e "${YELLOW}Create admin user? (y/n)${NC}"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker compose exec backend python scripts/create_admin.py
else
    echo -e "${YELLOW}Skipping admin user creation${NC}"
    echo "You can create an admin user later by running:"
    echo "  docker compose exec backend python scripts/create_admin.py"
fi

# Final status
echo ""
echo -e "${GREEN}=== Installation Complete! ===${NC}"
echo ""
echo "Services are running at:"
echo -e "  ${BLUE}Frontend:${NC}    http://localhost:3000"
echo -e "  ${BLUE}Backend API:${NC} http://localhost:8000"
echo -e "  ${BLUE}API Docs:${NC}    http://localhost:8000/docs"
echo -e "  ${BLUE}ReDoc:${NC}       http://localhost:8000/redoc"
echo -e "  ${BLUE}HTTPS:${NC}       https://localhost (with self-signed cert)"
echo ""
echo "MinIO Console: http://localhost:9001"
echo "  Username: minioadmin"
echo "  Password: minioadmin"
echo ""
echo "Useful commands:"
echo "  View logs:        docker compose logs -f"
echo "  Stop services:    docker compose down"
echo "  Restart:          docker compose restart"
echo "  Run migrations:   docker compose exec backend alembic upgrade head"
echo "  Create admin:     docker compose exec backend python scripts/create_admin.py"
echo ""
echo -e "${YELLOW}Note: For production, update .env with strong passwords and proper secrets${NC}"
