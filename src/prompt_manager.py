import os
from typing import Dict


class PromptManager:
    """Prompt管理类，用于加载和格式化prompt"""

    def __init__(self, prompt_dir: str = "prompts"):
        """初始化PromptManager

        Args:
            prompt_dir: prompt文件所在目录
        """
        self.prompt_dir = prompt_dir
        self.prompts: Dict[str, str] = {}
        self._load_all_prompts()

    def _load_all_prompts(self) -> None:
        """加载所有prompt文件到内存"""
        if not os.path.exists(self.prompt_dir):
            raise FileNotFoundError(f"Prompt directory {self.prompt_dir} not found")

        for filename in os.listdir(self.prompt_dir):
            if filename.endswith(".md"):
                prompt_name = filename[:-3]  # 去掉.md后缀
                file_path = os.path.join(self.prompt_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    self.prompts[prompt_name] = f.read()

    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """获取指定名称的prompt，并进行格式化

        Args:
            prompt_name: prompt名称
            **kwargs: 用于格式化prompt的变量

        Returns:
            格式化后的prompt字符串
        """
        if prompt_name not in self.prompts:
            raise ValueError(f"Prompt {prompt_name} not found")

        prompt = self.prompts[prompt_name]
        return prompt.format(**kwargs)

    def reload_prompts(self) -> None:
        """重新加载所有prompt文件"""
        self._load_all_prompts()
