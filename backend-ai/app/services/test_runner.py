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
from typing import Dict, Any, Optional
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

        return {
            'all_passed': all_passed,
            'total': total,
            'passed': passed,
            'failed': failed,
            'success_rate': success_rate,
            'errors': errors,
        }


# 创建全局实例
test_runner = TestRunner()
