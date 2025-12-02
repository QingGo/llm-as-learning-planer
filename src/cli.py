import typer
import logging
from typing import Optional
import os
from logging.handlers import RotatingFileHandler
from .config import settings
from .workflow import run_workflow

# 初始化Typer应用
app = typer.Typer(
    name="planer",
    help="A tool to generate personalized learning plans using large language models",
)

# 配置日志
# 创建日志目录
if settings.log_to_file and not os.path.exists(settings.log_dir):
    os.makedirs(settings.log_dir, exist_ok=True)

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, settings.log_level))

# 清除现有的处理器
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, settings.log_level))
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)

# 文件处理器
if settings.log_to_file:
    from datetime import datetime

    # 添加日期时间戳到日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(settings.log_dir, f"planer-{timestamp}.log")
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # 文件日志记录所有级别
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)


@app.command()
def generate(
    background_file: str = typer.Option(
        "background.txt",
        "--background-file",
        "-bf",
        help="包含个人技术背景介绍的文件路径",
    ),
    goal_file: str = typer.Option(
        "goal.txt", "--goal-file", "-gf", help="包含学习目标的文件路径"
    ),
    output_dir: Optional[str] = typer.Option(
        None, "--output-dir", "-o", help="输出目录，默认使用配置文件中的值"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="启用详细日志输出"),
):
    """生成个性化学习计划"""
    try:
        # 如果启用了详细日志，调整日志级别
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info("开始生成学习计划...")

        # 从文件读取背景和目标
        with open(background_file, "r", encoding="utf-8") as f:
            background = f.read().strip()

        with open(goal_file, "r", encoding="utf-8") as f:
            goal = f.read().strip()

        logger.info(f"从文件读取背景信息: {background_file}")
        logger.info(f"从文件读取学习目标: {goal_file}")

        # 调用工作流生成计划
        result = run_workflow(background, goal, output_dir)

        logger.info("学习计划生成完成！")
        logger.info(f"总计划已保存到: {result.output_dir}/overall_plan.md")
        logger.info(f"日粒度计划已保存到: {result.output_dir}/daily/")

        typer.echo("✅ 学习计划生成完成！")
        typer.echo(f"📋 总计划已保存到: {result.output_dir}/overall_plan.md")
        typer.echo(f"📅 日粒度计划已保存到: {result.output_dir}/daily/")

    except FileNotFoundError as e:
        logger.error(f"文件未找到: {e}")
        typer.echo(f"❌ 文件未找到: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"生成学习计划时出错: {e}")
        typer.echo(f"❌ 生成学习计划时出错: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def version():
    """显示当前版本"""
    from importlib.metadata import version

    try:
        ver = version("llm-as-learning-planer")
        typer.echo(f"planer version: {ver}")
    except Exception:
        typer.echo("planer version: 0.1.0 (development)")


if __name__ == "__main__":
    app()
