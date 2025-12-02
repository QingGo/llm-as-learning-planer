from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    # 大模型配置
    platform: str = "deepseek"  # 可选值: deepseek, google
    model_name: str = "deepseek-chat"
    api_key: str
    deepseek_api_base: str
    
    # 日志配置
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_to_file: bool = True
    
    # 输出配置
    output_dir: str = "plans"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False 


# 创建全局配置实例
settings = Settings()
