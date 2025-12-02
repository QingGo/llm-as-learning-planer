from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
import logging
import os
import json
from .config import settings
from .model_client import ModelClient
from .prompt_manager import PromptManager

logger = logging.getLogger(__name__)


class PlanState(BaseModel):
    """工作流状态类"""
    # 输入数据
    user_background: str
    user_goal: str
    original_question: str
    
    # 生成的计划
    initial_plan: str = ""
    revised_plans: List[str] = []
    comparison_result: str = ""
    final_plan: str = ""
    daily_plans: Dict[str, str] = {}
    
    # 配置
    output_dir: str = settings.output_dir
    
    # 客户端和管理器
    model_client: ModelClient = None
    prompt_manager: PromptManager = None
    
    class Config:
        arbitrary_types_allowed = True


def init_clients(state: PlanState) -> PlanState:
    """初始化客户端和管理器"""
    logger.info("=== Entering init_clients node ===")
    try:
        logger.debug("Creating ModelClient instance...")
        state.model_client = ModelClient()
        logger.debug("Creating PromptManager instance...")
        state.prompt_manager = PromptManager()
        logger.info("=== Exiting init_clients node ===")
        return state
    except Exception as e:
        logger.error(f"Error in init_clients node: {e}")
        logger.exception("Full error traceback:")
        raise


def generate_initial_plan(state: PlanState) -> PlanState:
    """生成初始学习计划"""
    logger.info("=== Entering generate_initial_plan node ===")
    try:
        logger.debug("Getting initial_plan prompt...")
        # 获取初始计划prompt
        prompt = state.prompt_manager.get_prompt(
            "initial_plan",
            user_background=state.user_background,
            user_goal=state.user_goal
        )
        
        logger.debug("Calling model to generate initial plan...")
        # 调用大模型生成初始计划
        state.initial_plan = state.model_client.generate(prompt)
        logger.info("Initial plan generated successfully")
        logger.info("=== Exiting generate_initial_plan node ===")
        return state
    except Exception as e:
        logger.error(f"Error in generate_initial_plan node: {e}")
        logger.exception("Full error traceback:")
        raise


def critique_plan(state: PlanState) -> PlanState:
    """对初始计划进行批判性审查"""
    logger.info("=== Entering critique_plan node ===")
    try:
        logger.debug("Starting critique process, will generate 3 revised plans...")
        
        # 生成三份修正计划
        state.revised_plans = []
        for i in range(3):
            logger.info(f"Generating revised plan {i+1}/3...")
            
            logger.debug(f"Getting critical_think prompt for revision {i+1}...")
            # 获取批判性思维prompt
            prompt = state.prompt_manager.get_prompt(
                "critical_think",
                user_question=state.original_question,
                model_answer=state.initial_plan
            )
            
            logger.debug(f"Calling model to generate revised plan {i+1}...")
            # 调用大模型生成修正计划
            revised_plan = state.model_client.generate(prompt)
            state.revised_plans.append(revised_plan)
            logger.info(f"Revised plan {i+1}/3 generated successfully")
        
        logger.info(f"Generated {len(state.revised_plans)} revised plans")
        logger.info("=== Exiting critique_plan node ===")
        return state
    except Exception as e:
        logger.error(f"Error in critique_plan node: {e}")
        logger.exception("Full error traceback:")
        raise


def compare_plans(state: PlanState) -> PlanState:
    """对比三份修正计划，分析它们的优点和缺点"""
    logger.info("=== Entering compare_plans node ===")
    try:
        logger.debug("Getting compare_plans prompt...")
        # 获取对比方案prompt
        prompt = state.prompt_manager.get_prompt(
            "compare_plans",
            original_question=state.original_question,
            answerA=state.revised_plans[0],
            answerB=state.revised_plans[1],
            answerC=state.revised_plans[2]
        )
        
        logger.debug("Calling model to compare plans...")
        # 调用大模型对比计划
        comparison_result = state.model_client.generate(prompt)
        
        # 从对比结果中提取最佳计划
        logger.debug("Extracting best plan from comparison result...")
        state.comparison_result = comparison_result
        logger.info("Plans compared successfully")
        logger.info("=== Exiting compare_plans node ===")
        return state
    except Exception as e:
        logger.error(f"Error in compare_plans node: {e}")
        logger.exception("Full error traceback:")
        raise


def generate_final_plan(state: PlanState) -> PlanState:
    """生成最终的双周粒度计划"""
    logger.info("=== Entering generate_final_plan node ===")
    try:
        logger.debug("Getting final_plan prompt...")
        # 获取最终计划prompt
        prompt = state.prompt_manager.get_prompt(
            "final_plan",
            original_question=state.original_question,
            planA=state.revised_plans[0],
            planB=state.revised_plans[1],
            planC=state.revised_plans[2],
            comparison_result=state.comparison_result
        )
        
        logger.debug("Calling model to generate final plan...")
        # 调用大模型生成最终计划
        state.final_plan = state.model_client.generate(prompt)
        logger.info("Final plan generated successfully")
        
        # 立即保存最终计划
        logger.info("Saving final plan immediately...")
        # 确保输出目录存在
        os.makedirs(state.output_dir, exist_ok=True)
        final_plan_path = os.path.join(state.output_dir, "overall_plan.md")
        with open(final_plan_path, "w", encoding="utf-8") as f:
            f.write(state.final_plan)
        logger.info(f"Final plan saved to {final_plan_path}")
        
        # 保存JSON格式的最终计划
        try:
            # 解析JSON
            final_plan_json = json.loads(state.final_plan)
            # 保存JSON文件
            final_plan_json_path = os.path.join(state.output_dir, "overall_plan.json")
            with open(final_plan_json_path, "w", encoding="utf-8") as f:
                json.dump(final_plan_json, f, indent=2, ensure_ascii=False)
            logger.info(f"Final plan JSON saved to {final_plan_json_path}")
            
            # 生成并保存Markdown格式的最终计划
            final_plan_md = json_to_markdown(final_plan_json)
            final_plan_md_path = os.path.join(state.output_dir, "overall_plan_markdown.md")
            with open(final_plan_md_path, "w", encoding="utf-8") as f:
                f.write(final_plan_md)
            logger.info(f"Final plan Markdown saved to {final_plan_md_path}")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse final plan as JSON: {e}")
        
        logger.info("=== Exiting generate_final_plan node ===")
        return state
    except Exception as e:
        logger.error(f"Error in generate_final_plan node: {e}")
        logger.exception("Full error traceback:")
        raise


def generate_daily_plans(state: PlanState) -> PlanState:
    """为每双周生成详细的日粒度计划"""
    logger.info("=== Entering generate_daily_plans node ===")
    try:
        # 假设最终计划包含6个双周（共12周）
        total_weeks = 6
        logger.info(f"Will generate daily plans for {total_weeks} bi-weekly periods")
        
        state.daily_plans = {}
        # 确保输出目录存在
        daily_dir = os.path.join(state.output_dir, "daily")
        os.makedirs(daily_dir, exist_ok=True)
        
        for i in range(total_weeks):
            week_start = i * 2 + 1
            week_end = week_start + 1
            week_range = f"Week {week_start}-{week_end}"
            
            logger.info(f"Generating daily plan for {week_range} ({i+1}/{total_weeks})...")
            
            logger.debug(f"Getting daily_plan prompt for {week_range}...")
            # 获取每日计划prompt
            prompt = state.prompt_manager.get_prompt(
                "daily_plan",
                user_background=state.user_background,
                biweekly_plan=state.final_plan,
                week_range=week_range
            )
            
            logger.debug(f"Calling model to generate daily plan for {week_range}...")
            # 调用大模型生成日粒度计划
            daily_plan = state.model_client.generate(prompt)
            state.daily_plans[week_range] = daily_plan
            logger.info(f"Daily plan for {week_range} generated successfully")
            
            # 立即保存该双周的日计划
            logger.info(f"Saving daily plan for {week_range} immediately...")
            # 将"Week 1-2"转换为"week1-2"
            filename = week_range.lower().replace(" ", "") + ".md"
            daily_plan_path = os.path.join(daily_dir, filename)
            with open(daily_plan_path, "w", encoding="utf-8") as f:
                f.write(daily_plan)
            logger.info(f"Daily plan saved to {daily_plan_path}")
            
            # 保存JSON和Markdown格式的每日计划
            try:
                # 解析JSON
                daily_plan_json = json.loads(daily_plan)
                # 保存JSON文件
                daily_plan_json_path = os.path.join(daily_dir, filename.replace(".md", ".json"))
                with open(daily_plan_json_path, "w", encoding="utf-8") as f:
                    json.dump(daily_plan_json, f, indent=2, ensure_ascii=False)
                logger.info(f"Daily plan JSON saved to {daily_plan_json_path}")
                
                # 生成并保存Markdown格式的每日计划
                daily_plan_md = json_to_daily_markdown(daily_plan_json)
                daily_plan_md_path = os.path.join(daily_dir, filename.replace(".md", "_markdown.md"))
                with open(daily_plan_md_path, "w", encoding="utf-8") as f:
                    f.write(daily_plan_md)
                logger.info(f"Daily plan Markdown saved to {daily_plan_md_path}")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse daily plan for {week_range} as JSON: {e}")
        
        logger.info(f"Generated {len(state.daily_plans)} daily plans")
        logger.info("=== Exiting generate_daily_plans node ===")
        return state
    except Exception as e:
        logger.error(f"Error in generate_daily_plans node: {e}")
        logger.exception("Full error traceback:")
        raise


def json_to_markdown(json_data: dict) -> str:
    """将JSON格式的学习计划转换为Markdown格式
    
    Args:
        json_data: JSON格式的学习计划数据
        
    Returns:
        Markdown格式的学习计划字符串
    """
    md_content = []
    
    # 添加标题
    md_content.append(f"# {json_data.get('title', '学习计划')}")
    md_content.append("")
    
    # 添加概述
    overview = json_data.get('overview', '')
    if overview:
        md_content.append("## 计划概述")
        md_content.append(overview)
        md_content.append("")
    
    # 添加计划时长
    duration = json_data.get('duration', '')
    if duration:
        md_content.append(f"**计划时长**: {duration}")
        md_content.append("")
    
    # 添加最终目标
    final_goal = json_data.get('final_goal', '')
    if final_goal:
        md_content.append("## 最终目标")
        md_content.append(final_goal)
        md_content.append("")
    
    # 添加成功标准
    success_criteria = json_data.get('success_criteria', [])
    if success_criteria:
        md_content.append("## 成功标准")
        for criterion in success_criteria:
            md_content.append(f"- {criterion}")
        md_content.append("")
    
    # 添加风险管理
    risk_management = json_data.get('risk_notes', '')
    if risk_management:
        md_content.append("## 风险提示")
        md_content.append(risk_management)
        md_content.append("")
    
    # 添加里程碑
    milestones = json_data.get('milestones', [])
    if milestones:
        md_content.append("## 双周里程碑")
        for milestone in milestones:
            week_range = milestone.get('week_range', '未知')
            md_content.append(f"### {week_range}")
            
            goal = milestone.get('goal', '')
            if goal:
                md_content.append(f"**目标**: {goal}")
                md_content.append("")
            
            skills = milestone.get('skills', [])
            if skills:
                md_content.append("**需掌握技能**:")
                for skill in skills:
                    md_content.append(f"- {skill}")
                md_content.append("")
            
            projects = milestone.get('projects', [])
            if projects:
                md_content.append("**项目产出要求**:")
                for project in projects:
                    md_content.append(f"- {project}")
                md_content.append("")
            
            resources = milestone.get('resources', [])
            if resources:
                md_content.append("**推荐学习资源**:")
                for resource in resources:
                    md_content.append(f"- {resource}")
                md_content.append("")
    
    return '\n'.join(md_content)


def json_to_daily_markdown(json_data: dict) -> str:
    """将JSON格式的每日计划转换为Markdown格式
    
    Args:
        json_data: JSON格式的每日计划数据
        
    Returns:
        Markdown格式的每日计划字符串
    """
    md_content = []
    
    # 添加标题
    week_range = json_data.get('week_range', '未知')
    md_content.append(f"# {week_range} 每日学习计划")
    md_content.append("")
    
    # 添加总时长
    total_hours = json_data.get('total_hours', 0)
    md_content.append(f"**总学习时长**: {total_hours} 小时")
    md_content.append("")
    
    # 添加每日计划
    daily_schedule = json_data.get('daily_schedule', [])
    if daily_schedule:
        for day_schedule in daily_schedule:
            day = day_schedule.get('day', '未知')
            date = day_schedule.get('date', '')
            md_content.append(f"## {day} {date}")
            
            # 添加当日总时长
            day_total_hours = day_schedule.get('total_hours', 0)
            md_content.append(f"**当日总时长**: {day_total_hours} 小时")
            md_content.append("")
            
            # 添加休息时间
            rest_time = day_schedule.get('rest_time', '')
            if rest_time:
                md_content.append(f"**休息时间安排**: {rest_time}")
                md_content.append("")
            
            # 添加学习建议
            learning_tips = day_schedule.get('learning_tips', '')
            if learning_tips:
                md_content.append(f"**学习建议**: {learning_tips}")
                md_content.append("")
            
            # 添加当日任务
            tasks = day_schedule.get('tasks', [])
            if tasks:
                md_content.append("### 当日任务")
                for task in tasks:
                    title = task.get('title', '未知任务')
                    duration = task.get('duration_hours', 0)
                    description = task.get('description', '')
                    skills = task.get('skills', [])
                    expected_outcome = task.get('expected_outcome', '')
                    
                    md_content.append(f"#### {title} ({duration}小时)")
                    if description:
                        md_content.append(f"**任务描述**: {description}")
                    if skills:
                        md_content.append(f"**涉及技能**: {', '.join(skills)}")
                    if expected_outcome:
                        md_content.append(f"**预期成果**: {expected_outcome}")
                    md_content.append("")
    
    # 添加双周总结
    week_summary = json_data.get('week_summary', '')
    if week_summary:
        md_content.append("## 双周学习总结和回顾建议")
        md_content.append(week_summary)
    
    return '\n'.join(md_content)


def save_plans(state: PlanState) -> PlanState:
    """保存生成的计划到文件"""
    logger.info("=== Entering save_plans node ===")
    try:
        logger.debug(f"Output directory: {state.output_dir}")
        
        # 确保输出目录存在
        os.makedirs(state.output_dir, exist_ok=True)
        daily_dir = os.path.join(state.output_dir, "daily")
        os.makedirs(daily_dir, exist_ok=True)
        logger.debug(f"Created output directories: {state.output_dir} and {daily_dir}")
        
        # 保存最终双周计划
        final_plan_path = os.path.join(state.output_dir, "overall_plan.md")
        logger.debug(f"Saving final plan to {final_plan_path}...")
        with open(final_plan_path, "w", encoding="utf-8") as f:
            f.write(state.final_plan)
        logger.info(f"Final plan saved to {final_plan_path}")
        
        # 保存每日计划
        logger.info(f"Saving {len(state.daily_plans)} daily plans...")
        for week_range, daily_plan in state.daily_plans.items():
            # 将"Week 1-2"转换为"week1-2"
            filename = week_range.lower().replace(" ", "") + ".md"
            daily_plan_path = os.path.join(daily_dir, filename)
            logger.debug(f"Saving daily plan for {week_range} to {daily_plan_path}...")
            with open(daily_plan_path, "w", encoding="utf-8") as f:
                f.write(daily_plan)
            logger.info(f"Daily plan for {week_range} saved to {daily_plan_path}")
        
        logger.info("=== Exiting save_plans node ===")
        return state
    except Exception as e:
        logger.error(f"Error in save_plans node: {e}")
        logger.exception("Full error traceback:")
        raise


def create_workflow() -> StateGraph:
    """创建工作流图"""
    logger.info("=== Creating workflow graph ===")
    try:
        # 创建状态图
        workflow = StateGraph(PlanState)
        logger.debug("StateGraph created")
        
        # 添加节点
        logger.debug("Adding nodes to workflow...")
        workflow.add_node("init_clients", init_clients)
        workflow.add_node("generate_initial_plan", generate_initial_plan)
        workflow.add_node("critique_plan", critique_plan)
        workflow.add_node("compare_plans", compare_plans)
        workflow.add_node("generate_final_plan", generate_final_plan)
        workflow.add_node("generate_daily_plans", generate_daily_plans)
        workflow.add_node("save_plans", save_plans)
        
        # 添加边
        logger.debug("Adding edges to workflow...")
        workflow.set_entry_point("init_clients")
        workflow.add_edge("init_clients", "generate_initial_plan")
        workflow.add_edge("generate_initial_plan", "critique_plan")
        workflow.add_edge("critique_plan", "compare_plans")
        workflow.add_edge("compare_plans", "generate_final_plan")
        workflow.add_edge("generate_final_plan", "generate_daily_plans")
        workflow.add_edge("generate_daily_plans", "save_plans")
        workflow.add_edge("save_plans", END)
        
        logger.info("=== Workflow graph created successfully ===")
        return workflow
    except Exception as e:
        logger.error(f"Error creating workflow graph: {e}")
        logger.exception("Full error traceback:")
        raise


def run_workflow(user_background: str, user_goal: str, output_dir: str = None) -> Dict[str, Any]:
    """运行工作流
    
    Args:
        user_background: 用户的技术背景介绍
        user_goal: 用户的学习目标
        output_dir: 输出目录，默认使用配置文件中的值
        
    Returns:
        包含生成计划的字典
    """
    logger.info("=== Starting workflow execution ===")
    logger.debug(f"User background (first 100 chars): {user_background[:100]}...")
    logger.debug(f"User goal (first 100 chars): {user_goal[:100]}...")
    logger.debug(f"Output directory: {output_dir or settings.output_dir}")
    
    try:
        # 创建工作流
        workflow = create_workflow()
        logger.debug("Compiling workflow...")
        app = workflow.compile()
        
        # 构建原始问题
        logger.debug("Building original question...")
        original_question = f"{user_background}\n{user_goal}\n- 严格遵循SMART原则（Specific/Measurable/Achievable/Relevant/Time-bound）\n- 分双周设置里程碑目标\n- 每个阶段包含可量化的技能掌握指标和项目产出要求"
        logger.debug(f"Original question (first 200 chars): {original_question[:200]}...")
        
        # 运行工作流
        logger.info("=== Invoking workflow ===")
        result = app.invoke({
            "user_background": user_background,
            "user_goal": user_goal,
            "original_question": original_question,
            "output_dir": output_dir or settings.output_dir
        })
        
        logger.info("=== Workflow execution completed successfully ===")
        return result
    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        logger.exception("Full error traceback:")
        raise
