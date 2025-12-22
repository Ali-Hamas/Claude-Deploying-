#!/bin/bash

echo "============================================"
echo "Installing Todo Backend Dependencies"
echo "============================================"
echo ""

# Check if pip is available
if ! python -m pip --version > /dev/null 2>&1; then
    echo "ERROR: pip is not installed or not in PATH"
    exit 1
fi

echo "Installing dependencies from requirements.txt..."
echo ""

# Install all dependencies
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn[standard] sqlmodel psycopg2-binary alembic openai mcp openai-agents python-jose[cryptography] passlib[argon2] argon2-cffi python-dotenv python-multipart dapr dapr-ext-fastapi

echo ""
echo "============================================"
echo "Verifying installations..."
echo "============================================"
echo ""

# Verify critical imports
python -c "import fastapi; print('✓ fastapi installed')" 2>/dev/null || echo "✗ fastapi FAILED"
python -c "import uvicorn; print('✓ uvicorn installed')" 2>/dev/null || echo "✗ uvicorn FAILED"
python -c "import sqlmodel; print('✓ sqlmodel installed')" 2>/dev/null || echo "✗ sqlmodel FAILED"
python -c "from jose import jwt; print('✓ python-jose installed')" 2>/dev/null || echo "✗ python-jose FAILED"
python -c "import passlib; print('✓ passlib installed')" 2>/dev/null || echo "✗ passlib FAILED"
python -c "import dapr; print('✓ dapr installed')" 2>/dev/null || echo "✗ dapr FAILED"
python -c "import dotenv; print('✓ python-dotenv installed')" 2>/dev/null || echo "✗ python-dotenv FAILED"

echo ""
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo ""
echo "You can now run:"
echo "  dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --resources-path ../dapr/components -- uvicorn main:app --reload --port 8000"
echo ""
