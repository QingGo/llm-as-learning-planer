from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage
from typing import Optional, Dict, Any
import logging
import os
import json
from datetime import datetime

from .config import settings

logger = logging.getLogger(__name__)

# 创建专门用于记录模型交互的日志器
model_interaction_logger = logging.getLogger("model_interaction")
model_interaction_logger.setLevel(logging.INFO)

# 创建日志目录
os.makedirs(settings.log_dir, exist_ok=True)

# 创建文件处理器，记录完整的模型交互

# 添加日期时间戳到日志文件名
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
model_interaction_handler = logging.FileHandler(
    os.path.join(settings.log_dir, f"model_interactions-{timestamp}.log"),
    encoding="utf-8",
)
model_interaction_formatter = logging.Formatter(
    "%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
model_interaction_handler.setFormatter(model_interaction_formatter)
model_interaction_logger.addHandler(model_interaction_handler)
# 避免日志传播到根日志器
model_interaction_logger.propagate = False


class ModelClient:
    """大模型客户端类，用于调用大模型API"""

    def __init__(
        self,
        platform: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """初始化大模型客户端

        Args:
            platform: 大模型平台，默认使用配置文件中的值
            model_name: 模型名称，默认使用配置文件中的值
            api_key: API密钥，默认使用配置文件中的值
        """
        self.platform = platform or settings.platform
        self.model_name = model_name or settings.model_name
        self.api_key = api_key or settings.api_key

        # 根据平台配置选择不同的客户端
        if self.platform == "deepseek":
            # 初始化DeepSeek客户端
            logger.info(f"Initializing DeepSeek client for model {self.model_name}")
            self.client = ChatDeepSeek(
                model=self.model_name,
                api_key=self.api_key,
                api_base=settings.deepseek_api_base,
                temperature=0.7,
                max_tokens=None,
                timeout=None,
            )
        elif self.platform == "google":
            # 初始化Google Generative AI客户端
            logger.info(
                f"Initializing Google Generative AI client for model {self.model_name}"
            )
            self.client = ChatGoogleGenerativeAI(
                model=self.model_name,
                api_key=self.api_key,
                temperature=0.7,
                max_tokens=None,
                timeout=None,
            )
        else:
            raise ValueError(
                f"Unsupported platform: {self.platform}. Supported platforms: deepseek, google"
            )

    def generate(self, prompt: str, **kwargs) -> str:
        """调用大模型生成文本

        Args:
            prompt: 输入的prompt
            **kwargs: 额外的参数

        Returns:
            大模型生成的文本
        """
        try:
            logger.info(
                f"Calling model {self.model_name} with prompt (first 200 chars): {prompt[:200]}..."
            )
            logger.debug(f"Full prompt: {prompt}")

            # 记录完整的模型交互
            interaction_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            model_interaction_logger.info(f"=== Interaction {interaction_id} Start ===")
            model_interaction_logger.info(f"Model: {self.model_name}")
            model_interaction_logger.info(f"Prompt:\n{prompt}")

            # 调用大模型
            messages = [HumanMessage(content=prompt)]
            response = self.client.invoke(messages)

            logger.info(
                f"Model {self.model_name} returned response (first 200 chars): {response.content[:200]}..."
            )
            logger.debug(f"Full response: {response.content}")

            # 记录完整的响应
            model_interaction_logger.info(f"Response:\n{response.content}")
            model_interaction_logger.info(f"=== Interaction {interaction_id} End ===\n")

            return response.content
        except Exception as e:
            logger.error(f"Error calling model {self.model_name}: {e}")
            logger.exception("Full error traceback:")
            raise

    def generate_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """调用大模型生成JSON格式的文本

        Args:
            prompt: 输入的prompt
            **kwargs: 额外的参数

        Returns:
            解析后的JSON数据
        """

        # 在prompt末尾添加要求输出JSON格式的指令
        json_prompt = f"{prompt}\n\n请严格按照JSON格式输出，不要包含任何其他文本。"

        logger.info(f"Generating JSON response with model {self.model_name}")
        response = self.generate(json_prompt, **kwargs)

        try:
            json_data = json.loads(response)
            logger.info(
                f"Successfully parsed JSON response from model {self.model_name}"
            )
            logger.debug(
                f"Parsed JSON data: {json.dumps(json_data, indent=2, ensure_ascii=False)}"
            )
            return json_data
        except json.JSONDecodeError as e:
            logger.error(
                f"Error parsing JSON response from model {self.model_name}: {e}"
            )
            logger.error(f"Raw response that failed to parse: {response}")
            logger.exception("Full error traceback:")
            raise
