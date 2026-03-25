#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
员工请假流程自动化测试脚本
包含6个完整测试场景

测试场景：
1. 短期请假 - 审批通过
2. 短期请假 - 审批拒绝
3. 长期请假 - 多级审批通过
4. 长期请假 - 经理初审拒绝
5. 长期请假 - 部门经理拒绝
6. 假期不足 - 自动拒绝
"""

import requests
import json
import time
import argparse
from typing import Dict, Optional, List
from enum import Enum


class Color:
    """终端颜色代码"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class Status(Enum):
    """流程状态枚举"""
    SUBMITTED = "SUBMITTED"
    INSUFFICIENT_LEAVE = "INSUFFICIENT_LEAVE"
    PENDING_MANAGER_APPROVAL = "PENDING_MANAGER_APPROVAL"
    PENDING_DEPT_MANAGER_APPROVAL = "PENDING_DEPT_MANAGER_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TestResult:
    """测试结果类"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_pass(self):
        self.total += 1
        self.passed += 1

    def add_fail(self, error_msg: str):
        self.total += 1
        self.failed += 1
        self.errors.append(error_msg)

    def print_summary(self):
        print(f"\n{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}测试结果汇总{Color.RESET}")
        print(f"{'='*60}")
        print(f"总测试数: {self.total}")
        print(f"{Color.GREEN}通过: {self.passed}{Color.RESET}")
        print(f"{Color.RED}失败: {self.failed}{Color.RESET}")
        
        if self.errors:
            print(f"\n{Color.RED}失败详情:{Color.RESET}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        print(f"{'='*60}\n")


class FlowableTestClient:
    """Flowable API测试客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.result = TestResult()

    def log_step(self, step: str, description: str = ""):
        """打印测试步骤"""
        print(f"\n{Color.CYAN}{Color.BOLD}[步骤] {step}{Color.RESET}")
        if description:
            print(f"  {description}")

    def log_success(self, message: str):
        """打印成功信息"""
        print(f"{Color.GREEN}✓ {message}{Color.RESET}")

    def log_error(self, message: str):
        """打印错误信息"""
        print(f"{Color.RED}✗ {message}{Color.RESET}")

    def log_info(self, message: str):
        """打印信息"""
        print(f"{Color.YELLOW}ℹ {message}{Color.RESET}")

    def apply_leave(self, applicant_name: str, leave_days: int, 
                   remaining_days: int, reason: str) -> Optional[str]:
        """申请请假"""
        url = f"{self.base_url}/api/leave/apply"
        data = {
            "applicantName": applicant_name,
            "leaveDays": leave_days,
            "remainingDays": remaining_days,
            "reason": reason
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                process_id = result.get("processInstanceId")
                self.log_success(f"请假申请已提交")
                self.log_info(f"流程实例ID: {process_id}")
                self.log_info(f"申请人: {applicant_name}, 请假天数: {leave_days}")
                return process_id
            else:
                self.log_error(f"申请失败: {result.get('message')}")
                return None
        except Exception as e:
            self.log_error(f"API调用失败: {str(e)}")
            return None

    def get_process_instance(self, process_id: str) -> Optional[Dict]:
        """查询流程实例"""
        url = f"{self.base_url}/api/leave/process/instance/{process_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            result = response.json()
            
            status = result.get("status")
            status_name = result.get("statusDisplayName")
            ended = result.get("ended")
            
            self.log_info(f"当前状态: {status_name} ({status})")
            self.log_info(f"是否结束: {'是' if ended else '否'}")
            
            return result
        except Exception as e:
            self.log_error(f"查询流程实例失败: {str(e)}")
            return None

    def get_task_list(self) -> List[Dict]:
        """查询所有待办任务"""
        url = f"{self.base_url}/api/leave/task/list"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            tasks = response.json()
            
            if tasks:
                self.log_info(f"找到 {len(tasks)} 个待办任务")
                for task in tasks:
                    self.log_info(f"  - 任务ID: {task['id']}, 名称: {task['name']}")
            else:
                self.log_info("没有待办任务")
            
            return tasks
        except Exception as e:
            self.log_error(f"查询任务列表失败: {str(e)}")
            return []

    def approve_by_manager(self, task_id: str, approved: bool, 
                          comment: str = "approved") -> bool:
        """经理审批"""
        url = f"{self.base_url}/api/leave/manager/approve/{task_id}"
        params = {
            "approved": str(approved).lower(),
            "comment": comment
        }
        
        try:
            response = self.session.post(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                action = "批准" if approved else "拒绝"
                self.log_success(f"经理审批完成: {action}")
                return True
            else:
                self.log_error(f"审批失败: {result.get('message')}")
                return False
        except Exception as e:
            self.log_error(f"审批API调用失败: {str(e)}")
            return False

    def approve_by_dept_manager(self, task_id: str, approved: bool, 
                                comment: str = "approved") -> bool:
        """部门经理审批"""
        url = f"{self.base_url}/api/leave/dept-manager/approve/{task_id}"
        params = {
            "approved": str(approved).lower(),
            "comment": comment
        }
        
        try:
            response = self.session.post(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                action = "批准" if approved else "拒绝"
                self.log_success(f"部门经理审批完成: {action}")
                return True
            else:
                self.log_error(f"审批失败: {result.get('message')}")
                return False
        except Exception as e:
            self.log_error(f"审批API调用失败: {str(e)}")
            return False

    def verify_status(self, process_id: str, expected_status: Status, 
                     expected_ended: bool = None) -> bool:
        """验证流程状态"""
        instance = self.get_process_instance(process_id)
        if not instance:
            return False
        
        actual_status = instance.get("status")
        actual_ended = instance.get("ended")
        
        status_match = actual_status == expected_status.value
        ended_match = expected_ended is None or actual_ended == expected_ended
        
        if status_match and ended_match:
            self.log_success(f"状态验证通过: {expected_status.value}")
            return True
        else:
            error_msg = f"状态验证失败: 期望={expected_status.value}, 实际={actual_status}"
            if expected_ended is not None:
                error_msg += f", 期望结束={expected_ended}, 实际结束={actual_ended}"
            self.log_error(error_msg)
            return False

    def verify_task_count(self, expected_count: int) -> bool:
        """验证任务数量"""
        tasks = self.get_task_list()
        actual_count = len(tasks)
        
        if actual_count == expected_count:
            self.log_success(f"任务数量验证通过: {actual_count}")
            return True
        else:
            self.log_error(f"任务数量验证失败: 期望={expected_count}, 实际={actual_count}")
            return False

    def wait(self, seconds: float = 0.5):
        """等待"""
        time.sleep(seconds)

    # ==================== 测试场景 ====================

    def test_scenario_1(self):
        """场景1：短期请假 - 审批通过"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}场景1：短期请假 - 审批通过 ✅{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        
        scenario_passed = True
        
        try:
            # 步骤1：申请请假
            self.log_step("步骤1", "申请2天假期")
            process_id = self.apply_leave("张三", 2, 10, "personal")
            if not process_id:
                scenario_passed = False
                self.result.add_fail("场景1: 申请请假失败")
                return
            self.wait()
            
            # 步骤2：验证初始状态
            self.log_step("步骤2", "验证流程状态为待审批")
            if not self.verify_status(process_id, Status.PENDING_MANAGER_APPROVAL, False):
                scenario_passed = False
            self.wait()
            
            # 步骤3：获取待办任务
            self.log_step("步骤3", "查询待办任务")
            tasks = self.get_task_list()
            if not tasks:
                self.log_error("没有找到待办任务")
                scenario_passed = False
                self.result.add_fail("场景1: 没有找到待办任务")
                return
            task_id = tasks[0]["id"]
            self.wait()
            
            # 步骤4：经理审批通过
            self.log_step("步骤4", "经理审批通过")
            if not self.approve_by_manager(task_id, True, "approved"):
                scenario_passed = False
            self.wait()
            
            # 步骤5：验证最终状态
            self.log_step("步骤5", "验证流程已批准并结束")
            if not self.verify_status(process_id, Status.APPROVED, True):
                scenario_passed = False
            self.wait()
            
            # 步骤6：验证任务已完成
            self.log_step("步骤6", "验证任务列表为空")
            if not self.verify_task_count(0):
                scenario_passed = False
            
            if scenario_passed:
                self.log_success(f"\n{Color.BOLD}场景1测试通过 ✓{Color.RESET}")
                self.result.add_pass()
            else:
                self.result.add_fail("场景1: 部分验证失败")
                
        except Exception as e:
            self.log_error(f"场景1执行出错: {str(e)}")
            self.result.add_fail(f"场景1: {str(e)}")

    def test_scenario_2(self):
        """场景2：短期请假 - 审批拒绝"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}场景2：短期请假 - 审批拒绝 ❌{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        
        scenario_passed = True
        
        try:
            # 步骤1：申请请假
            self.log_step("步骤1", "申请2天假期")
            process_id = self.apply_leave("李四", 2, 10, "test")
            if not process_id:
                scenario_passed = False
                self.result.add_fail("场景2: 申请请假失败")
                return
            self.wait()
            
            # 步骤2：获取待办任务
            self.log_step("步骤2", "查询待办任务")
            tasks = self.get_task_list()
            if not tasks:
                self.log_error("没有找到待办任务")
                scenario_passed = False
                self.result.add_fail("场景2: 没有找到待办任务")
                return
            task_id = tasks[0]["id"]
            self.wait()
            
            # 步骤3：经理审批拒绝
            self.log_step("步骤3", "经理审批拒绝")
            if not self.approve_by_manager(task_id, False, "rejected"):
                scenario_passed = False
            self.wait()
            
            # 步骤4：验证最终状态
            self.log_step("步骤4", "验证流程已拒绝并结束")
            if not self.verify_status(process_id, Status.REJECTED, True):
                scenario_passed = False
            self.wait()
            
            # 步骤5：验证任务已完成
            self.log_step("步骤5", "验证任务列表为空")
            if not self.verify_task_count(0):
                scenario_passed = False
            
            if scenario_passed:
                self.log_success(f"\n{Color.BOLD}场景2测试通过 ✓{Color.RESET}")
                self.result.add_pass()
            else:
                self.result.add_fail("场景2: 部分验证失败")
                
        except Exception as e:
            self.log_error(f"场景2执行出错: {str(e)}")
            self.result.add_fail(f"场景2: {str(e)}")

    def test_scenario_3(self):
        """场景3：长期请假 - 多级审批通过"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}场景3：长期请假 - 多级审批通过 ✅✅{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        
        scenario_passed = True
        
        try:
            # 步骤1：申请请假
            self.log_step("步骤1", "申请5天假期（需要多级审批）")
            process_id = self.apply_leave("王五", 5, 10, "vacation")
            if not process_id:
                scenario_passed = False
                self.result.add_fail("场景3: 申请请假失败")
                return
            self.wait()
            
            # 步骤2：验证初始状态
            self.log_step("步骤2", "验证流程状态为待直接经理审批")
            if not self.verify_status(process_id, Status.PENDING_MANAGER_APPROVAL, False):
                scenario_passed = False
            self.wait()
            
            # 步骤3：获取待办任务
            self.log_step("步骤3", "查询待办任务")
            tasks = self.get_task_list()
            if not tasks:
                self.log_error("没有找到待办任务")
                scenario_passed = False
                self.result.add_fail("场景3: 没有找到待办任务")
                return
            task_id = tasks[0]["id"]
            self.wait()
            
            # 步骤4：直接经理初审通过
            self.log_step("步骤4", "直接经理初审通过")
            if not self.approve_by_manager(task_id, True, "ok"):
                scenario_passed = False
            self.wait()
            
            # 步骤5：验证状态变化为待部门经理审批
            self.log_step("步骤5", "验证流程状态为待部门经理审批")
            if not self.verify_status(process_id, Status.PENDING_DEPT_MANAGER_APPROVAL, False):
                scenario_passed = False
            self.wait()
            
            # 步骤6：获取部门经理待办任务
            self.log_step("步骤6", "查询部门经理待办任务")
            tasks = self.get_task_list()
            if not tasks:
                self.log_error("没有找到部门经理待办任务")
                scenario_passed = False
                self.result.add_fail("场景3: 没有找到部门经理待办任务")
                return
            task_id = tasks[0]["id"]
            self.wait()
            
            # 步骤7：部门经理审批通过
            self.log_step("步骤7", "部门经理审批通过")
            if not self.approve_by_dept_manager(task_id, True, "approved"):
                scenario_passed = False
            self.wait()
            
            # 步骤8：验证最终状态
            self.log_step("步骤8", "验证流程已批准并结束")
            if not self.verify_status(process_id, Status.APPROVED, True):
                scenario_passed = False
            self.wait()
            
            # 步骤9：验证任务已完成
            self.log_step("步骤9", "验证任务列表为空")
            if not self.verify_task_count(0):
                scenario_passed = False
            
            if scenario_passed:
                self.log_success(f"\n{Color.BOLD}场景3测试通过 ✓{Color.RESET}")
                self.result.add_pass()
            else:
                self.result.add_fail("场景3: 部分验证失败")
                
        except Exception as e:
            self.log_error(f"场景3执行出错: {str(e)}")
            self.result.add_fail(f"场景3: {str(e)}")

    def test_scenario_4(self):
        """场景4：长期请假 - 经理初审拒绝"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}场景4：长期请假 - 经理初审拒绝 ❌{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        
        scenario_passed = True
        
        try:
            # 步骤1：申请请假
            self.log_step("步骤1", "申请5天假期")
            process_id = self.apply_leave("赵六", 5, 10, "test")
            if not process_id:
                scenario_passed = False
                self.result.add_fail("场景4: 申请请假失败")
                return
            self.wait()
            
            # 步骤2：获取待办任务
            self.log_step("步骤2", "查询待办任务")
            tasks = self.get_task_list()
            if not tasks:
                self.log_error("没有找到待办任务")
                scenario_passed = False
                self.result.add_fail("场景4: 没有找到待办任务")
                return
            task_id = tasks[0]["id"]
            self.wait()
            
            # 步骤3：直接经理拒绝
            self.log_step("步骤3", "直接经理初审拒绝")
            if not self.approve_by_manager(task_id, False, "rejected"):
                scenario_passed = False
            self.wait()
            
            # 步骤4：验证流程已结束，不会到达部门经理
            self.log_step("步骤4", "验证流程已拒绝并结束")
            if not self.verify_status(process_id, Status.REJECTED, True):
                scenario_passed = False
            self.wait()
            
            # 步骤5：验证任务列表为空
            self.log_step("步骤5", "验证任务列表为空")
            if not self.verify_task_count(0):
                scenario_passed = False
            
            if scenario_passed:
                self.log_success(f"\n{Color.BOLD}场景4测试通过 ✓{Color.RESET}")
                self.result.add_pass()
            else:
                self.result.add_fail("场景4: 部分验证失败")
                
        except Exception as e:
            self.log_error(f"场景4执行出错: {str(e)}")
            self.result.add_fail(f"场景4: {str(e)}")

    def test_scenario_5(self):
        """场景5：长期请假 - 部门经理拒绝"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}场景5：长期请假 - 部门经理拒绝 ❌{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        
        scenario_passed = True
        
        try:
            # 步骤1：申请请假
            self.log_step("步骤1", "申请5天假期")
            process_id = self.apply_leave("孙七", 5, 10, "test")
            if not process_id:
                scenario_passed = False
                self.result.add_fail("场景5: 申请请假失败")
                return
            self.wait()
            
            # 步骤2：直接经理通过
            self.log_step("步骤2", "直接经理初审通过")
            tasks = self.get_task_list()
            if not tasks:
                self.log_error("没有找到待办任务")
                scenario_passed = False
                self.result.add_fail("场景5: 没有找到待办任务")
                return
            task_id = tasks[0]["id"]
            if not self.approve_by_manager(task_id, True, "ok"):
                scenario_passed = False
            self.wait()
            
            # 步骤3：部门经理拒绝
            self.log_step("步骤3", "部门经理审批拒绝")
            tasks = self.get_task_list()
            if not tasks:
                self.log_error("没有找到部门经理待办任务")
                scenario_passed = False
                self.result.add_fail("场景5: 没有找到部门经理待办任务")
                return
            task_id = tasks[0]["id"]
            if not self.approve_by_dept_manager(task_id, False, "rejected"):
                scenario_passed = False
            self.wait()
            
            # 步骤4：验证流程已结束
            self.log_step("步骤4", "验证流程已拒绝并结束")
            if not self.verify_status(process_id, Status.REJECTED, True):
                scenario_passed = False
            self.wait()
            
            # 步骤5：验证任务列表为空
            self.log_step("步骤5", "验证任务列表为空")
            if not self.verify_task_count(0):
                scenario_passed = False
            
            if scenario_passed:
                self.log_success(f"\n{Color.BOLD}场景5测试通过 ✓{Color.RESET}")
                self.result.add_pass()
            else:
                self.result.add_fail("场景5: 部分验证失败")
                
        except Exception as e:
            self.log_error(f"场景5执行出错: {str(e)}")
            self.result.add_fail(f"场景5: {str(e)}")

    def test_scenario_6(self):
        """场景6：假期不足 - 自动拒绝"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}场景6：假期不足 - 自动拒绝 🚫{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        
        scenario_passed = True
        
        try:
            # 步骤1：申请请假（假期不足）
            self.log_step("步骤1", "申请15天假期（但只剩10天）")
            process_id = self.apply_leave("钱八", 15, 10, "long trip")
            if not process_id:
                scenario_passed = False
                self.result.add_fail("场景6: 申请请假失败")
                return
            self.wait()
            
            # 步骤2：验证流程自动拒绝
            self.log_step("步骤2", "验证流程因假期不足自动拒绝")
            if not self.verify_status(process_id, Status.INSUFFICIENT_LEAVE, True):
                scenario_passed = False
            self.wait()
            
            # 步骤3：验证没有创建任务
            self.log_step("步骤3", "验证没有创建审批任务")
            if not self.verify_task_count(0):
                scenario_passed = False
            
            if scenario_passed:
                self.log_success(f"\n{Color.BOLD}场景6测试通过 ✓{Color.RESET}")
                self.result.add_pass()
            else:
                self.result.add_fail("场景6: 部分验证失败")
                
        except Exception as e:
            self.log_error(f"场景6执行出错: {str(e)}")
            self.result.add_fail(f"场景6: {str(e)}")

    def run_all_scenarios(self):
        """运行所有测试场景"""
        print(f"\n{Color.BOLD}{Color.GREEN}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}{Color.GREEN}开始执行所有测试场景{Color.RESET}")
        print(f"{Color.BOLD}{Color.GREEN}{'='*60}{Color.RESET}\n")
        
        self.test_scenario_1()
        self.test_scenario_2()
        self.test_scenario_3()
        self.test_scenario_4()
        self.test_scenario_5()
        self.test_scenario_6()
        
        self.result.print_summary()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='员工请假流程自动化测试脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  # 运行所有测试场景
  python test_leave.py --all
  
  # 运行单个场景
  python test_leave.py --scenario 1
  
  # 运行多个场景
  python test_leave.py --scenario 1 2 6
  
  # 指定服务器地址
  python test_leave.py --all --url http://localhost:8080
        '''
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='运行所有测试场景'
    )
    
    parser.add_argument(
        '--scenario',
        type=int,
        nargs='+',
        choices=[1, 2, 3, 4, 5, 6],
        help='指定要运行的场景编号（1-6）'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        default='http://localhost:8080',
        help='服务器地址（默认：http://localhost:8080）'
    )
    
    args = parser.parse_args()
    
    # 创建测试客户端
    client = FlowableTestClient(base_url=args.url)
    
    print(f"\n{Color.BOLD}{Color.CYAN}员工请假流程自动化测试{Color.RESET}")
    print(f"{Color.CYAN}服务器地址: {args.url}{Color.RESET}\n")
    
    # 运行测试
    if args.scenario:
        # 运行指定的场景
        for scenario_num in args.scenario:
            method_name = f"test_scenario_{scenario_num}"
            if hasattr(client, method_name):
                getattr(client, method_name)()
            else:
                client.log_error(f"场景{scenario_num}不存在")
        
        client.result.print_summary()
    else:
        # 默认运行所有场景（无参数或使用--all）
        client.run_all_scenarios()


if __name__ == "__main__":
    main()
