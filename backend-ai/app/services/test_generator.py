"""
测试脚本生成服务
参照 ai_workflow_generator.py 的 _generate_test_script() 方法实现
使用 Jinja2 模板生成可执行的集成测试 Python 脚本
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader


class TestGenerator:
    """集成测试脚本生成器"""

    # 角色关键词映射表（中文 → 英文角色标识）
    # 注意：匹配时使用 _sorted_role_keys 按长度降序匹配，确保"项目经理"优先于"经理"
    ROLE_MAPPING = {
        '直接主管': 'supervisor', '直属主管': 'supervisor', '主管': 'supervisor',
        '项目经理': 'pm', 'PM': 'pm',
        '部门经理': 'director', '部门负责人': 'director',
        '经理': 'manager',
        'HR': 'hr', 'hr': 'hr', '人力资源': 'hr', '人事': 'hr',
        '财务': 'finance', '财务审批': 'finance',
        '总监': 'director', '副总': 'director',
        'CEO': 'ceo', '总经理': 'ceo', '总裁': 'ceo',
    }

    # 按关键词长度降序排列，确保最长匹配优先
    _sorted_role_keys = sorted(ROLE_MAPPING.keys(), key=len, reverse=True)

    def __init__(self):
        # 初始化 Jinja2 模板引擎
        template_dir = Path(__file__).parent.parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def generate_test_script(
        self,
        process_name: str,
        test_cases: List[Dict[str, Any]],
        bpmn_xml: str,
        requirements: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        根据测试案例生成集成测试脚本

        Args:
            process_name: 流程名称
            test_cases: 测试案例列表（后端格式）
            bpmn_xml: BPMN XML 字符串（用于提取流程信息）
            requirements: 结构化需求文档（可选，用于提取额外字段信息）

        Returns:
            生成的 Python 测试脚本代码
        """
        # 1. 提取流程元信息
        process_key = self._extract_process_key(bpmn_xml, 'process')
        process_type = self._extract_process_type(process_name, bpmn_xml, process_key, test_cases)
        # 生成类名：将 process_type 中的 - 和 _ 都作为分隔符
        class_name = ''.join(word.capitalize() for word in re.split(r'[-_]', process_type)) + 'FlowTester'
        api_prefix = f'/api/{process_type}'

        # 2. 提取表单字段
        form_fields = self._extract_form_fields(test_cases, requirements)

        # 3. 提取审批角色
        approval_roles = self._extract_approval_roles(test_cases, requirements)

        # 4. 转换测试案例为模板需要的格式
        template_test_cases = self._convert_test_cases(test_cases, approval_roles)

        # 4.1 补充流程必填字段的默认值（确保生成的脚本能通过后端验证）
        self._fill_required_fields(template_test_cases, process_type)

        # 5. 准备模板数据
        template_data = {
            'process_type': process_type,
            'process_name': process_name,
            'class_name': class_name,
            'api_prefix': api_prefix,
            'approval_roles': approval_roles,
            'test_cases': template_test_cases,
            'form_fields': form_fields,
        }

        # 6. 渲染模板
        template = self.jinja_env.get_template('test_script_template.py.j2')
        code = template.render(**template_data)

        # 7. 验证代码语法
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            print(f"⚠️ 测试脚本语法错误: {e} (行 {e.lineno})")

        return code

    def _extract_process_type(self, process_name: str, bpmn_xml: str = '', process_key: str = '', test_cases: List[Dict[str, Any]] = None) -> str:
        """
        从流程名称/BPMN XML/测试案例内容 提取流程类型标识
        
        优先级：
        1. 从流程名称的中文关键词匹配
        2. 从 BPMN XML 的 process name 属性匹配
        3. 从 BPMN XML 的 process id（process_key）推断
        4. 从测试案例的字段名/步骤内容推断
        5. 默认 'process'
        """
        # 常见流程类型映射（value 必须与后端配置的 apiPrefix 中的 flowType 一致）
        type_mapping = {
            '请假': 'leave', '休假': 'leave',
            '采购': 'purchase', '购买': 'purchase',
            '报销': 'reimbursement', '费用': 'reimbursement',
            '加班': 'overtime',
            '出差': 'business-trip', '差旅': 'business-trip',
            '经费': 'reimbursement',
        }
        
        # 1. 从流程名称匹配
        for keyword, ptype in type_mapping.items():
            if keyword in process_name:
                return ptype
        
        # 2. 从 BPMN XML 的 process name 属性匹配
        if bpmn_xml:
            name_match = re.search(r'<process\s+[^>]*name="([^"]+)"', bpmn_xml)
            if name_match:
                bpmn_process_name = name_match.group(1)
                for keyword, ptype in type_mapping.items():
                    if keyword in bpmn_process_name:
                        return ptype
        
        # 3. 从 process_key (process id) 推断
        if process_key:
            key_lower = process_key.lower()
            key_type_mapping = {
                'reimbursement': 'reimbursement',
                'expense': 'reimbursement',
                'leave': 'leave',
                'overtime': 'overtime',
                'business_trip': 'business-trip',
                'businesstrip': 'business-trip',
                'travel': 'business-trip',
                'purchase': 'purchase',
            }
            for key_fragment, ptype in key_type_mapping.items():
                if key_fragment in key_lower:
                    return ptype
        
        # 4. 从测试案例的字段名和步骤描述推断
        if test_cases:
            all_text = ''
            for tc in test_cases:
                all_text += tc.get('name', '') + ' '
                for step in tc.get('steps', []):
                    if isinstance(step, dict):
                        all_text += step.get('action', '') + ' '
                        for field_name in step.get('fields', {}).keys():
                            all_text += field_name + ' '
            for keyword, ptype in type_mapping.items():
                if keyword in all_text:
                    return ptype
        
        # 5. 默认使用 process
        return 'process'

    def _extract_process_key(self, bpmn_xml: str, default_type: str) -> str:
        """从 BPMN XML 中提取 process id"""
        match = re.search(r'<process\s+id="([^"]+)"', bpmn_xml)
        if match:
            return match.group(1)
        return f'{default_type}Process'

    def _extract_form_fields(
        self,
        test_cases: List[Dict[str, Any]],
        requirements: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """从测试案例和需求中提取表单字段定义"""
        fields_dict = {}  # name -> {name, label, type}

        # 从需求文档中提取字段定义
        if requirements:
            data_reqs = requirements.get('data_requirements', [])
            for data_req in data_reqs:
                for attr in data_req.get('attributes', []):
                    # 过滤无效字段名：至少2个字符，且不是纯标点
                    if attr and len(attr) >= 2 and attr not in fields_dict:
                        camel_name = self._to_camel_case(attr)
                        # 如果转换后仍是中文且未在映射中，跳过（避免无意义字段）
                        if camel_name == attr and not re.match(r'^[a-zA-Z]', camel_name):
                            # 未映射的中文字段名，仍然保留但标记
                            pass
                        fields_dict[attr] = {
                            'name': camel_name,
                            'label': attr,
                            'type': 'string'
                        }

        # 从测试案例的 steps.fields 中提取字段
        for tc in test_cases:
            steps = tc.get('steps', [])
            for step in steps:
                if isinstance(step, dict):
                    fields = step.get('fields', {})
                    for field_name, field_value in fields.items():
                        # 过滤无效字段名：至少2个字符
                        if not field_name or len(field_name) < 2:
                            continue
                        if field_name not in fields_dict:
                            field_type = self._infer_field_type(field_value)
                            fields_dict[field_name] = {
                                'name': self._to_camel_case(field_name),
                                'label': field_name,
                                'type': field_type
                            }

        # 确保有基本字段
        basic_fields = [
            {'name': 'applicantName', 'label': '申请人', 'type': 'string'},
            {'name': 'applicantId', 'label': '申请人ID', 'type': 'string'},
            {'name': 'department', 'label': '部门', 'type': 'string'},
        ]
        for bf in basic_fields:
            if bf['label'] not in fields_dict and bf['name'] not in [f['name'] for f in fields_dict.values()]:
                fields_dict[bf['label']] = bf

        return list(fields_dict.values())

    def _extract_approval_roles(
        self,
        test_cases: List[Dict[str, Any]],
        requirements: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """从测试案例和需求中提取审批角色列表（最长关键词优先匹配）"""
        roles = []

        def _extract_from_text(text: str):
            """从文本中提取角色，使用最长优先匹配，避免子串重复匹配"""
            remaining_text = text
            for keyword in self._sorted_role_keys:
                if keyword in remaining_text:
                    role = self.ROLE_MAPPING[keyword]
                    if role not in roles:
                        roles.append(role)
                    # 将已匹配的关键词从文本中移除，避免"项目经理"再匹配到"经理"
                    remaining_text = remaining_text.replace(keyword, '', 1)

        # 从需求的 business_rules 中提取
        if requirements:
            for rule in requirements.get('business_rules', []):
                action = rule.get('action', '')
                _extract_from_text(action)

            # 从 actors 中提取
            matrix = requirements.get('analysis_matrix', {})
            if isinstance(matrix, dict):
                for actor in matrix.get('actors', []):
                    _extract_from_text(actor)

        # 从测试案例的步骤中提取
        for tc in test_cases:
            steps = tc.get('steps', [])
            for step in steps:
                if isinstance(step, dict):
                    actor = step.get('actor', '')
                    action = step.get('action', '')
                    combined_text = f"{actor} {action}"
                    _extract_from_text(combined_text)

        # 如果没有提取到角色，默认添加 supervisor
        if not roles:
            roles = ['supervisor']

        return roles

    def _convert_test_cases(
        self,
        test_cases: List[Dict[str, Any]],
        approval_roles: List[str]
    ) -> List[Dict[str, Any]]:
        """
        将后端 test_cases 格式转换为 Jinja2 模板需要的格式

        后端格式（每个test_case）:
        {
            "id": "TC001",
            "name": "...",
            "steps": [
                {"step_no": 1, "actor": "员工", "action": "提交申请", "fields": {...}, "expected_result": "..."},
                {"step_no": 2, "actor": "项目经理", "action": "审批通过", "fields": {}, "expected_result": "..."}
            ]
        }

        模板需要的格式:
        {
            "id": "case_1",
            "name": "...",
            "description": "...",
            "form_data": {"字段1": "值1", ...},
            "approval_steps": [
                {"assignee": "supervisor", "approved": True, "comment": "...", "description": "..."}
            ]
        }
        """
        converted = []

        for idx, tc in enumerate(test_cases):
            tc_id = tc.get('id', f'TC{idx+1:03d}')
            # 将 id 转为合法的 Python 标识符
            safe_id = re.sub(r'[^a-zA-Z0-9_]', '_', tc_id).lower()
            if safe_id[0].isdigit():
                safe_id = f'case_{safe_id}'

            tc_name = tc.get('name', f'测试用例{idx+1}')
            tc_desc = tc.get('description', tc_name)
            steps = tc.get('steps', [])

            # 提取表单数据（从第一个有 fields 的步骤，通常是"提交申请"步骤）
            form_data = {}
            approval_steps = []

            for step in steps:
                if not isinstance(step, dict):
                    continue

                actor = step.get('actor', '')
                action = step.get('action', '')
                fields = step.get('fields', {})
                expected_result = step.get('expected_result', '')

                # 判断是提交步骤还是审批步骤
                if self._is_submit_step(action, actor):
                    # 提交步骤 - 提取表单数据（排除审批环节字段）
                    if fields:
                        for k, v in fields.items():
                            if k not in self.EXCLUDED_FORM_FIELDS:
                                form_data[k] = v
                elif self._is_approval_step(action, actor):
                    # 审批步骤 - 提取审批信息
                    assignee = self._match_role(actor, action, approval_roles)
                    is_approved = not any(kw in action for kw in ['拒绝', '驳回', '不通过', '不批准', '退回'])
                    comment = self._extract_comment(action, expected_result, is_approved)

                    approval_steps.append({
                        'assignee': assignee,
                        'approved': is_approved,
                        'comment': comment,
                        'description': f"{actor}{action}" if actor else action
                    })

            # 如果没有提取到表单数据，生成默认数据
            if not form_data:
                form_data = {
                    'applicantName': '测试用户',
                    'applicantId': 'test_user_001',
                    'department': '技术部',
                }

            # 如果没有提取到审批步骤，从角色列表自动生成
            if not approval_steps:
                # 根据测试案例的 category 决定是通过还是拒绝
                category = tc.get('category', 'normal')
                if category == 'exception':
                    # 异常场景：第一个审批角色拒绝
                    if approval_roles:
                        approval_steps.append({
                            'assignee': approval_roles[0],
                            'approved': False,
                            'comment': '审批拒绝',
                            'description': f'{approval_roles[0]}审批拒绝'
                        })
                else:
                    # 正常/分支场景：所有审批角色通过
                    for role in approval_roles:
                        approval_steps.append({
                            'assignee': role,
                            'approved': True,
                            'comment': '审批通过',
                            'description': f'{role}审批通过'
                        })

            converted.append({
                'id': safe_id,
                'name': tc_name,
                'description': tc_desc,
                'form_data': form_data,
                'approval_steps': approval_steps,
            })

        return converted

    # 不应出现在申请表单中的字段（审批环节字段，不是申请人填写的）
    EXCLUDED_FORM_FIELDS = {
        '审批状态', '批复人', '审批人', '审批结果', '审批意见',
        '批准', '拒绝', '通过', '不通过',
        'approvalStatus', 'approver', 'approvalResult',
    }

    def _is_submit_step(self, action: str, actor: str) -> bool:
        """判断是否为提交申请步骤"""
        submit_keywords = ['提交', '发起', '申请', '填写', '录入']
        return any(kw in action for kw in submit_keywords)

    def _is_approval_step(self, action: str, actor: str) -> bool:
        """判断是否为审批步骤"""
        approval_keywords = ['审批', '批准', '审核', '确认', '签批', '拒绝', '驳回']
        return any(kw in action for kw in approval_keywords)

    def _match_role(self, actor: str, action: str, available_roles: List[str]) -> str:
        """将角色描述匹配到可用的英文角色标识（最长关键词优先匹配）"""
        combined = f"{actor} {action}"
        # 按长度降序匹配，确保"项目经理"优先于"经理"
        for keyword in self._sorted_role_keys:
            if keyword in combined:
                role = self.ROLE_MAPPING[keyword]
                if role in available_roles:
                    return role
        # 如果没有精确匹配到 available_roles 中的，再次尝试不限定 available_roles
        for keyword in self._sorted_role_keys:
            if keyword in combined:
                return self.ROLE_MAPPING[keyword]
        # 默认返回第一个可用角色
        return available_roles[0] if available_roles else 'supervisor'

    def _extract_comment(self, action: str, expected_result: str, is_approved: bool) -> str:
        """提取审批评论"""
        if not is_approved:
            # 尝试从 action 中提取拒绝原因
            reason_match = re.search(r'[，,](.+)', action)
            if reason_match:
                return reason_match.group(1).strip()
            return '审批不通过'
        return '同意' if is_approved else '不同意'

    def _infer_field_type(self, value: Any) -> str:
        """推断字段类型"""
        if isinstance(value, bool):
            return 'boolean'
        if isinstance(value, (int, float)):
            return 'number'
        if isinstance(value, str):
            if re.match(r'\d{4}-\d{2}-\d{2}', value):
                return 'date'
            try:
                float(value)
                return 'number'
            except (ValueError, TypeError):
                pass
        return 'string'

    def _fill_required_fields(self, test_cases: List[Dict[str, Any]], process_type: str) -> None:
        """
        根据流程类型，自动补充每个测试案例 form_data 中缺失的必填字段默认值。
        这确保生成的测试脚本在调用后端 /apply 时不会因缺少必填字段而失败。
        """
        # 各流程类型的必填字段及默认测试值
        PROCESS_REQUIRED_FIELDS = {
            'reimbursement': {
                'reimbursementType': '差旅费',
                'amount': 150,
                'reason': '测试报销',
                'description': '自动化测试报销申请',
                'applicantName': '测试用户',
                'applicantId': 'test_user_001',
                'department': '技术部',
            },
            'leave': {
                'leaveType': '年假',
                'leaveDays': 3,
                'reason': '个人事务',
                'startDate': '2026-06-01',
                'endDate': '2026-06-03',
                'applicantName': '测试用户',
                'applicantId': 'test_user_001',
                'department': '技术部',
            },
            'overtime': {
                'overtimeDate': '2026-06-01',
                'overtimeHours': 3,
                'reason': '项目紧急',
                'applicantName': '测试用户',
                'applicantId': 'test_user_001',
                'department': '技术部',
            },
            'business-trip': {
                'destination': '上海',
                'tripDays': 3,
                'startDate': '2026-06-01',
                'endDate': '2026-06-03',
                'reason': '客户拜访',
                'estimatedCost': 5000,
                'applicantName': '测试用户',
                'applicantId': 'test_user_001',
                'department': '技术部',
            },
        }

        defaults = PROCESS_REQUIRED_FIELDS.get(process_type, {})
        if not defaults:
            return

        for tc in test_cases:
            form_data = tc.get('form_data', {})
            # 将 form_data 中的中文键转为英文键（用于比对）
            existing_english_keys = set()
            for key in form_data.keys():
                english_key = self._to_camel_case(key) if not re.match(r'^[a-zA-Z]', key) else key
                existing_english_keys.add(english_key)

            # 补充缺失的必填字段
            for field_name, default_value in defaults.items():
                if field_name not in existing_english_keys and field_name not in form_data:
                    form_data[field_name] = default_value

            tc['form_data'] = form_data

    def _to_camel_case(self, chinese_name: str) -> str:
        """将中文字段名转为驼峰英文（简单映射）"""
        mapping = {
            '申请人': 'applicantName', '申请人ID': 'applicantId',
            '部门': 'department',
            '金额': 'amount', '总金额': 'totalAmount',
            '单次金额': 'amount', '单次报销金额': 'amount',
            '报销金额': 'amount', '经费金额': 'amount',
            '月累计金额': 'monthlyTotal', '累计金额': 'monthlyTotal',
            '本月累计': 'monthlyTotal', '单月总金额': 'monthlyTotal',
            '单月总报销金额': 'monthlyTotal', '月总报销金额': 'monthlyTotal',
            '单月累计报销金额': 'monthlyTotal', '累计报销金额': 'monthlyTotal',
            '天数': 'days', '请假天数': 'leaveDays', '请假类型': 'leaveType',
            '原因': 'reason', '请假原因': 'reason', '报销原因': 'reason',
            '申请原因': 'reason', '事由': 'reason',
            '开始日期': 'startDate', '结束日期': 'endDate',
            '申请日期': 'applyDate', '日期': 'applyDate',
            '标题': 'title', '描述': 'description',
            '采购物品': 'items', '单价': 'unitPrice', '数量': 'quantity',
            '报销类型': 'reimbursementType', '费用类型': 'reimbursementType',
            '报销凭证': 'receipt', '凭证': 'receipt',
            '批复人': 'approver', '审批人': 'approver',
            '审批状态': 'approvalStatus', '状态': 'status',
            '加班时长': 'overtimeHours', '加班日期': 'overtimeDate',
            '出差目的地': 'destination', '目的地': 'destination',
            '出差天数': 'tripDays', '预估费用': 'estimatedCost',
        }
        return mapping.get(chinese_name, chinese_name)


# 创建全局实例
test_generator = TestGenerator()
