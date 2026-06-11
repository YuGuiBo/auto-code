import json
from typing import List, Dict, Any, Optional
import httpx
from openai import OpenAI
from app.core.config import settings


class AIService:
    """AI服务 - 支持DeepSeek和通义千问"""
    
    def __init__(self):
        # 创建不使用代理的 httpx 客户端，避免公司代理导致的连接问题
        http_client = httpx.Client(
            proxy=None,
            timeout=httpx.Timeout(300.0, connect=30.0)
        )
        self.client = OpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
            http_client=http_client
        )
        self.model = settings.AI_MODEL
    
    def _normalize_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        规范化测试案例数据格式，确保每个测试案例的字段符合前端期望的结构。
        处理AI可能返回的简化格式（如steps为字符串、preconditions为字符串等）。
        """
        import re
        normalized = []
        for tc in test_cases:
            if not isinstance(tc, dict):
                continue
            
            # 规范化 preconditions: 确保是数组
            preconditions = tc.get("preconditions", [])
            if isinstance(preconditions, str):
                # 尝试按句号、分号或换行拆分
                preconditions = [p.strip() for p in re.split(r'[;；。\n]', preconditions) if p.strip()]
            elif not isinstance(preconditions, list):
                preconditions = []
            
            # 规范化 postconditions: 确保是数组
            postconditions = tc.get("postconditions", [])
            if isinstance(postconditions, str):
                postconditions = [p.strip() for p in re.split(r'[;；。\n]', postconditions) if p.strip()]
            elif not isinstance(postconditions, list):
                postconditions = []
            
            # 规范化 steps: 确保是对象数组
            steps = tc.get("steps", [])
            if isinstance(steps, str):
                # 将字符串步骤解析为结构化步骤
                # 常见格式: "1. xxx 2. xxx" 或 "1、xxx 2、xxx"
                step_parts = re.split(r'\d+[.、．]\s*', steps)
                step_parts = [s.strip() for s in step_parts if s.strip()]
                steps = []
                for i, part in enumerate(step_parts, 1):
                    steps.append({
                        "step_no": i,
                        "actor": "系统/用户",
                        "action": part,
                        "fields": {},
                        "expected_result": ""
                    })
            elif isinstance(steps, list):
                # 检查列表中的每个元素是否是正确格式
                normalized_steps = []
                for i, step in enumerate(steps, 1):
                    if isinstance(step, str):
                        # 字符串步骤转为对象
                        normalized_steps.append({
                            "step_no": i,
                            "actor": "系统/用户",
                            "action": step,
                            "fields": {},
                            "expected_result": ""
                        })
                    elif isinstance(step, dict):
                        # 确保必要字段存在
                        normalized_steps.append({
                            "step_no": step.get("step_no", i),
                            "actor": step.get("actor", "系统/用户"),
                            "action": step.get("action", ""),
                            "fields": step.get("fields", {}),
                            "expected_result": step.get("expected_result", "")
                        })
                    else:
                        normalized_steps.append({
                            "step_no": i,
                            "actor": "系统/用户",
                            "action": str(step),
                            "fields": {},
                            "expected_result": ""
                        })
                steps = normalized_steps
            else:
                steps = []
            
            # 确保 expected_final_result 存在
            expected_final_result = tc.get("expected_final_result", "")
            if not expected_final_result:
                expected_final_result = tc.get("expected_result", "流程执行完成")
            
            normalized.append({
                "id": tc.get("id", f"TC{len(normalized)+1:03d}"),
                "name": tc.get("name", "未命名测试案例"),
                "category": tc.get("category", "normal"),
                "description": tc.get("description", ""),
                "preconditions": preconditions,
                "steps": steps,
                "postconditions": postconditions,
                "expected_final_result": expected_final_result
            })
        
        return normalized

    async def analyze_requirements(
        self, 
        user_message: str, 
        context: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        分析用户需求，生成5维分析矩阵
        
        Args:
            user_message: 用户输入的需求描述
            context: 对话上下文
            
        Returns:
            包含分析矩阵和AI回复的字典
        """
        system_prompt = """你是一个专业的业务流程分析师，擅长将自然语言需求转化为结构化的流程分析。

你的任务是通过对话引导用户，逐步完善以下5个维度的分析矩阵：

1. **参与者/角色 (actors)**: 谁会参与这个流程？有哪些角色？
2. **场景/活动 (scenarios)**: 这个流程包含哪些场景或活动？
3. **数据/信息 (data)**: 流程中需要哪些数据？从哪里来？
4. **规则/逻辑 (rules)**: 有什么业务规则？什么条件下做什么？
5. **异常场景 (exceptions)**: 可能出现哪些异常情况？如何处理？

**对话策略**：
- 首次对话：理解用户的基本需求，提取初步信息
- 后续对话：针对缺失或不清晰的维度提问
- 当5个维度都比较完整时，总结并询问是否可以进入下一阶段

**输出格式**：
你必须返回JSON格式，包含以下字段：
{
  "message": "你的回复消息",
  "analysis_matrix": {
    "actors": ["角色1", "角色2"],
    "scenarios": ["场景1", "场景2"],
    "data": ["数据1", "数据2"],
    "rules": ["规则1", "规则2"],
    "exceptions": ["异常1", "异常2"]
  },
  "completeness": 0.6,
  "next_questions": ["建议的下一个问题1", "建议的下一个问题2"],
  "stage": "analysis"
}

注意：
- 保持友好、专业的对话风格
- 每次只关注1-2个维度，不要一次问太多
- 根据用户的回答逐步完善矩阵
- 当completeness >= 0.8时，可以建议进入下一阶段
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加对话上下文
        if context:
            messages.extend(context)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            # 降级处理：返回基于用户输入的简单分析
            print(f"AI API调用失败: {str(e)}")
            print("使用降级模式返回模拟数据...")
            
            # 简单的关键词提取
            mock_analysis = self._generate_mock_analysis(user_message)
            
            return {
                "message": f"我理解了您的需求。让我为您分析一下这个流程的关键要素。\n\n"
                          f"根据您的描述，我识别出了以下关键信息：\n"
                          f"- 参与者：{', '.join(mock_analysis['actors']) if mock_analysis['actors'] else '待补充'}\n"
                          f"- 场景：{', '.join(mock_analysis['scenarios']) if mock_analysis['scenarios'] else '待补充'}\n"
                          f"- 数据：{', '.join(mock_analysis['data']) if mock_analysis['data'] else '待补充'}\n"
                          f"- 规则：{', '.join(mock_analysis['rules']) if mock_analysis['rules'] else '待补充'}\n"
                          f"- 异常：{', '.join(mock_analysis['exceptions']) if mock_analysis['exceptions'] else '待补充'}\n\n"
                          f"请问还有什么需要补充的吗？",
                "analysis_matrix": mock_analysis,
                "completeness": 0.3,
                "next_questions": [
                    "这个流程中还有其他参与者吗？",
                    "有什么特殊的业务规则需要注意？"
                ],
                "stage": "analysis"
            }
    
    def _generate_mock_analysis(self, user_message: str) -> Dict[str, List[str]]:
        """生成模拟分析数据（降级模式）"""
        analysis = {
            "actors": [],
            "scenarios": [],
            "data": [],
            "rules": [],
            "exceptions": []
        }
        
        # 简单的关键词匹配
        message_lower = user_message.lower()
        
        # 识别参与者
        actor_keywords = {
            "员工": "员工", "经理": "部门经理", "总经理": "总经理",
            "用户": "用户", "管理员": "管理员", "审批人": "审批人",
            "申请人": "申请人", "财务": "财务人员"
        }
        for keyword, actor in actor_keywords.items():
            if keyword in message_lower and actor not in analysis["actors"]:
                analysis["actors"].append(actor)
        
        # 识别场景
        if "请假" in message_lower or "休假" in message_lower:
            analysis["scenarios"].append("请假申请")
            analysis["data"].append("请假天数")
            analysis["data"].append("请假类型")
            analysis["data"].append("请假原因")
        if "审批" in message_lower:
            analysis["scenarios"].append("审批流程")
            analysis["rules"].append("需要审批人审核")
        if "报销" in message_lower:
            analysis["scenarios"].append("费用报销")
            analysis["data"].append("报销金额")
            analysis["data"].append("报销凭证")
        if "加班" in message_lower:
            analysis["scenarios"].append("加班申请")
            analysis["data"].append("加班时长")
        
        # 识别规则
        if "超过" in message_lower or "大于" in message_lower:
            # 提取数字
            import re
            numbers = re.findall(r'\d+', user_message)
            if numbers:
                analysis["rules"].append(f"超过{numbers[0]}天需要额外审批")
        
        if "天" in message_lower:
            analysis["data"].append("天数")
        if "金额" in message_lower or "元" in message_lower:
            analysis["data"].append("金额")
        
        # 识别异常情况
        if "拒绝" in message_lower or "驳回" in message_lower:
            analysis["exceptions"].append("审批被拒绝")
        if "撤回" in message_lower or "取消" in message_lower:
            analysis["exceptions"].append("申请被撤回")
        
        # 如果没有识别到任何内容，添加默认值
        if not analysis["actors"]:
            analysis["actors"] = ["申请人", "审批人"]
        if not analysis["scenarios"]:
            analysis["scenarios"] = ["提交申请", "审批处理"]
        
        return analysis
    
    async def generate_requirements(
        self, 
        analysis_matrix: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        根据分析矩阵生成结构化需求文档
        
        Args:
            analysis_matrix: 5维分析矩阵
            
        Returns:
            结构化需求文档
        """
        system_prompt = """你是一个需求工程师，根据分析矩阵生成结构化的需求文档。

输出格式（JSON）：
{
  "title": "需求标题",
  "overview": "需求概述",
  "functional_requirements": [
    {
      "id": "FR-001",
      "title": "功能需求标题",
      "description": "详细描述",
      "priority": "high/medium/low",
      "actors": ["相关角色"]
    }
  ],
  "non_functional_requirements": [
    {
      "id": "NFR-001",
      "category": "性能/安全/可用性等",
      "description": "描述",
      "criteria": "验收标准"
    }
  ],
  "business_rules": [
    {
      "id": "BR-001",
      "description": "业务规则描述",
      "condition": "触发条件",
      "action": "执行动作"
    }
  ],
  "data_requirements": [
    {
      "entity": "数据实体名称",
      "attributes": ["属性1", "属性2"],
      "source": "数据来源"
    }
  ]
}
"""
        
        user_message = f"请根据以下分析矩阵生成结构化需求文档：\n\n{json.dumps(analysis_matrix, ensure_ascii=False, indent=2)}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "title": "需求文档生成失败",
                "overview": f"错误：{str(e)}",
                "functional_requirements": [],
                "non_functional_requirements": [],
                "business_rules": [],
                "data_requirements": []
            }
    
    async def generate_user_cases(
        self, 
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        根据需求文档生成用户用例
        
        Args:
            requirements: 结构化需求文档
            
        Returns:
            用户用例列表
        """
        system_prompt = """你是一个用例设计专家，根据需求文档生成详细的用户用例。

输出格式（JSON数组）：
[
  {
    "id": "UC-001",
    "title": "用例标题",
    "actor": "主要参与者",
    "precondition": "前置条件",
    "main_flow": [
      "步骤1：用户执行某操作",
      "步骤2：系统响应",
      "步骤3：..."
    ],
    "alternative_flows": [
      {
        "condition": "替代条件",
        "steps": ["步骤1", "步骤2"]
      }
    ],
    "postcondition": "后置条件",
    "priority": "high/medium/low"
  }
]
"""
        
        user_message = f"请根据以下需求文档生成用户用例：\n\n{json.dumps(requirements, ensure_ascii=False, indent=2)}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            # 如果返回的是对象而不是数组，尝试提取数组
            if isinstance(result, dict) and "cases" in result:
                return result["cases"]
            elif isinstance(result, list):
                return result
            else:
                return []
            
        except Exception as e:
            return [{
                "id": "UC-ERROR",
                "title": "用例生成失败",
                "actor": "系统",
                "precondition": "",
                "main_flow": [f"错误：{str(e)}"],
                "alternative_flows": [],
                "postcondition": "",
                "priority": "low"
            }]
    def _build_process_variables_prompt(self, process_name: str, requirements: Dict[str, Any], test_cases: List[Dict[str, Any]]) -> str:
        """
        根据流程名称和需求文档动态生成流程变量定义段落。
        确保 BPMN 中条件表达式使用的变量名与后端实际传入的变量名一致。
        """
        # 1. 根据流程类型确定核心变量
        name_lower = process_name.lower()
        all_text = process_name
        
        # 从需求文档中提取更多上下文
        if requirements:
            for rule in requirements.get('business_rules', []):
                all_text += ' ' + rule.get('description', '') + ' ' + rule.get('condition', '')
            for data_req in requirements.get('data_requirements', []):
                all_text += ' ' + ' '.join(data_req.get('attributes', []))
        
        # 2. 定义各流程类型的变量配置
        variables_config = {
            'leave': {
                'description': '请假流程',
                'variables': [
                    ('leaveDays', '请假天数（整数，由员工填写）'),
                    ('remainingDays', '剩余假期天数（整数，由系统提供）'),
                    ('leaveType', '请假类型（字符串，如：年假、事假、病假）'),
                ],
                'condition_examples': [
                    ('短期请假只需项目经理审批', '${leaveDays &lt;= 2}'),
                    ('长期请假需要部门经理审批', '${leaveDays &gt; 2}'),
                    ('假期不足自动拒绝', '${remainingDays &lt; leaveDays}'),
                ]
            },
            'reimbursement': {
                'description': '报销流程',
                'variables': [
                    ('amount', '单次报销金额（数字，由员工填写）'),
                    ('monthlyTotal', '本月累计报销金额（数字，由系统计算）'),
                ],
                'condition_examples': [
                    ('小额报销只需项目经理审批', '${amount &lt;= 200}'),
                    ('大额报销需要部门经理审批', '${amount &gt; 200}'),
                    ('累计金额超限需要额外审批', '${amount &gt; 200 or monthlyTotal &gt;= 800}'),
                ]
            },
            'overtime': {
                'description': '加班流程',
                'variables': [
                    ('overtimeHours', '加班时长（小时，数字）'),
                ],
                'condition_examples': [
                    ('短时加班只需主管审批', '${overtimeHours &lt;= 4}'),
                    ('长时加班需要部门经理审批', '${overtimeHours &gt; 4}'),
                ]
            },
            'business-trip': {
                'description': '出差流程',
                'variables': [
                    ('tripDays', '出差天数（整数）'),
                    ('estimatedCost', '预估费用（数字）'),
                ],
                'condition_examples': [
                    ('短期出差只需主管审批', '${tripDays &lt;= 3}'),
                    ('长期出差需要部门经理审批', '${tripDays &gt; 3}'),
                ]
            },
        }
        
        # 3. 匹配流程类型
        matched_type = None
        type_keywords = {
            'leave': ['请假', '休假', 'leave'],
            'reimbursement': ['报销', '费用', '经费', 'reimbursement', 'expense'],
            'overtime': ['加班', 'overtime'],
            'business-trip': ['出差', '差旅', 'business', 'trip', 'travel'],
        }
        
        for ptype, keywords in type_keywords.items():
            if any(kw in all_text for kw in keywords):
                matched_type = ptype
                break
        
        # 4. 构建 prompt 段落
        lines = ['**流程变量定义**（必须在条件表达式中使用这些变量名，不要自创变量名）：']
        lines.append('- `${approved}`: 审批结果（布尔值，true表示批准，false表示拒绝。每个审批任务完成后由系统自动设置）')
        
        if matched_type and matched_type in variables_config:
            config = variables_config[matched_type]
            for var_name, var_desc in config['variables']:
                lines.append(f'- `${{{var_name}}}`: {var_desc}')
            
            lines.append('')
            lines.append(f'**{config["description"]}条件分支示例**（请根据实际需求文档中的规则调整阈值）：')
            for desc, expr in config['condition_examples']:
                lines.append(f'- {desc}：`{expr}`')
        else:
            # 通用变量：从需求中推断
            lines.append('- 请根据需求文档中的业务规则，使用英文驼峰命名法定义条件变量')
            lines.append('- 变量名必须与申请表单中的字段名一致（如 amount, days, count 等）')
            lines.append('')
            lines.append('**注意**：条件变量名必须使用英文驼峰命名（如 leaveDays, amount），因为这些变量名会直接用于 Flowable 引擎的条件表达式计算。')
        
        lines.append('')
        lines.append('**重要约束**：')
        lines.append('- `${approved}` 是固定的审批结果变量名，所有审批决策网关必须使用它')
        lines.append('- 条件路由网关（如按天数/金额判断走哪条分支）使用上述业务变量')
        lines.append('- 不要混淆这两种网关：审批决策网关（判断通过/拒绝）vs 条件路由网关（判断业务条件）')
        
        return '\n'.join(lines)

    async def generate_bpmn(
        self,
        process_name: str,
        test_cases: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> str:
        """
        根据测试案例和需求文档生成BPMN 2.0 XML
        
        Args:
            process_name: 流程名称
            test_cases: 测试案例列表
            requirements: 结构化需求文档
            
        Returns:
            BPMN 2.0 XML字符串
        """
        # 动态生成流程变量定义
        process_variables_section = self._build_process_variables_prompt(process_name, requirements, test_cases)
        
        system_prompt = """你是一个BPMN流程设计专家，根据测试案例和需求文档生成标准的BPMN 2.0 XML。

**BPMN 2.0 XML规范要点**：
1. 使用标准命名空间：xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
2. 包含必要元素：process, startEvent, endEvent, userTask, sequenceFlow, exclusiveGateway
3. 每个元素必须有唯一的id
4. sequenceFlow必须正确连接sourceRef和targetRef
5. **必须包含 BPMNDiagram 元素定义图形坐标** - 这是关键！

""" + process_variables_section + """

**条件表达式中的XML特殊字符转义（必须遵守！）**：
- 小于号 < 必须写成 `&lt;`
- 大于号 > 必须写成 `&gt;`
- 与号 & 必须写成 `&amp;`
- 正确示例：`${amount &lt;= 200}` 
- 错误示例：`${amount <= 200}`

**流程结构设计原则**：

1. **主干线性化**：流程主干按实际业务执行时序从左到右线性排列

2. **审批节点模式**：每个审批任务(userTask)后面紧跟一个exclusiveGateway，输出两条路径：
   - 通过（`${approved == true}`） → 继续主干流程
   - 拒绝（`${approved == false}`） → 连接到对应的终止结束事件

3. **条件路由模式**：使用exclusiveGateway作为路由器，分支条件需要根据业务规则设计。

   **单条件判断示例**（只有单次金额影响流程）：
   - 条件分支1：`${amount &lt;= 200}` → 项目经理审批
   - 条件分支2：`${amount &gt; 200}` → 部门经理审批

   **组合条件判断示例**（单次金额 + 累计金额共同影响流程）：
   当需求中存在"累计金额达到阈值后需要加强审批"等规则时，必须使用组合条件：
   - 条件分支1（仅需项目经理）：`${amount &lt;= 200 and monthlyTotal &lt; 800}`
   - 条件分支2（需要部门经理）：`${amount &gt; 200 or monthlyTotal &gt;= 800}`

4. **终止节点清晰**：
   - 成功路径最终汇合到一个"完成"结束事件
   - 每个拒绝/驳回路径有独立的结束事件，并标注是哪个节点拒绝的

5. **中文标签**：所有节点使用中文命名，清晰表达业务含义

**特别提醒 - 累计/历史状态规则的处理**：
如果需求文档中的业务规则包含以下关键词，你**必须**使用上述"组合条件判断"模式：
- "累计...达到..."
- "一旦...之后的所有..."
- "历史...超过..."
- "本月累计..."
- "总额达到..."

这类规则不能只用单次金额判断，必须引入 `${monthlyTotal}` 变量并在条件中组合判断。

**生成策略**：
- 分析需求文档中的 functional_requirements 和 business_rules，提取所有决策条件
- 从测试案例的 category=normal 案例确定主干流程
- 从测试案例的 category=branch 案例确定条件分支
- 从测试案例的 category=exception 案例确定异常/拒绝路径
- 确保所有测试案例描述的路径在流程图中都能走通
- **必须为每个元素定义图形坐标（BPMNShape 和 BPMNEdge）**

**输出格式**：
直接返回完整的BPMN 2.0 XML字符串，不要包含任何其他文本或解释。

**重要：必须包含完整的 BPMNDiagram 定义！示例结构**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
             xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
             xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
             targetNamespace="http://bpmn.io/schema/bpmn"
             id="Definitions_1">
  <process id="Process_1" name="流程名称" isExecutable="true">
    <startEvent id="StartEvent_1" name="开始"/>
    <userTask id="Task_1" name="任务1"/>
    <sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_1"/>
    <endEvent id="EndEvent_1" name="结束"/>
    <sequenceFlow id="Flow_2" sourceRef="Task_1" targetRef="EndEvent_1"/>
  </process>
  
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="Shape_StartEvent_1" bpmnElement="StartEvent_1">
        <dc:Bounds x="150" y="100" width="36" height="36"/>
        <bpmndi:BPMNLabel>
          <dc:Bounds x="156" y="143" width="24" height="14"/>
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Shape_Task_1" bpmnElement="Task_1">
        <dc:Bounds x="250" y="78" width="100" height="80"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Shape_EndEvent_1" bpmnElement="EndEvent_1">
        <dc:Bounds x="400" y="100" width="36" height="36"/>
        <bpmndi:BPMNLabel>
          <dc:Bounds x="406" y="143" width="24" height="14"/>
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Edge_Flow_1" bpmnElement="Flow_1">
        <di:waypoint x="186" y="118"/>
        <di:waypoint x="250" y="118"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_2" bpmnElement="Flow_2">
        <di:waypoint x="350" y="118"/>
        <di:waypoint x="400" y="118"/>
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</definitions>
```

**坐标布局规则（必须严格遵守，确保生成美观、无重叠、连线正确的BPMN图）**

========================================
一、元素尺寸（固定，单位：像素）
========================================
- StartEvent / EndEvent: width=36, height=36
- UserTask: width=100, height=80
- ExclusiveGateway: width=50, height=50 （必须加 isMarkerVisible="true"）

========================================
二、主干布局（水平主线，Y=200）
========================================
所有主干节点（开始、员工提交、主网关、主审批、决策网关、成功结束）的中心Y坐标均为200。

坐标计算公式：
- 第一个节点（StartEvent）: x=100, y=182 （中心Y=200）
- 后续节点 x = 前一个节点.x + 前一个节点.width + 80 （节点间水平间距80px）
- UserTask 的 y = 200 - 40 = 160
- Gateway 的 y = 200 - 25 = 175
- EndEvent 的 y = 200 - 18 = 182

示例主干序列：
Start(100) → [+36+80=216] → Task(216) → [+100+80=396] → Gateway(396) → [+50+80=526] → Task(526) → [+100+80=706] → Gateway(706) → [+50+80=836] → End(836)

========================================
三、分支布局规则（处理互斥路径）
========================================
当流程在网关后分为两条或多条互斥路径时（例如：一条路径只需项目经理审批，另一条需要部门经理审批），采用以下规则：

3.1 将其中一条路径作为**主干路径**（留在 Y=200 水平线）
3.2 将另一条路径作为**分支路径**，整体上移或下移，避免重叠
    - 推荐：分支路径放在主干**上方**，设置 Y=60（审批节点 y=60-40=20，网关 y=60-25=35，结束事件 y=60-18=42）
    - 分支路径的节点 x 坐标与主干路径中对应位置的节点 x 保持一致

3.3 分支路径的结束事件（成功或拒绝）必须与主干路径的结束事件**分开**，使用不同坐标

3.4 分支路径的连线规则：
    - 从网关出发到分支路径：使用垂直向上连线（从网关顶部中点 → 分支节点底部中点）
    - 分支路径节点之间：水平连线（节点右边缘 → 下一节点左边缘）
    - 分支路径完成后汇合到主干的成功结束事件：使用 Z 型连线（右边缘 → 向右偏移30px → 垂直向下至主干Y → 水平至成功结束事件左边缘）

========================================
四、结束事件（EndEvent）独立坐标规则
========================================
每个结束事件必须有**唯一且不重叠**的坐标，禁止共用。

4.1 主干成功结束事件：放在主干最右侧，Y=182
4.2 主干路径上的拒绝结束事件：放在其对应决策网关的正下方
    - x = 网关.x + 7 （使中心对齐）
    - y = 网关.y + 90
4.3 分支路径上的拒绝结束事件：放在分支路径决策网关的正下方
    - x = 分支网关.x + 7
    - y = 分支网关.y + 90
4.4 分支路径的成功结束事件：与主干成功结束事件**共用同一个节点**（id相同，坐标相同），表示流程最终完成

========================================
五、连线（BPMNEdge）详细坐标计算
========================================
所有连线使用直角折线（waypoint），不能使用斜线。

5.1 水平连线（主干路径节点之间）
    - 起点：前一个节点右边缘中点 (x+width, y+height/2)
    - 终点：下一个节点左边缘中点 (x, y+height/2)
    - 只需要两个 waypoint：起点 → 终点

5.2 垂直向下连线（主干拒绝分支）
    - 起点：决策网关底部中点 (网关.x+25, 网关.y+50)
    - 终点：拒绝结束事件顶部中点 (结束.x+18, 结束.y)
    - 需要两个 waypoint：起点 → 终点

5.3 垂直向上连线（从网关到上方分支路径的第一个节点）
    - 起点：网关顶部中点 (网关.x+25, 网关.y)
    - 终点：分支节点底部中点 (分支节点.x+width/2, 分支节点.y+height)
    - 两个 waypoint：起点 → 终点

5.4 分支路径内部的水平连线
    - 规则同 5.1

5.5 分支路径汇合到主干成功结束事件的 Z 型连线
    - 起点：分支路径最后一个节点（决策网关）的右边缘中点 (分支网关.x+50, 分支网关.y+25)
    - 第一转折点：向右偏移 30px (分支网关.x+80, 分支网关.y+25)
    - 第二转折点：垂直向下到主干成功结束事件的 Y 中心 (分支网关.x+80, 成功结束.y+18)
    - 终点：主干成功结束事件左边缘中点 (成功结束.x, 成功结束.y+18)
    - 需要四个 waypoint：起点 → 转折点1 → 转折点2 → 终点

========================================
六、节点 ID 与 BPMNLabel 规范
========================================
6.1 节点 ID 命名：
    - 开始：StartEvent_1
    - 用户任务：Task_{功能名}，如 Task_EmployeeSubmit, Task_PMApproval, Task_DMApproval
    - 网关：Gateway_{功能名}，如 Gateway_AmountCheck, Gateway_PMDecision, Gateway_DMDecision
    - 结束事件：EndEvent_Approved（成功）, EndEvent_RejectedByPM, EndEvent_RejectedByDM

6.2 BPMNLabel 位置（仅对 StartEvent, EndEvent, Gateway 需要）：
    - StartEvent 标签：x = 节点.x + 6, y = 节点.y + 43
    - EndEvent 标签：x = 节点.x + 6, y = 节点.y + 43
    - Gateway 标签：x = 节点.x, y = 节点.y + 55 （放在网关下方）

========================================
七、完整示例：经费申请流程（≤200且累计<800走PM，否则走DM）
========================================

节点布局（主干：项目经理路径，分支：部门经理路径）：

StartEvent_1          : x=100,  y=182
Task_EmployeeSubmit   : x=216,  y=160
Gateway_AmountCheck   : x=396,  y=175
Task_PMApproval       : x=526,  y=160   # 主干
Gateway_PMDecision    : x=656,  y=175
EndEvent_Approved     : x=786,  y=182   # 共用成功结束
EndEvent_RejectedByPM : x=663,  y=265   # PM拒绝在下方

# 分支路径（部门经理）放在上方 Y=60
Task_DMApproval       : x=526,  y=20    # 526 与 PMApproval 对齐
Gateway_DMDecision    : x=656,  y=35
EndEvent_RejectedByDM : x=663,  y=125   # DM拒绝在上方

连线 waypoint 示例：

Flow_4 (AmountCheck → DMApproval 向上):
起点(396+25=421, 175) → 终点(526+50=576, 20+80=100)  # 垂直向上
实际 waypoint: (421,175) → (421,100) → (576,100) → (576,20)?

纠正：应使用网关顶部中点 (421,175) 到 DMApproval 底部中点 (576,100)
waypoint: (421,175) → (421,100) → (576,100) → (576,100) 可简化为两个点 (421,175) → (576,100) 但为保证垂直+水平，建议：
(421,175) → (421,100) → (576,100)

Flow_8 (DMDecision → Approved 汇合):
起点 (656+50=706, 35+25=60) → 右移30 (736,60) → 下移到成功结束Y中心 (736,200) → 终点 (786,200)
waypoint: (706,60) → (736,60) → (736,200) → (786,200)

========================================
八、禁止事项
========================================
- 禁止两个不同结束事件使用相同坐标
- 禁止 userTask 被渲染为菱形（确保正确使用 userTask 元素，不要用 exclusiveGateway 代替）
- 禁止连线穿过无关节点
- 禁止分支路径的连线回到主干路径的错误节点（如部门经理审批后不应回到项目经理决策网关）
"""
        
        user_message = f"""请根据以下信息生成BPMN 2.0 XML：

**流程名称**：{process_name}

**测试案例**：
{json.dumps(test_cases, ensure_ascii=False, indent=2)}

**需求文档**：
{json.dumps(requirements, ensure_ascii=False, indent=2)}

请生成完整的BPMN 2.0 XML，确保：
1. 流程逻辑完整且符合测试案例描述
2. 所有元素ID唯一
3. 节点连接正确
4. 包含适当的网关处理分支逻辑
5. XML格式正确且可被BPMN引擎解析
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # 较低温度以获得更稳定的XML输出
            )
            
            bpmn_xml = response.choices[0].message.content.strip()
            
            # 清理可能的markdown代码块标记
            if bpmn_xml.startswith("```xml"):
                bpmn_xml = bpmn_xml[6:]
            if bpmn_xml.startswith("```"):
                bpmn_xml = bpmn_xml[3:]
            if bpmn_xml.endswith("```"):
                bpmn_xml = bpmn_xml[:-3]
            
            bpmn_xml = bpmn_xml.strip()
            
            # 验证是否为有效的XML开头
            if not bpmn_xml.startswith("<?xml") and not bpmn_xml.startswith("<definitions"):
                # 如果没有XML声明，添加一个
                bpmn_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + bpmn_xml
            
            return bpmn_xml
            
        except Exception as e:
            # 返回一个基本的错误BPMN模板
            error_bpmn = f"""<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             targetNamespace="http://bpmn.io/schema/bpmn"
             id="Definitions_Error">
  <process id="Process_Error" name="{process_name}" isExecutable="false">
    <startEvent id="StartEvent_1" name="开始"/>
    <userTask id="Task_Error" name="生成失败">
      <documentation>错误信息: {str(e)}</documentation>
    </userTask>
    <sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_Error"/>
    <endEvent id="EndEvent_1" name="结束"/>
    <sequenceFlow id="Flow_2" sourceRef="Task_Error" targetRef="EndEvent_1"/>
  </process>
</definitions>"""
            return error_bpmn



    async def generate_test_cases(
        self,
        requirements: Dict[str, Any],
        analysis_matrix: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        根据需求文档和分析矩阵生成测试案例
        
        Args:
            requirements: 结构化需求文档
            analysis_matrix: 分析矩阵
            
        Returns:
            测试案例数据（包含test_cases列表和metadata）
        """
        system_prompt = """你是一个测试案例设计专家，根据需求文档生成详细且完整的测试案例。

**生成策略（适用于任何业务流程）**：

第一步：从需求文档中提取所有业务规则(business_rules)，识别每条规则中的条件判断。
第二步：对每个条件判断，使用等价类划分+边界值分析，确定需要覆盖的测试数据。
第三步：对流程中的每个审批/决策节点，分别生成通过和拒绝的案例。
第四步：组合多条件场景，确保条件之间的交叉组合得到覆盖。

测试案例分为三大类：
1. **正常流程（normal）**: 每条独立的从起点到终点的成功路径
2. **条件分支（branch）**: 不同条件取值导致的不同流转路径（包含边界值）
3. **异常场景（exception）**: 每个决策节点的拒绝/退回/超时等情况

**覆盖完整性要求**：
- 每条业务规则涉及的条件，至少生成：满足条件、不满足条件、边界值 三种案例
- 流程中有N个审批节点，则异常场景至少覆盖每个节点的拒绝情况
- 如果存在累计/历史状态相关的规则，需要测试状态转换前后的不同表现
- 总案例数应能覆盖需求文档中所有规则的所有分支路径

输出格式（JSON）：
{
  "test_cases": [
    {
      "id": "TC001",
      "name": "测试案例名称",
      "category": "normal/branch/exception",
      "description": "详细描述这个测试案例要验证什么",
      "preconditions": ["前置条件1", "前置条件2"],
      "steps": [
        {
          "step_no": 1,
          "actor": "执行者角色",
          "action": "执行的操作",
          "fields": {
            "字段名1": "测试数据1",
            "字段名2": "测试数据2"
          },
          "expected_result": "这一步的预期结果"
        }
      ],
      "postconditions": ["后置条件1", "后置条件2"],
      "expected_final_result": "整个测试案例的预期最终结果"
    }
  ],
  "metadata": {
    "total_cases": 10,
    "normal_cases": 3,
    "branch_cases": 4,
    "exception_cases": 3,
    "generated_at": "2024-01-01T10:00:00Z"
  }
}

**重要**：
- 生成前先列举出所有需要覆盖的路径组合，确保无遗漏
- 每个测试案例的steps要详细，包含具体的测试数据
- expected_result要明确、可验证
- 宁多勿少，确保所有分支路径都有对应的测试案例
"""
        
        from datetime import datetime
        
        user_message = f"""请根据以下需求文档和分析矩阵生成详细的测试案例：

**需求文档**：
{json.dumps(requirements, ensure_ascii=False, indent=2)}

**分析矩阵**：
{json.dumps(analysis_matrix, ensure_ascii=False, indent=2)}

请生成完整的测试案例集合，确保覆盖所有重要的业务场景、条件分支和异常情况。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=8000
            )
            
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            print(f"AI返回的原始内容(完整): {content}")  # 打印完整内容用于调试
            print(f"finish_reason: {finish_reason}, 内容长度: {len(content)}")
            
            # 检查是否因为token限制被截断
            if finish_reason == "length":
                print("警告：AI输出被截断（达到max_tokens限制），可能导致JSON不完整")
            
            # 从返回内容中提取JSON（AI可能在JSON前后添加了说明文字）
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = content
            
            result = json.loads(json_str)
            
            # 检查result是否是字典类型
            if not isinstance(result, dict):
                print(f"警告：AI返回的不是字典对象，而是 {type(result)}，内容：{result}")
                raise ValueError(f"AI返回的JSON格式不正确，期望对象但得到 {type(result)}")
            
            # 确保test_cases字段存在
            if "test_cases" not in result:
                print(f"警告：返回的结果中没有test_cases字段，result keys: {result.keys()}")
                # 尝试修复：如果result本身是一个数组，包装它
                if isinstance(result, list):
                    result = {"test_cases": result}
                else:
                    raise ValueError("返回的结果中缺少test_cases字段")
            
            # 检测AI是否将test_case内部字段错误地提升到了顶层
            # 如果顶层有steps/postconditions/expected_final_result等字段，
            # 说明AI把一个test_case的内容拆散了
            top_level_steps = result.get("steps")
            top_level_postconditions = result.get("postconditions")
            top_level_expected = result.get("expected_final_result")
            
            test_cases = result.get("test_cases", [])
            
            # 如果顶层有这些字段，尝试将它们合并回test_cases中的对应元素
            if (top_level_steps or top_level_postconditions or top_level_expected) and test_cases:
                print(f"检测到顶层字段泄漏，尝试修复...")
                # 通常是最后一个test_case的字段被提升到了顶层
                last_tc = test_cases[-1] if isinstance(test_cases[-1], dict) else {}
                if top_level_steps and not last_tc.get("steps"):
                    last_tc["steps"] = top_level_steps
                if top_level_postconditions and not last_tc.get("postconditions"):
                    last_tc["postconditions"] = top_level_postconditions
                if top_level_expected and not last_tc.get("expected_final_result"):
                    last_tc["expected_final_result"] = top_level_expected
                test_cases[-1] = last_tc
            
            # 确保test_cases中的每个元素都是字典类型
            # 如果AI返回的test_cases元素是字符串（如JSON字符串），尝试解析
            parsed_test_cases = []
            for tc in test_cases:
                if isinstance(tc, dict):
                    parsed_test_cases.append(tc)
                elif isinstance(tc, str):
                    try:
                        parsed_tc = json.loads(tc)
                        if isinstance(parsed_tc, dict):
                            parsed_test_cases.append(parsed_tc)
                        else:
                            print(f"警告：test_case元素解析后不是字典: {type(parsed_tc)}")
                    except json.JSONDecodeError:
                        print(f"警告：test_case元素无法解析为JSON: {tc[:100]}")
                else:
                    print(f"警告：test_case元素类型异常: {type(tc)}")
            
            test_cases = parsed_test_cases
            
            # 规范化测试案例数据格式，确保前端能正确渲染
            test_cases = self._normalize_test_cases(test_cases)
            result["test_cases"] = test_cases
            
            result["metadata"] = {
                "total_cases": len(test_cases),
                "normal_cases": sum(1 for tc in test_cases if tc.get("category") == "normal"),
                "branch_cases": sum(1 for tc in test_cases if tc.get("category") == "branch"),
                "exception_cases": sum(1 for tc in test_cases if tc.get("category") == "exception"),
                "generated_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            print(f"生成测试案例失败: {str(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            # 返回一个基本的测试案例模板
            return {
                "test_cases": [
                    {
                        "id": "TC001",
                        "name": "基本流程测试",
                        "category": "normal",
                        "description": "测试标准业务流程",
                        "preconditions": ["系统可用", "用户已登录"],
                        "steps": [
                            {
                                "step_no": 1,
                                "actor": "用户",
                                "action": "提交申请",
                                "fields": {},
                                "expected_result": "申请提交成功"
                            }
                        ],
                        "postconditions": ["申请已保存"],
                        "expected_final_result": "流程正常完成"
                    }
                ],
                "metadata": {
                    "total_cases": 1,
                    "normal_cases": 1,
                    "branch_cases": 0,
                    "exception_cases": 0,
                    "generated_at": datetime.now().isoformat()
                }
            }
    
    async def process_test_case_feedback(
        self,
        current_test_cases: Dict[str, Any],
        feedback: str,
        requirements: Dict[str, Any],
        analysis_matrix: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        处理用户反馈，更新测试案例
        
        Args:
            current_test_cases: 当前的测试案例数据
            feedback: 用户反馈内容
            requirements: 结构化需求文档
            analysis_matrix: 分析矩阵
            
        Returns:
            更新后的测试案例数据
        """
        system_prompt = """你是一个测试案例设计专家，根据用户反馈更新测试案例。

用户可能会：
1. 指出缺失的测试场景
2. 指出测试案例中的错误
3. 要求添加新的测试条件
4. 要求修改某些测试步骤

你的任务是：
1. 分析用户反馈，理解问题所在
2. 根据反馈添加新的测试案例或修改现有测试案例
3. 保持原有正确的测试案例不变
4. 返回完整更新后的测试案例集合

**重要：你必须返回JSON格式的输出！**

输出格式（JSON）：
{
  "test_cases": [...],
  "metadata": {
    "total_cases": 数量,
    "normal_cases": 数量,
    "branch_cases": 数量,
    "exception_cases": 数量,
    "generated_at": "时间戳"
  }
}
"""
        
        from datetime import datetime
        
        user_message = f"""当前测试案例：
{json.dumps(current_test_cases, ensure_ascii=False, indent=2)}

用户反馈：
{feedback}

需求文档：
{json.dumps(requirements, ensure_ascii=False, indent=2)}

分析矩阵：
{json.dumps(analysis_matrix, ensure_ascii=False, indent=2)}

请分析用户反馈，更新测试案例。如果用户指出缺失场景，添加新的测试案例。如果指出错误，修正相应的测试案例。保持其他正确的测试案例不变。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # 规范化测试案例数据格式
            test_cases = result.get("test_cases", [])
            test_cases = self._normalize_test_cases(test_cases)
            result["test_cases"] = test_cases
            
            # 重新计算metadata
            result["metadata"] = {
                "total_cases": len(test_cases),
                "normal_cases": sum(1 for tc in test_cases if tc.get("category") == "normal"),
                "branch_cases": sum(1 for tc in test_cases if tc.get("category") == "branch"),
                "exception_cases": sum(1 for tc in test_cases if tc.get("category") == "exception"),
                "generated_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            print(f"处理反馈失败: {str(e)}")
            # 如果处理失败，返回原始测试案例
            return current_test_cases




# 创建全局AI服务实例
ai_service = AIService()

# Made with Bob
