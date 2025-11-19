#!/usr/bin/env python3
"""
Script interativo para deletar relatórios de execução (comparisons).

Permite escolher um projeto específico ou deletar todos os relatórios.
Inclui confirmação antes de deletar.

Uso:
    python3 scripts/delete_comparison_reports.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.comparison import Comparison, ComparisonResult
from app.models.project import Project
from app.models.change_log import ChangeLog
from sqlalchemy import func


def list_projects():
    """Lista todos os projetos ativos"""
    projects = Project.query.filter_by(is_active=True).order_by(Project.name).all()
    return projects


def get_comparison_stats(project_id=None):
    """Obtém estatísticas de comparações"""
    query = Comparison.query
    
    if project_id:
        query = query.filter_by(project_id=project_id)
    
    total_comparisons = query.count()
    
    if total_comparisons > 0:
        # Get total results
        comparison_ids = [c.id for c in query.all()]
        total_results = ComparisonResult.query.filter(
            ComparisonResult.comparison_id.in_(comparison_ids)
        ).count()
        
        # Get total change logs
        total_change_logs = ChangeLog.query.filter(
            ChangeLog.comparison_id.in_(comparison_ids)
        ).count()
    else:
        total_results = 0
        total_change_logs = 0
    
    return {
        'total_comparisons': total_comparisons,
        'total_results': total_results,
        'total_change_logs': total_change_logs
    }


def delete_comparisons(project_id=None):
    """Deleta todas as comparações, opcionalmente filtradas por projeto"""
    try:
        # Get comparisons to delete
        query = Comparison.query
        if project_id:
            query = query.filter_by(project_id=project_id)
        
        comparisons = query.all()
        
        if not comparisons:
            print("Nenhuma comparação encontrada para deletar.")
            return {'success': True, 'deleted': 0}
        
        comparison_ids = [c.id for c in comparisons]
        
        # Delete change logs first
        change_logs = ChangeLog.query.filter(
            ChangeLog.comparison_id.in_(comparison_ids)
        ).all()
        
        deleted_change_logs = 0
        for change_log in change_logs:
            db.session.delete(change_log)
            deleted_change_logs += 1
        
        # Delete comparison results (cascade should handle this, but being explicit)
        results = ComparisonResult.query.filter(
            ComparisonResult.comparison_id.in_(comparison_ids)
        ).all()
        
        deleted_results = 0
        for result in results:
            db.session.delete(result)
            deleted_results += 1
        
        # Delete comparisons
        deleted_comparisons = 0
        for comparison in comparisons:
            db.session.delete(comparison)
            deleted_comparisons += 1
        
        db.session.commit()
        
        return {
            'success': True,
            'deleted_comparisons': deleted_comparisons,
            'deleted_results': deleted_results,
            'deleted_change_logs': deleted_change_logs
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }


def main():
    """Função principal do script"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("DELETAR RELATÓRIOS DE EXECUÇÃO")
        print("=" * 70)
        print()
        
        # List projects
        projects = list_projects()
        
        if not projects:
            print("Nenhum projeto encontrado.")
            return
        
        # Show all projects
        print("Projetos disponíveis:")
        print("-" * 70)
        for i, project in enumerate(projects, 1):
            stats = get_comparison_stats(project.id)
            print(f"{i}. {project.name} (ID: {project.id})")
            print(f"   Relatórios: {stats['total_comparisons']}")
            print(f"   Resultados: {stats['total_results']}")
            print()
        
        print(f"{len(projects) + 1}. TODOS OS PROJETOS")
        print()
        
        # Get user choice
        try:
            choice = input(f"Escolha um projeto (1-{len(projects) + 1}) ou 0 para cancelar: ").strip()
            
            if choice == '0':
                print("Operação cancelada.")
                return
            
            choice_num = int(choice)
            
            if choice_num < 1 or choice_num > len(projects) + 1:
                print("Escolha inválida.")
                return
            
            # Determine project_id
            project_id = None
            project_name = "TODOS OS PROJETOS"
            
            if choice_num <= len(projects):
                selected_project = projects[choice_num - 1]
                project_id = selected_project.id
                project_name = selected_project.name
            
            # Show statistics
            stats = get_comparison_stats(project_id)
            
            print()
            print("=" * 70)
            print("ESTATÍSTICAS")
            print("=" * 70)
            print(f"Projeto: {project_name}")
            print(f"Total de Relatórios: {stats['total_comparisons']}")
            print(f"Total de Resultados: {stats['total_results']}")
            print(f"Total de Change Logs: {stats['total_change_logs']}")
            print("=" * 70)
            print()
            
            if stats['total_comparisons'] == 0:
                print("Nenhum relatório encontrado para deletar.")
                return
            
            # Confirmation
            print("⚠️  ATENÇÃO: Esta ação não pode ser desfeita!")
            print()
            confirm = input(f"Tem certeza que deseja deletar TODOS os relatórios do projeto '{project_name}'? (digite 'SIM' para confirmar): ").strip()
            
            if confirm != 'SIM':
                print("Operação cancelada.")
                return
            
            # Delete
            print()
            print("Deletando relatórios...")
            result = delete_comparisons(project_id)
            
            if result['success']:
                print()
                print("=" * 70)
                print("✓ SUCESSO")
                print("=" * 70)
                print(f"Relatórios deletados: {result['deleted_comparisons']}")
                print(f"Resultados deletados: {result['deleted_results']}")
                print(f"Change Logs deletados: {result['deleted_change_logs']}")
                print("=" * 70)
            else:
                print()
                print("=" * 70)
                print("✗ ERRO")
                print("=" * 70)
                print(f"Erro ao deletar: {result.get('error', 'Erro desconhecido')}")
                print("=" * 70)
        
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
        except Exception as e:
            print(f"\nErro: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()

