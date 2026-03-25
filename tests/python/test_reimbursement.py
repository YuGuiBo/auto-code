#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报销管理模块测试脚本
测试报销申请、审批流程和状态管理

测试场景：
1. 场景1：小额报销通过（≤1000元）- 经理→财务
2. 场景2：大额报销通过（>1000元）- 经理→部门经理→财务
3. 场景3：经理拒绝场景
4. 场景4：部门经理拒绝场景
5. 场景5：财务拒绝场景
"""

import requests
import json
import time
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:8080"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.END}\n")

# 辅助函数
def apply_reimbursement(data):
    """提交报销申请"""
    url = f"{BASE_URL}/api/reimbursement/apply"
    response = requests.post(url, json=data)
    return response

def manager_approve(task_id, approved, comment):
    """经理审批"""
    url = f"{BASE_URL}/api/reimbursement/manager/approve/{task_id}"
    params = {
        "approved": approved,
        "comment": comment
    }
    response = requests.post(url, params=params)
    return response

def dept_manager_approve(task_id, approved, comment):
    """部门经理审批"""
    url = f"{BASE_URL}/api/reimbursement/dept-manager/approve/{task_id}"
    params = {
        "approved": approved,
        "comment": comment
    }
    response = requests.post(url, params=params)
    return response

def finance_approve(task_id, approved, comment):
    """财务审批"""
    url = f"{BASE_URL}/api/reimbursement/finance/approve/{task_id}"
    params = {
        "approved": approved,
        "comment": comment
    }
    response = requests.post(url, params=params)
    return response

def get_process_instance(process_instance_id):
    """查询流程实例"""
    url = f"{BASE_URL}/api/reimbursement/process/instance/{process_instance_id}"
    response = requests.get(url)
    return response

def get_all_tasks():
    """查询所有待办任务"""
    url = f"{BASE_URL}/api/reimbursement/task/list"
    response = requests.get(url)
    return response

def find_task_by_process_id(process_instance_id):
    """根据流程实例ID查找任务"""
    response = get_all_tasks()
    if response.status_code == 200:
        tasks = response.json()
        for task in tasks:
            if task.get('processInstanceId') == process_instance_id:
                return task
    return None

# 测试场景

def test_scenario_1_small_amount_approved():
    """场景1：小额报销通过（≤1000元）"""
    print_section("场景1：小额报销通过（≤1000元）")
    
    # 1. 张三提交800元报销申请
    print_info("步骤1：张三提交800元差旅报销...")
    reimbursement_data = {
        "applicantName": "张三",
        "department": "技术部",
        "reimbursementType": "差旅费",
        "amount": 800.0,
        "currency": "CNY",
        "expenseDate": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "北京出差车费和住宿费",
        "invoiceNumber": "INV-2026-001",
        "bankAccount": "6222021234567890"
    }
    
    response = apply_reimbursement(reimbursement_data)
    assert response.status_code == 200, "申请报销失败"
    process_instance_id = response.json()['processInstanceId']
    print_success(f"报销申请已提交，流程ID: {process_instance_id}")
    
    # 验证初始状态
    response = get_process_instance(process_instance_id)
    assert response.status_code == 200
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_MANAGER_APPROVAL'
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None, "未找到待办任务"
    print_info(f"找到任务: {task['name']} (ID: {task['id']})")
    
    response = manager_approve(task['id'], True, "同意报销，金额合理")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    # 验证状态更新为待财务审批（小额报销跳过部门经理）
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_FINANCE_APPROVAL'
    
    time.sleep(1)
    
    # 3. 财务审批（批准）
    print_info("步骤3：财务审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None, "未找到财务审批任务"
    print_info(f"找到任务: {task['name']} (ID: {task['id']})")
    
    response = finance_approve(task['id'], True, "财务审批通过，准备打款")
    assert response.status_code == 200
    print_success("财务审批完成")
    
    # 验证最终状态
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'APPROVED'
    assert instance['ended'] == True
    
    print_success("✅ 场景1测试通过！小额报销流程正常完成")


def test_scenario_2_large_amount_approved():
    """场景2：大额报销通过（>1000元）"""
    print_section("场景2：大额报销通过（>1000元）")
    
    # 1. 李四提交5000元报销申请
    print_info("步骤1：李四提交5000元设备采购报销...")
    reimbursement_data = {
        "applicantName": "李四",
        "department": "技术部",
        "reimbursementType": "办公用品",
        "amount": 5000.0,
        "currency": "CNY",
        "expenseDate": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "description": "购买开发服务器和网络设备",
        "invoiceNumber": "INV-2026-002",
        "bankAccount": "6222029876543210"
    }
    
    response = apply_reimbursement(reimbursement_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"报销申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], True, "同意报销，设备确实需要")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    # 验证状态更新为待部门经理审批（大额报销需要部门经理）
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_DEPT_MANAGER_APPROVAL'
    
    time.sleep(1)
    
    # 3. 部门经理审批（批准）
    print_info("步骤3：部门经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    print_info(f"找到任务: {task['name']} (ID: {task['id']})")
    
    response = dept_manager_approve(task['id'], True, "同意报销，项目需要")
    assert response.status_code == 200
    print_success("部门经理审批完成")
    
    # 验证状态更新为待财务审批
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_FINANCE_APPROVAL'
    
    time.sleep(1)
    
    # 4. 财务审批（批准）
    print_info("步骤4：财务审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = finance_approve(task['id'], True, "财务审批通过，准备打款")
    assert response.status_code == 200
    print_success("财务审批完成")
    
    # 验证最终状态
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'APPROVED'
    assert instance['ended'] == True
    
    print_success("✅ 场景2测试通过！大额报销流程正常完成")


def test_scenario_3_manager_rejected():
    """场景3：经理拒绝场景"""
    print_section("场景3：经理拒绝场景")
    
    # 1. 王五提交1200元报销申请
    print_info("步骤1：王五提交1200元餐费报销...")
    reimbursement_data = {
        "applicantName": "王五",
        "department": "销售部",
        "reimbursementType": "餐费",
        "amount": 1200.0,
        "currency": "CNY",
        "expenseDate": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "description": "客户接待餐费",
        "invoiceNumber": "INV-2026-003",
        "bankAccount": "6222025555666677"
    }
    
    response = apply_reimbursement(reimbursement_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"报销申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（拒绝）
    print_info("步骤2：直接经理审批（拒绝）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], False, "无预算，不同意报销")
    assert response.status_code == 200
    print_success("经理审批完成（拒绝）")
    
    # 验证最终状态为已拒绝
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'REJECTED'
    assert instance['ended'] == True
    
    print_success("✅ 场景3测试通过！经理拒绝流程正常结束")


def test_scenario_4_dept_manager_rejected():
    """场景4：部门经理拒绝场景"""
    print_section("场景4：部门经理拒绝场景")
    
    # 1. 赵六提交3000元报销申请
    print_info("步骤1：赵六提交3000元培训费报销...")
    reimbursement_data = {
        "applicantName": "赵六",
        "department": "人力资源部",
        "reimbursementType": "培训费",
        "amount": 3000.0,
        "currency": "CNY",
        "expenseDate": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
        "description": "参加外部技术培训",
        "invoiceNumber": "INV-2026-004",
        "bankAccount": "6222028888999900"
    }
    
    response = apply_reimbursement(reimbursement_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"报销申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], True, "同意报销")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    time.sleep(1)
    
    # 3. 部门经理审批（拒绝）
    print_info("步骤3：部门经理审批（拒绝）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = dept_manager_approve(task['id'], False, "培训内容与工作不符，不同意报销")
    assert response.status_code == 200
    print_success("部门经理审批完成（拒绝）")
    
    # 验证最终状态为已拒绝
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'REJECTED'
    assert instance['ended'] == True
    
    print_success("✅ 场景4测试通过！部门经理拒绝流程正常结束")


def test_scenario_5_finance_rejected():
    """场景5：财务拒绝场景"""
    print_section("场景5：财务拒绝场景")
    
    # 1. 孙七提交600元报销申请
    print_info("步骤1：孙七提交600元交通费报销...")
    reimbursement_data = {
        "applicantName": "孙七",
        "department": "市场部",
        "reimbursementType": "交通费",
        "amount": 600.0,
        "currency": "CNY",
        "expenseDate": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "出租车费和停车费",
        "invoiceNumber": "INV-2026-005",
        "bankAccount": "6222027777888899"
    }
    
    response = apply_reimbursement(reimbursement_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"报销申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], True, "同意报销")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    time.sleep(1)
    
    # 3. 财务审批（拒绝）
    print_info("步骤3：财务审批（拒绝）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = finance_approve(task['id'], False, "发票不符合规定，不予报销")
    assert response.status_code == 200
    print_success("财务审批完成（拒绝）")
    
    # 验证最终状态为已拒绝
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'REJECTED'
    assert instance['ended'] == True
    
    print_success("✅ 场景5测试通过！财务拒绝流程正常结束")


# 主函数
def main():
    """运行所有测试场景"""
    print("\n")
    print(f"{Colors.BLUE}{'='*60}")
    print("报销管理模块测试")
    print(f"{'='*60}{Colors.END}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {BASE_URL}")
    print()
    
    test_results = []
    
    # 测试场景列表
    test_scenarios = [
        ("场景1：小额报销通过（≤1000元）", test_scenario_1_small_amount_approved),
        ("场景2：大额报销通过（>1000元）", test_scenario_2_large_amount_approved),
        ("场景3：经理拒绝场景", test_scenario_3_manager_rejected),
        ("场景4：部门经理拒绝场景", test_scenario_4_dept_manager_rejected),
        ("场景5：财务拒绝场景", test_scenario_5_finance_rejected),
    ]
    
    # 运行所有测试
    for test_name, test_func in test_scenarios:
        try:
            test_func()
            test_results.append((test_name, True, None))
        except AssertionError as e:
            print_error(f"❌ {test_name} 失败: {str(e)}")
            test_results.append((test_name, False, str(e)))
        except Exception as e:
            print_error(f"❌ {test_name} 异常: {str(e)}")
            test_results.append((test_name, False, str(e)))
    
    # 打印测试结果摘要
    print_section("测试结果摘要")
    passed = sum(1 for _, result, _ in test_results if result)
    total = len(test_results)
    
    for test_name, result, error in test_results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}: {error}")
    
    print()
    if passed == total:
        print_success(f"✅ 所有测试通过！({passed}/{total})")
        print_success("报销管理模块测试完成，所有功能正常！")
    else:
        print_error(f"❌ 部分测试失败！({passed}/{total})")
        print_warning("请检查失败的测试场景")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\n测试被用户中断")
        exit(1)
    except Exception as e:
        print_error(f"\n测试执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
