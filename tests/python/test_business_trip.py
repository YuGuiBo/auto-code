#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
出差申请模块测试脚本
测试出差申请、审批流程和状态管理

测试场景：
1. 场景1：短期出差通过（≤3天）- 经理→行政
2. 场景2：长期出差通过（>3天）- 经理→部门经理→行政
3. 场景3：经理拒绝场景
4. 场景4：部门经理拒绝场景
5. 场景5：行政拒绝场景
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
def apply_business_trip(data):
    """提交出差申请"""
    url = f"{BASE_URL}/api/business-trip/apply"
    response = requests.post(url, json=data)
    return response

def manager_approve(task_id, approved, comment):
    """经理审批"""
    url = f"{BASE_URL}/api/business-trip/manager/approve/{task_id}"
    params = {
        "approved": approved,
        "comment": comment
    }
    response = requests.post(url, params=params)
    return response

def dept_manager_approve(task_id, approved, comment):
    """部门经理审批"""
    url = f"{BASE_URL}/api/business-trip/dept-manager/approve/{task_id}"
    params = {
        "approved": approved,
        "comment": comment
    }
    response = requests.post(url, params=params)
    return response

def admin_approve(task_id, approved, comment):
    """行政审批"""
    url = f"{BASE_URL}/api/business-trip/admin/approve/{task_id}"
    params = {
        "approved": approved,
        "comment": comment
    }
    response = requests.post(url, params=params)
    return response

def get_process_instance(process_instance_id):
    """查询流程实例"""
    url = f"{BASE_URL}/api/business-trip/process/instance/{process_instance_id}"
    response = requests.get(url)
    return response

def get_all_tasks():
    """查询所有待办任务"""
    url = f"{BASE_URL}/api/business-trip/task/list"
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

def test_scenario_1_short_trip_approved():
    """场景1：短期出差通过（≤3天）"""
    print_section("场景1：短期出差通过（≤3天）")
    
    # 1. 张三提交2天出差申请
    print_info("步骤1：张三提交2天上海出差...")
    trip_data = {
        "applicantName": "张三",
        "department": "销售部",
        "destination": "上海",
        "startDate": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "endDate": (datetime.now() + timedelta(days=9)).strftime("%Y-%m-%d"),
        "days": 2,
        "purpose": "客户拜访",
        "transportation": "高铁",
        "accommodation": "经济型",
        "estimatedCost": 1500.0,
        "companions": "无",
        "contactPhone": "13800138000"
    }
    
    response = apply_business_trip(trip_data)
    assert response.status_code == 200, "申请出差失败"
    process_instance_id = response.json()['processInstanceId']
    print_success(f"出差申请已提交，流程ID: {process_instance_id}")
    
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
    
    response = manager_approve(task['id'], True, "同意出差，注意安全")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    # 验证状态更新为待行政审批（短期出差跳过部门经理）
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_ADMIN_APPROVAL'
    
    time.sleep(1)
    
    # 3. 行政审批（批准）
    print_info("步骤3：行政审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None, "未找到行政审批任务"
    print_info(f"找到任务: {task['name']} (ID: {task['id']})")
    
    response = admin_approve(task['id'], True, "已预定高铁票和酒店")
    assert response.status_code == 200
    print_success("行政审批完成")
    
    # 验证最终状态
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'APPROVED'
    assert instance['ended'] == True
    
    print_success("✅ 场景1测试通过！短期出差流程正常完成")


def test_scenario_2_long_trip_approved():
    """场景2：长期出差通过（>3天）"""
    print_section("场景2：长期出差通过（>3天）")
    
    # 1. 李四提交7天出差申请
    print_info("步骤1：李四提交7天深圳出差...")
    trip_data = {
        "applicantName": "李四",
        "department": "技术部",
        "destination": "深圳",
        "startDate": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        "endDate": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
        "days": 7,
        "purpose": "项目实施",
        "transportation": "飞机",
        "accommodation": "商务型",
        "estimatedCost": 8000.0,
        "companions": "王五",
        "contactPhone": "13900139000"
    }
    
    response = apply_business_trip(trip_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"出差申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], True, "同意出差，做好项目实施")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    # 验证状态更新为待部门经理审批（长期出差需要部门经理）
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
    
    response = dept_manager_approve(task['id'], True, "同意出差，注意成本控制")
    assert response.status_code == 200
    print_success("部门经理审批完成")
    
    # 验证状态更新为待行政审批
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_ADMIN_APPROVAL'
    
    time.sleep(1)
    
    # 4. 行政审批（批准）
    print_info("步骤4：行政审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = admin_approve(task['id'], True, "已预定机票和商务酒店")
    assert response.status_code == 200
    print_success("行政审批完成")
    
    # 验证最终状态
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'APPROVED'
    assert instance['ended'] == True
    
    print_success("✅ 场景2测试通过！长期出差流程正常完成")


def test_scenario_3_manager_rejected():
    """场景3：经理拒绝场景"""
    print_section("场景3：经理拒绝场景")
    
    # 1. 王五提交5天出差申请
    print_info("步骤1：王五提交5天北京出差...")
    trip_data = {
        "applicantName": "王五",
        "department": "市场部",
        "destination": "北京",
        "startDate": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
        "endDate": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "days": 5,
        "purpose": "市场调研",
        "transportation": "飞机",
        "accommodation": "经济型",
        "estimatedCost": 5000.0,
        "companions": "无",
        "contactPhone": "13700137000"
    }
    
    response = apply_business_trip(trip_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"出差申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（拒绝）
    print_info("步骤2：直接经理审批（拒绝）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], False, "项目预算不足，不同意出差")
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
    
    # 1. 赵六提交10天出差申请
    print_info("步骤1：赵六提交10天广州出差...")
    trip_data = {
        "applicantName": "赵六",
        "department": "研发部",
        "destination": "广州",
        "startDate": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
        "endDate": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "days": 10,
        "purpose": "技术交流",
        "transportation": "飞机",
        "accommodation": "商务型",
        "estimatedCost": 12000.0,
        "companions": "孙七",
        "contactPhone": "13600136000"
    }
    
    response = apply_business_trip(trip_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"出差申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], True, "同意出差")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    time.sleep(1)
    
    # 3. 部门经理审批（拒绝）
    print_info("步骤3：部门经理审批（拒绝）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = dept_manager_approve(task['id'], False, "时间太长，影响项目进度，不同意")
    assert response.status_code == 200
    print_success("部门经理审批完成（拒绝）")
    
    # 验证最终状态为已拒绝
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'REJECTED'
    assert instance['ended'] == True
    
    print_success("✅ 场景4测试通过！部门经理拒绝流程正常结束")


def test_scenario_5_admin_rejected():
    """场景5：行政拒绝场景"""
    print_section("场景5：行政拒绝场景")
    
    # 1. 孙七提交1天出差申请
    print_info("步骤1：孙七提交1天杭州出差...")
    trip_data = {
        "applicantName": "孙七",
        "department": "采购部",
        "destination": "杭州",
        "startDate": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "endDate": (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d"),
        "days": 1,
        "purpose": "供应商考察",
        "transportation": "高铁",
        "accommodation": "经济型",
        "estimatedCost": 800.0,
        "companions": "无",
        "contactPhone": "13500135000"
    }
    
    response = apply_business_trip(trip_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"出差申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], True, "同意出差")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    time.sleep(1)
    
    # 3. 行政审批（拒绝）
    print_info("步骤3：行政审批（拒绝）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = admin_approve(task['id'], False, "高铁票已售罄，无法预定")
    assert response.status_code == 200
    print_success("行政审批完成（拒绝）")
    
    # 验证最终状态为已拒绝
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'REJECTED'
    assert instance['ended'] == True
    
    print_success("✅ 场景5测试通过！行政拒绝流程正常结束")


# 主函数
def main():
    """运行所有测试场景"""
    print("\n")
    print(f"{Colors.BLUE}{'='*60}")
    print("出差申请模块测试")
    print(f"{'='*60}{Colors.END}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {BASE_URL}")
    print()
    
    test_results = []
    
    # 测试场景列表
    test_scenarios = [
        ("场景1：短期出差通过（≤3天）", test_scenario_1_short_trip_approved),
        ("场景2：长期出差通过（>3天）", test_scenario_2_long_trip_approved),
        ("场景3：经理拒绝场景", test_scenario_3_manager_rejected),
        ("场景4：部门经理拒绝场景", test_scenario_4_dept_manager_rejected),
        ("场景5：行政拒绝场景", test_scenario_5_admin_rejected),
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
        print_success("出差申请模块测试完成，所有功能正常！")
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
