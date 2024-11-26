import os

import pytest


def test_example_files_execute():
    """Test that all example files execute without errors"""
    examples_dir = "examples/stores"

    # Skip if examples directory doesn't exist
    if not os.path.exists(examples_dir):
        pytest.skip("Examples directory not found")

    for file in os.listdir(examples_dir):
        if file.endswith(".py"):
            example_path = os.path.join(examples_dir, file)
            print(f"Executing {file}")

            # Each example should execute without raising an exception
            try:
                exec(open(example_path).read())
            except Exception as e:
                pytest.fail(f"Failed to execute {file}: {str(e)}")
