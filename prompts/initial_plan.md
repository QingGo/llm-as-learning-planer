{user_background}
{user_goal}
- 严格遵循SMART原则（Specific/Measurable/Achievable/Relevant/Time-bound）
- 分双周设置里程碑目标
- 每个阶段包含可量化的技能掌握指标和项目产出要求

请严格按照JSON格式输出，包含以下字段：
- "title": 计划标题
- "overview": 计划概述
- "duration": 计划时长
- "milestones": 双周里程碑数组，每个里程碑包含：
  - "week_range": 双周范围（如"Week 1-2"）
  - "goal": 里程碑目标
  - "skills": 需掌握的技能列表
  - "projects": 项目产出要求
  - "resources": 推荐学习资源
- "final_goal": 最终目标描述