#!/usr/bin/env python3
"""Validation script for Prefect 3.x migration."""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        # Test core imports
        import prefect
        print(f"✓ Prefect {prefect.__version__} imported successfully")
        
        # Test that we have Prefect 3.x
        major_version = int(prefect.__version__.split('.')[0])
        if major_version >= 3:
            print("✓ Prefect 3.x detected")
        else:
            print(f"⚠ Warning: Prefect {prefect.__version__} detected, but 3.x recommended")
        
        # Test package imports
        from src.customer_flows import get_settings, example_analysis_flow, create_analysis_crew
        print("✓ Customer flows package imported successfully")
        
        # Test configuration
        settings = get_settings()
        print(f"✓ Settings loaded (environment: {settings.environment})")
        
        # Test logging
        from src.customer_flows.utils.logging import get_logger, configure_logging
        configure_logging()
        logger = get_logger(__name__)
        logger.info("Testing logging functionality")
        print("✓ Logging configured successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        traceback.print_exc()
        return False


def test_flow_creation():
    """Test that flows can be created and validated."""
    print("\nTesting flow creation...")
    
    try:
        from src.customer_flows.flows.example_flow import example_analysis_flow
        
        # Test flow function exists
        assert callable(example_analysis_flow), "Flow must be callable"
        print("✓ Flow function is callable")
        
        # Test flow metadata
        flow_obj = example_analysis_flow
        assert hasattr(flow_obj, 'name'), "Flow must have a name"
        assert hasattr(flow_obj, 'description'), "Flow must have a description"
        print(f"✓ Flow metadata: {flow_obj.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Flow creation test failed: {e}")
        traceback.print_exc()
        return False


def test_crew_creation():
    """Test that CrewAI crews can be created."""
    print("\nTesting CrewAI crew creation...")
    
    try:
        from src.customer_flows.agents.example_crew import create_analysis_crew, validate_crew_configuration
        
        # Test crew creation
        sample_data = {
            "original": "test data",
            "word_count": 2,
            "character_count": 9,
        }
        
        crew = create_analysis_crew(sample_data)
        print("✓ CrewAI crew created successfully")
        
        # Test crew validation
        validation_result = validate_crew_configuration(crew)
        if validation_result["is_valid"]:
            print("✓ Crew configuration is valid")
        else:
            print("⚠ Crew configuration has issues:")
            for error in validation_result["errors"]:
                print(f"  - {error}")
        
        return True
        
    except Exception as e:
        print(f"✗ CrewAI test failed: {e}")
        traceback.print_exc()
        return False


def test_cli_interface():
    """Test that CLI interface is working."""
    print("\nTesting CLI interface...")
    
    try:
        from src.customer_flows.cli import app
        
        # Test that CLI app exists
        assert app is not None, "CLI app must exist"
        print("✓ CLI app imported successfully")
        
        # Test CLI commands exist
        commands = [cmd.name for cmd in app.commands.values()]
        expected_commands = ["info", "run-flow", "list-flows", "test-crew", "deploy", "validate-config"]
        
        for cmd in expected_commands:
            if cmd in commands:
                print(f"✓ CLI command '{cmd}' found")
            else:
                print(f"⚠ CLI command '{cmd}' missing")
        
        return True
        
    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        traceback.print_exc()
        return False


def test_deployment_scripts():
    """Test that deployment scripts are valid."""
    print("\nTesting deployment configurations...")
    
    try:
        # Test deployment script import
        import deployments.prefect_deployments as deploy_module
        print("✓ Deployment module imported successfully")
        
        # Test deployment functions exist
        functions = ["create_example_flow_deployment", "create_all_deployments", "deploy_flows"]
        for func_name in functions:
            if hasattr(deploy_module, func_name):
                print(f"✓ Deployment function '{func_name}' found")
            else:
                print(f"⚠ Deployment function '{func_name}' missing")
        
        # Check Docker files exist
        docker_files = [
            "deployments/docker/Dockerfile",
            "deployments/docker/docker-compose.yml",
            "deployments/.env.example"
        ]
        
        for file_path in docker_files:
            if Path(file_path).exists():
                print(f"✓ Docker file '{file_path}' found")
            else:
                print(f"⚠ Docker file '{file_path}' missing")
        
        return True
        
    except Exception as e:
        print(f"✗ Deployment test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all validation tests."""
    print("🚀 Validating Prefect 3.x Migration")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_flow_creation,
        test_crew_creation,
        test_cli_interface,
        test_deployment_scripts,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Migration appears successful.")
        return 0
    else:
        print("⚠ Some tests failed. Please review and fix issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
