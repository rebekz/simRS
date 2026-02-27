# Suggested Commands

## Development

### Start Services
```bash
docker compose up -d
```

### View Logs
```bash
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
```

### Backend Commands
```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Create admin user
docker compose exec backend python scripts/create_admin.py

# Run tests
docker compose exec backend pytest

# Linting
docker compose exec backend black .
docker compose exec backend isort .
docker compose exec backend flake8
docker compose exec backend mypy .
```

### Frontend Commands
```bash
# Development
cd frontend && npm run dev

# Build
cd frontend && npm run build

# Lint
cd frontend && npm run lint

# Type check
cd frontend && npm run type-check

# Storybook
cd frontend && npm run storybook
```

### Stop Services
```bash
docker compose down
```

## Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- HTTPS: https://localhost
