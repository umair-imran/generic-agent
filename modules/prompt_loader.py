"""Dynamic prompt loader for use case-specific prompts."""
from pathlib import Path
from typing import Dict, Any
from utils import load_yaml
from utils.logger import LOGGER


class PromptLoader:
    """Load prompts dynamically based on use case configuration."""
    
    @staticmethod
    def load_prompt(prompt_file: str) -> str:
        """
        Load prompt from YAML file.
        
        Args:
            prompt_file: Path to the prompt YAML file (relative or absolute)
            
        Returns:
            The prompt string from the YAML file
            
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
            ValueError: If the prompt file doesn't contain a 'prompt' key
        """
        try:
            prompt_path = Path(prompt_file)
            
            # Try relative path first
            if not prompt_path.exists():
                # Try relative to project root
                prompt_path = Path(".") / prompt_file
                if not prompt_path.exists():
                    # Try relative to config directory
                    prompt_path = Path("config") / prompt_file
                    if not prompt_path.exists():
                        raise FileNotFoundError(
                            f"Prompt file not found: {prompt_file}. "
                            f"Tried: {prompt_file}, ./{prompt_file}, config/{prompt_file}"
                        )
            
            LOGGER.info(f"Loading prompt from: {prompt_path}")
            prompt_data = load_yaml(str(prompt_path))
            
            # Support both 'prompt' key and direct string content
            if isinstance(prompt_data, str):
                return prompt_data
            elif isinstance(prompt_data, dict):
                prompt = prompt_data.get("prompt", "")
                if not prompt:
                    raise ValueError(
                        f"Prompt file {prompt_file} does not contain a 'prompt' key"
                    )
                return prompt
            else:
                raise ValueError(f"Invalid prompt file format in {prompt_file}")
                
        except Exception as e:
            LOGGER.error(f"Failed to load prompt from {prompt_file}: {e}")
            raise
    
    @staticmethod
    def get_greeting(use_case_config: Dict[str, Any]) -> str:
        """
        Get greeting message for use case.
        
        Args:
            use_case_config: Use case configuration dictionary
            
        Returns:
            Greeting message string
        """
        return use_case_config.get("greeting", "Hello! How may I help you today?")





