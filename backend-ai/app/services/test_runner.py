"""
测试脚本运行服务
参照 auto_tester.py 的实现
运行生成的集成测试脚本并收集测试结果
"""

import os
import re
import sys
import subprocess
import tempfile
from typing import Dict, Any, Optional, List
from pathlib import Path


class TestRunner:
    """测试脚本运行器"""

    def __init__(self, flowable_base_url: str = "http://localhost:8080", timeout: int = 120):
        """
        初始化测试运行器

        Args:
            flowable_base_url: Flowable 服务地址
            timeout: 脚本执行超时时间（秒）
        """
        self.flowable_base_url = flowable_base_url
        self.timeout = timeout

    def run_test_script(self, script_content: str, verbose: bool = False) -> Dict[str, Any]:
        """
        运行测试脚本并返回结果

        Args:
            script_content: Python 测试脚本代码
            verbose: 是否启用详细输出

        Returns:
            dict: {
                'success': bool,          # 脚本是否执行成功（exit code == 0）
                'all_passed': bool,       # 所有测试用例是否全部通过
                'total': int,             # 总测试数
                'passed': int,            # 通过数
                'failed': int,            # 失败数
                'success_rate': float,    # 成功率（百分比）
                'errors': list,           # 错误列表
                'output': str,            # 完整输出
                'stderr': str,            # 错误输出
                'exit_code': int,         # 退出码
                'test_script': str,       # 测试脚本内容
            }
        """
        # 创建临时文件保存测试脚本
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                prefix='test_bpmn_integration_',
                delete=False,
                encoding='utf-8'
            )
            temp_file.write(script_content)
            temp_file.close()
            script_path = temp_file.name

            # 构建命令
            cmd = [
                sys.executable,
                script_path,
                "--url", self.flowable_base_url,
            ]
            if verbose:
                cmd.append("--verbose")

            # 设置环境变量
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['NO_COLOR'] = '1'  # 禁用 ANSI 颜色，便于解析输出

            # 执行脚本
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=self.timeout,
                env=env,
            )

            stdout = result.stdout
            stderr = result.stderr
            exit_code = result.returncode

            # 解析测试输出
            test_result = self._parse_test_output(stdout + stderr)
            test_result['success'] = (exit_code == 0)
            test_result['output'] = stdout
            test_result['stderr'] = stderr
            test_result['exit_code'] = exit_code
            test_result['test_script'] = script_content

            return test_result

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'all_passed': False,
                'total': 0,
                'passed': 0,
                'failed': 1,
                'success_rate': 0.0,
                'errors': [{'type': 'timeout', 'message': f'测试脚本执行超时({self.timeout}秒)'}],
                'output': '',
                'stderr': f'执行超时（{self.timeout}秒）',
                'exit_code': -1,
                'test_script': script_content,
            }
        except Exception as e:
            return {
                'success': False,
                'all_passed': False,
                'total': 0,
                'passed': 0,
                'failed': 1,
                'success_rate': 0.0,
                'errors': [{'type': 'exception', 'message': str(e)}],
                'output': '',
                'stderr': str(e),
                'exit_code': -1,
                'test_script': script_content,
            }
        finally:
            # 清理临时文件
            if temp_file:
                try:
                    os.unlink(temp_file.name)
                except OSError:
                    pass

    def _parse_test_output(self, output: str) -> Dict[str, Any]:
        """
        解析测试脚本输出，提取通过/失败统计

        Args:
            output: 脚本的完整输出

        Returns:
            解析后的测试结果
        """
        total = 0
        passed = 0
        failed = 0
        errors = []

        # 匹配 "总测试数: X"
        total_match = re.search(r'总测试数[:：]\s*(\d+)', output)
        if total_match:
            total = int(total_match.group(1))

        # 匹配 "通过: X"
        passed_match = re.search(r'通过[:：]\s*(\d+)', output)
        if passed_match:
            passed = int(passed_match.group(1))

        # 匹配 "失败: X"
        failed_match = re.search(r'失败[:：]\s*(\d+)', output)
        if failed_match:
            failed = int(failed_match.group(1))

        # 如果没有找到标准摘要，用其他方式计算
        if total == 0:
            # "★ 流程完成" 表示一个测试用例完整通过
            passed = len(re.findall(r'★\s*流程完成', output))
            # "✗ 失败:" 表示一个测试用例失败
            failed = len(re.findall(r'✗\s*失败', output))
            # 加上健康检查
            if '健康检查: PASS' in output:
                passed += 1
            elif '健康检查: FAIL' in output:
                failed += 1
            total = passed + failed

        # 提取具体的失败信息
        # 格式：✗ 失败: 测试名称 - 错误原因
        fail_pattern = r'✗\s*失败[:：]\s*(.+?)\s*-\s*(.+?)(?=\n|$)'
        for match in re.finditer(fail_pattern, output):
            errors.append({
                'test_name': match.group(1).strip(),
                'message': match.group(2).strip()
            })

        # 也提取 "失败的测试:" 后面的列表
        failed_section = re.search(r'失败的测试[:：]\s*\n((?:\s*-\s*.+\n?)+)', output)
        if failed_section:
            for line in failed_section.group(1).strip().split('\n'):
                line = line.strip().lstrip('- ')
                if ':' in line:
                    parts = line.split(':', 1)
                    errors.append({
                        'test_name': parts[0].strip(),
                        'message': parts[1].strip()
                    })

        success_rate = (passed / total * 100) if total > 0 else 0.0
        all_passed = (failed == 0 and total > 0)

        # 提取每个测试用例的详细流程步骤
        case_details = self._parse_case_details(output)

        return {
            'all_passed': all_passed,
            'total': total,
            'passed': passed,
            'failed': failed,
            'success_rate': success_rate,
            'errors': errors,
            'case_details': case_details,
        }

    def _parse_case_details(self, output: str) -> List[Dict[str, Any]]:
        """
        从测试输出中解析每个测试用例的详细执行步骤。

        实际输出格式示例：
            [i] [09:31:08]   步骤1: 提交申请 - 单次报销金额=150, ...
            [√] [09:31:08]   ✓ 申请提交成功: 38f9c126-...
            [i] [09:31:09]   步骤2: pm审批通过 (pm)...
            [√] [09:31:10]   ✓ pm审批通过: 通过 - "审批通过"
            [i] [09:31:11]   步骤3: director审批拒绝 (director)...
            [√] [09:31:11]   ✓ director审批拒绝: 拒绝 - "审批不通过"
            [√] [09:31:12]   ★ 流程完成! 部门经理拒绝... (3.40s) - 38f9c126-...

        以 "★ 流程完成" 或 "✗ 测试失败" 行作为每个用例的结束标记。

        Returns:
            list: 每个用例的详细信息
        """
        case_details = []
        
        # 先把输出按行分割，剥离日志前缀
        lines = output.split('\n')
        clean_lines = []
        for line in lines:
            # 剥离前缀：[√] [09:31:08]  或  [i] [09:31:08]  或  [✗] [09:31:08]
            stripped = re.sub(r'^\s*\[[^\]]*\]\s*\[[^\]]*\]\s*', '', line)
            clean_lines.append(stripped.strip())
        
        # 用 "★ 流程完成" 行来标识一个用例的结束，从中提取用例名
        # 也处理 "✗ 测试失败" 作为失败用例的结束
        current_steps = []
        
        for clean_line in clean_lines:
            if not clean_line:
                continue
            
            # 检查是否是流程完成行: "★ 流程完成! 用例名称 (Xs) - processId"
            complete_match = re.match(r'★\s*流程完成[!！]?\s*(.+?)(?:\s*\(\d+\.\d+s\)|\s*-\s*[a-f0-9-]+)', clean_line)
            if complete_match:
                case_name = complete_match.group(1).strip()
                # 添加流程完成步骤
                current_steps.append({
                    'step': '流程完成',
                    'status': 'completed',
                    'detail': case_name
                })
                case_details.append({
                    'case_name': case_name,
                    'status': 'passed',
                    'steps': current_steps,
                })
                current_steps = []
                continue
            
            # 检查是否是测试失败行: "✗ 测试失败: 用例名称 - 原因"
            fail_case_match = re.match(r'[✗✘×]\s*测试失败[:：]?\s*(.+?)(?:\s*-\s*(.+))?$', clean_line)
            if fail_case_match:
                case_name = fail_case_match.group(1).strip()
                detail = fail_case_match.group(2).strip() if fail_case_match.group(2) else ''
                current_steps.append({
                    'step': '测试失败',
                    'status': 'failed',
                    'detail': detail
                })
                case_details.append({
                    'case_name': case_name,
                    'status': 'failed',
                    'steps': current_steps,
                })
                current_steps = []
                continue
            
            # 步骤行: "步骤N: 描述 ..."
            step_match = re.match(r'步骤\d+[:：]\s*(.+)', clean_line)
            if step_match:
                step_desc = step_match.group(1).strip()
                # 清理尾部的 (角色)... 
                step_desc = re.sub(r'\s*\([^)]*\)\.\.\.\s*$', '', step_desc)
                # 清理尾部的 - 字段=值, 字段=值 部分，保留动作描述
                action_part = step_desc.split(' - ')[0].strip() if ' - ' in step_desc else step_desc
                current_steps.append({
                    'step': action_part,
                    'status': 'passed',
                    'detail': step_desc if step_desc != action_part else ''
                })
                continue
            
            # 成功步骤: "✓ 描述"
            success_match = re.match(r'[✓✔√]\s*(.+)', clean_line)
            if success_match:
                step_desc = success_match.group(1).strip()
                # 如果上一步是"步骤N"，更新其detail而不是新增
                if current_steps and current_steps[-1]['detail'] == '':
                    current_steps[-1]['detail'] = step_desc
                else:
                    current_steps.append({
                        'step': step_desc,
                        'status': 'passed',
                        'detail': ''
                    })
                continue
            
            # 失败步骤: "✗ 描述 - 原因"
            fail_match = re.match(r'[✗✘×]\s*(.+?)(?:\s*-\s*(.+))?$', clean_line)
            if fail_match:
                step_desc = fail_match.group(1).strip()
                detail = fail_match.group(2).strip() if fail_match.group(2) else ''
                current_steps.append({
                    'step': step_desc,
                    'status': 'failed',
                    'detail': detail
                })
                continue
        
        # 如果还有未关闭的步骤（没有 ★ 结尾），也要收集
        if current_steps:
            case_details.append({
                'case_name': '未完成的测试',
                'status': 'failed',
                'steps': current_steps,
            })
        
        return case_details


# 创建全局实例
test_runner = TestRunner()
