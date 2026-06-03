@echo off
echo ========================================
echo  Motor RAG Juridico - Projeto 1
echo ========================================

echo.
echo [1/4] Gerando dados de estresse...
python data/generate_data.py

echo.
echo [2/4] Processando cenario basico...
python src/main.py --input data/input_basico.json --output data/output_basico.json

echo.
echo [3/4] Processando cenario avancado...
python src/main.py --input data/input_avancado.json --output data/output_avancado.json

echo.
echo [4/4] Processando cenario de estresse...
python src/main.py --input data/input_estresse.json --output data/output_estresse.json

echo.
echo ========================================
echo  Concluido! Outputs gerados em data/
echo ========================================
pause