{user_background}
目前我已经有一份双周粒度的，符合 SMART 原则的学习计划，如下：

{biweekly_plan}

按 SMART 原则，为我细化 {week_range} 的每日学习计划。

# Requirements
1. **严格遵循SMART原则**：每个每日任务都要具体、可衡量、可实现、相关、有时限
2. **每日学习时间**：每天8小时，每周50小时
3. **任务分解**：将双周计划中的任务分解为具体的每日任务
4. **技能递进**：确保每日任务之间有逻辑递进关系
5. **包含休息时间**：合理安排休息时间，避免过度疲劳
6. **可执行性**：确保计划切实可行，不会过于理想化
7. **反馈机制**：包含每日学习效果的检查和反馈机制

# Output Format
请严格按照JSON格式输出，**注意：只输出纯JSON内容，不要包含任何markdown格式（如```json ... ```），确保输出是可直接解析的JSON**。包含以下字段：
- "week_range": 双周范围（如"Week 1-2"）
- "total_hours": 总学习时长
- "daily_schedule": 每日计划数组，每个计划包含：
  - "day": 第几天（如"Day 1"）
  - "date": 日期范围（如"Week 1, Day 1"）
  - "tasks": 当日任务列表，每个任务包含：
    - "title": 任务标题
    - "description": 任务描述
    - "duration_hours": 预计时长（小时）
    - "skills": 涉及的技能
    - "expected_outcome": 预期成果
  - "total_hours": 当日总时长
  - "rest_time": 休息时间安排
  - "learning_tips": 学习建议
- "week_summary": 双周学习总结和回顾建议