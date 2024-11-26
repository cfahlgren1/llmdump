import os
from unittest.mock import MagicMock, patch

import pytest


def test_example_files_execute():
    """Test that all example files execute without errors"""
    examples_dir = "examples/observers"

    # Skip if examples directory doesn't exist
    if not os.path.exists(examples_dir):
        pytest.skip("Examples directory not found")

    # Create mock clients
    mock_openai = MagicMock()
    mock_openai.chat.completions.create.return_value = {}

    mock_aisuite = MagicMock()
    mock_aisuite.chat.completions.create.return_value = {}

    # Mock classes that make external calls
    mocks = {
        "openai.OpenAI": patch("openai.OpenAI", return_value=mock_openai),
        "aisuite.Client": patch("aisuite.Client", return_value=mock_aisuite),
    }

    # Start all the mocks
    for mock in mocks.values():
        mock.start()

    try:
        for file in os.listdir(examples_dir):
            if file.endswith(".py"):
                example_path = os.path.join(examples_dir, file)
                print(f"Executing {file}")

                # Each example should execute without raising an exception
                try:
                    exec(open(example_path).read())
                except Exception as e:
                    pytest.fail(f"Failed to execute {file}: {str(e)}")
    finally:
        # Stop all mocks even if there's an error
        for mock in mocks.values():
            mock.stop()
