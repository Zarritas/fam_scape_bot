#!/bin/bash
# Script para ejecutar tests con datos reales

echo "🧪 Ejecutando tests con datos reales..."
echo ""

# Tests del web scraper con HTML real
echo "📊 Tests del Web Scraper (HTML real):"
pytest tests/unit/test_real_data/test_web_scraper_real.py -v
echo ""

# Tests del PDF parser con PDFs reales
echo "📄 Tests del PDF Parser (PDFs reales):"
pytest tests/unit/test_real_data/test_pdf_parser_real.py -v
echo ""

# Tests de deduplicación con datos realistas
echo "🔄 Tests de Deduplicación:"
pytest tests/integration/test_deduplication_and_cleanup_real.py -v
echo ""

# Tests del workflow completo
echo "🔗 Tests del Workflow Completo:"
pytest tests/integration/test_full_workflow_real.py -v
echo ""

echo "✅ Todos los tests con datos reales completados!"