import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings


class AIService:
    """AI服务 - 支持DeepSeek和通义千问"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        self.model = settings.AI_MODEL
    
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
    async def generate_bpmn(
        self,
        process_name: str,
        user_cases: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> str:
        """
        根据用户用例和需求文档生成BPMN 2.0 XML
        
        Args:
            process_name: 流程名称
            user_cases: 用户用例列表
            requirements: 结构化需求文档
            
        Returns:
            BPMN 2.0 XML字符串
        """
        system_prompt = """你是一个BPMN流程设计专家，根据用户用例和需求文档生成标准的BPMN 2.0 XML。

**BPMN 2.0 XML规范要点**：
1. 使用标准命名空间：xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
2. 包含必要元素：process, startEvent, endEvent, userTask, sequenceFlow, exclusiveGateway
3. 每个元素必须有唯一的id
4. sequenceFlow必须正确连接sourceRef和targetRef
5. **必须包含 BPMNDiagram 元素定义图形坐标** - 这是关键！

**生成策略**：
- 为每个用户用例的主流程创建对应的任务节点
- 使用exclusiveGateway处理条件分支和异常流程
- 合理设置任务名称和文档说明
- 确保流程逻辑清晰、完整
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

**坐标布局规则**：
- StartEvent: 圆形，宽高36x36，起始位置(150, 180) - 注意Y坐标从180开始，为流程名称留出空间
- UserTask: 矩形，宽高100x80，水平间距150，垂直中心位置约200
- ExclusiveGateway: 菱形，宽高50x50
- EndEvent: 圆形，宽高36x36
- 流程从左到右水平布局，适当留白
- 分支流程适当向下偏移（Y坐标+120或更多），避免重叠
- 整体布局：为流程名称预留顶部80-100px的空间，所有元素Y坐标建议从150以上开始

**重要：XML 特殊字符转义规则**：
在 conditionExpression 中，必须正确转义 XML 特殊字符：
- 小于号 < 必须写成 &lt;
- 大于号 > 必须写成 &gt;
- 与号 & 必须写成 &amp;
- 示例：${amount &lt;= 200} 而不是 ${amount <= 200}
- 示例：${amount &gt; 200} 而不是 ${amount > 200}
"""
        
        user_message = f"""请根据以下信息生成BPMN 2.0 XML：

**流程名称**：{process_name}

**用户用例**：
{json.dumps(user_cases, ensure_ascii=False, indent=2)}

**需求文档**：
{json.dumps(requirements, ensure_ascii=False, indent=2)}

请生成完整的BPMN 2.0 XML，确保：
1. 流程逻辑完整且符合用例描述
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



# 创建全局AI服务实例
ai_service = AIService()

# Made with Bob
