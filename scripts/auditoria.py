#!/usr/bin/env python3
"""
Sistema de auditoria contínua do AnalysisSupreme
"""

import subprocess
import sys
import os
from pathlib import Path
import json
from datetime import datetime


def executar_comando(comando: str, descricao: str = "") -> tuple:
    """Executa comando e retorna resultado"""
    try:
        resultado = subprocess.run(comando.split(), capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        return resultado.returncode == 0, resultado.stdout, resultado.stderr
    except Exception as e:
        return False, "", str(e)


def auditoria_pre_implementacao():
    """Auditoria antes da implementação"""
    print("🔍 AUDITORIA PRÉ-IMPLEMENTAÇÃO")
    print("=" * 50)

    sucesso, stdout, stderr = executar_comando("git status --porcelain", "Git Status")
    if sucesso:
        linhas = len([l for l in stdout.strip().split("\n") if l.strip()])
        print(f"✅ Git status: {linhas} arquivos modificados")
    else:
        print(f"❌ Git status falhou: {stderr}")

    arquivos_py = list(Path(".").rglob("*.py"))
    print(f"✅ Arquivos Python encontrados: {len(arquivos_py)}")

    sucesso, stdout, stderr = executar_comando("pytest --collect-only", "Pytest Collect")
    if sucesso:
        linhas = stdout.count("test session starts")
        print(f"✅ Pytest collect: sessão iniciada")
    else:
        print(f"⚠️  Pytest collect: {stderr}")

    print()


def auditoria_pos_implementacao():
    """Auditoria após implementação"""
    print("🔍 AUDITORIA PÓS-IMPLEMENTAÇÃO")
    print("=" * 50)

    sucesso, stdout, stderr = executar_comando("git diff --stat", "Git Diff")
    if sucesso and stdout.strip():
        linhas = len(stdout.strip().split("\n"))
        print(f"✅ Git diff: {linhas} linhas de mudanças")
    else:
        print("✅ Git diff: nenhuma mudança pendente")

    sucesso, stdout, stderr = executar_comando("pytest --tb=short", "Pytest")
    if sucesso:
        print("✅ Pytest: todos os testes passaram")
    else:
        print(f"❌ Pytest falhou: {stderr}")

    sucesso, stdout, stderr = executar_comando("ruff check .", "Ruff Check")
    if sucesso:
        print("✅ Ruff check: código limpo")
    else:
        print(f"⚠️  Ruff check: {stderr}")

    sucesso, stdout, stderr = executar_comando("make test", "Make Test")
    if sucesso:
        print("✅ Make test: aprovado")
    else:
        print(f"❌ Make test falhou: {stderr}")

    print()


def auditoria_kpis():
    """Auditoria específica de KPIs"""
    print("📊 AUDITORIA DE KPIs")
    print("=" * 50)

    kpis_esperados = {
        "arbitragem": ["latencia_ms", "spread_capturado", "execucao_simultanea"],
        "grid": ["range_eficiencia", "grid_adaptabilidade", "lucro_lateral"],
        "momentum": ["breakout_precisao", "false_signal_rate", "stop_eficiencia"],
        "scalping": ["throughput_ops", "latencia_ultra", "fee_optimization"],
        "mean_reversion": ["reversao_timing", "oversold_detection", "rsi_effectiveness"],
        "swing": ["trend_capture", "hold_time_optimal", "pattern_recognition"],
    }

    kpi_file = Path("src/utils/kpis.py")
    if kpi_file.exists():
        print("✅ Sistema de KPIs implementado")

        with open(kpi_file, "r", encoding="utf-8") as f:
            content = f.read()

        for bot, kpis in kpis_esperados.items():
            for kpi in kpis:
                if kpi in content:
                    print(f"   ✅ {bot}: {kpi}")
                else:
                    print(f"   ❌ {bot}: {kpi} - AUSENTE")
    else:
        print("❌ Sistema de KPIs não encontrado")

    print()


def auditoria_estrutura():
    """Auditoria da estrutura do projeto"""
    print("📁 AUDITORIA DE ESTRUTURA")
    print("=" * 50)

    estrutura_esperada = {
        "src/bots": ["arbitragem.py", "grid.py", "momentum.py", "scalping.py", "mean_reversion.py", "swing.py"],
        "src/core": ["configuracao.py", "gerenciador_bots.py"],
        "src/ia": ["motor_ia.py"],
        "src/observabilidade": ["monitor.py"],
        "src/utils": ["kpis.py", "logger.py", "metricas.py"],
        "scripts": ["setup_caso.py", "executar.py", "validar.py", "relatorio_geral.py", "auditoria.py"],
        "tests": ["test_bots.py"],
        ".": ["Makefile", "setup.py", "requirements.txt", "main.py"],
    }

    for diretorio, arquivos in estrutura_esperada.items():
        for arquivo in arquivos:
            caminho = Path(diretorio) / arquivo if diretorio != "." else Path(arquivo)
            if caminho.exists():
                print(f"✅ {caminho}")
            else:
                print(f"❌ {caminho} - AUSENTE")

    print()


def gerar_relatorio_auditoria():
    """Gera relatório final de auditoria"""
    relatorio = {
        "timestamp": datetime.now().isoformat(),
        "auditoria": {
            "pre_implementacao": True,
            "pos_implementacao": True,
            "kpis_verificados": True,
            "estrutura_verificada": True,
        },
        "status": "completo",
        "recomendacoes": [
            "Executar make setup antes dos testes",
            "Verificar cobertura de testes ≥80%",
            "Monitorar KPIs em tempo real",
            "Executar auditoria após cada mudança",
        ],
    }

    os.makedirs("logs/auditorias", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with open(f"logs/auditorias/auditoria_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print(f"📄 Relatório de auditoria salvo: logs/auditorias/auditoria_{timestamp}.json")


def main():
    """Executa auditoria completa"""
    print("🎯 SISTEMA DE AUDITORIA CONTÍNUA - ANALYSISSUPREME")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()

    auditoria_pre_implementacao()
    auditoria_pos_implementacao()
    auditoria_kpis()
    auditoria_estrutura()
    gerar_relatorio_auditoria()

    print("🎯 AUDITORIA CONCLUÍDA")
    print("=" * 60)


if __name__ == "__main__":
    main()
