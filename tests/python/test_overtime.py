#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加班申请模块测试脚本
测试加班申请、审批流程和状态管理

测试场景：
1. 场景1：工作日短时间加班通过（≤2小时）
2. 场景2：工作日长时间加班通过（>2小时）
3. 场景3：周末加班通过
4. 场景4：节假日加班通过
5. 场景5：经理拒绝场景
6. 场景6：部门经理拒绝场景
7. 场景7：HR拒绝场景
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
def apply_overtime(data):
    """提交加班申请"""
    url = f"{BASE_URL}/api/overtime/apply"
    response = requests.post(url, json=data)
    return response

def manager_approve(task_id, approved, comment):
    """经理审批"""
    url = f"{BASE_URL}/api/overtime/manager/approve/{task_id}"
    params = {
        "approved": approved,
        "comment": comment
    }
    response = requests.post(url, params=params)
    return response

def dept_manager_approve(task_id, approved, comment):
    """部门经理审批"""
    url = f"{BASE_URL}/api/overtime/dept-manager/approve/{task_id}"
    params = {
        "approved": approved,
        "comment": comment
    }
    response = requests.post(url, params=params)
    return response

def hr_confirm(task_id, approved, comment):
    """HR确认"""
    url = f"{BASE_URL}/api/overtime/hr/confirm/{task_id}"
    params = {
        "approved": approved,
        "comment": comment
    }
    response = requests.post(url, params=params)
    return response

def get_process_instance(process_instance_id):
    """查询流程实例"""
    url = f"{BASE_URL}/api/overtime/process/instance/{process_instance_id}"
    response = requests.get(url)
    return response

def get_all_tasks():
    """查询所有待办任务"""
    url = f"{BASE_URL}/api/overtime/task/list"
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

def test_scenario_1_weekday_short_overtime_approved():
    """场景1：工作日短时间加班通过（≤2小时）"""
    print_section("场景1：工作日短时间加班通过（≤2小时）")
    
    # 1. 张三提交工作日2小时加班
    print_info("步骤1：张三提交工作日2小时加班...")
    overtime_data = {
        "applicantName": "张三",
        "department": "技术部",
        "overtimeDate": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "startTime": "18:00:00",
        "endTime": "20:00:00",
        "hours": 2.0,
        "overtimeType": "WEEKDAY",
        "reason": "项目紧急上线",
        "workContent": "系统部署和测试",
        "compensationType": "REST"
    }
    
    response = apply_overtime(overtime_data)
    assert response.status_code == 200, "申请加班失败"
    process_instance_id = response.json()['processInstanceId']
    print_success(f"加班申请已提交，流程ID: {process_instance_id}")
    
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
    
    response = manager_approve(task['id'], True, "同意加班，辛苦了")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    # 验证状态更新为待HR确认
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_HR_CONFIRMATION'
    
    time.sleep(1)
    
    # 3. HR确认（批准）
    print_info("步骤3：HR确认（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None, "未找到HR确认任务"
    print_info(f"找到任务: {task['name']} (ID: {task['id']})")
    
    response = hr_confirm(task['id'], True, "加班已记录，可调休")
    assert response.status_code == 200
    print_success("HR确认完成")
    
    # 验证最终状态
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'APPROVED'
    assert instance['ended'] == True
    
    print_success("✅ 场景1测试通过！工作日短时间加班流程正常完成")


def test_scenario_2_weekday_long_overtime_approved():
    """场景2：工作日长时间加班通过（>2小时）"""
    print_section("场景2：工作日长时间加班通过（>2小时）")
    
    # 1. 李四提交工作日5小时加班
    print_info("步骤1：李四提交工作日5小时加班...")
    overtime_data = {
        "applicantName": "李四",
        "department": "研发部",
        "overtimeDate": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "startTime": "18:00:00",
        "endTime": "23:00:00",
        "hours": 5.0,
        "overtimeType": "WEEKDAY",
        "reason": "版本发布前紧急修复Bug",
        "workContent": "Bug修复和回归测试",
        "compensationType": "PAY"
    }
    
    response = apply_overtime(overtime_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"加班申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], True, "同意加班")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    # 验证状态更新为待部门经理审批
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
    
    response = dept_manager_approve(task['id'], True, "同意加班，注意休息")
    assert response.status_code == 200
    print_success("部门经理审批完成")
    
    # 验证状态更新为待HR确认
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_HR_CONFIRMATION'
    
    time.sleep(1)
    
    # 4. HR确认（批准）
    print_info("步骤4：HR确认（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = hr_confirm(task['id'], True, "加班已记录，将发放加班费")
    assert response.status_code == 200
    print_success("HR确认完成")
    
    # 验证最终状态
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'APPROVED'
    assert instance['ended'] == True
    
    print_success("✅ 场景2测试通过！工作日长时间加班流程正常完成")


def test_scenario_3_weekend_overtime_approved():
    """场景3：周末加班通过"""
    print_section("场景3：周末加班通过")
    
    # 1. 王五提交周末加班
    print_info("步骤1：王五提交周末加班...")
    overtime_data = {
        "applicantName": "王五",
        "department": "产品部",
        "overtimeDate": (datetime.now() + timedelta(days=6)).strftime("%Y-%m-%d"),
        "startTime": "09:00:00",
        "endTime": "18:00:00",
        "hours": 8.0,
        "overtimeType": "WEEKEND",
        "reason": "新功能开发冲刺",
        "workContent": "产品原型设计",
        "compensationType": "REST"
    }
    
    response = apply_overtime(overtime_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"加班申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], True, "同意周末加班")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    # 验证状态更新为待部门经理审批
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_DEPT_MANAGER_APPROVAL'
    
    time.sleep(1)
    
    # 3. 部门经理审批（批准）
    print_info("步骤3：部门经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = dept_manager_approve(task['id'], True, "同意周末加班")
    assert response.status_code == 200
    print_success("部门经理审批完成")
    
    # 验证状态更新为待HR确认
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_HR_CONFIRMATION'
    
    time.sleep(1)
    
    # 4. HR确认（批准）
    print_info("步骤4：HR确认（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = hr_confirm(task['id'], True, "周末加班已记录")
    assert response.status_code == 200
    print_success("HR确认完成")
    
    # 验证最终状态
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'APPROVED'
    assert instance['ended'] == True
    
    print_success("✅ 场景3测试通过！周末加班流程正常完成")


def test_scenario_4_holiday_overtime_approved():
    """场景4：节假日加班通过"""
    print_section("场景4：节假日加班通过")
    
    # 1. 赵六提交节假日加班
    print_info("步骤1：赵六提交节假日加班...")
    overtime_data = {
        "applicantName": "赵六",
        "department": "运维部",
        "overtimeDate": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
        "startTime": "09:00:00",
        "endTime": "17:00:00",
        "hours": 7.0,
        "overtimeType": "HOLIDAY",
        "reason": "系统紧急维护",
        "workContent": "数据库升级和系统维护",
        "compensationType": "PAY"
    }
    
    response = apply_overtime(overtime_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"加班申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], True, "同意节假日加班")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    # 验证状态更新为待部门经理审批
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_DEPT_MANAGER_APPROVAL'
    
    time.sleep(1)
    
    # 3. 部门经理审批（批准）
    print_info("步骤3：部门经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = dept_manager_approve(task['id'], True, "同意节假日加班，按3倍工资计算")
    assert response.status_code == 200
    print_success("部门经理审批完成")
    
    # 验证状态更新为待HR确认
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"当前状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'PENDING_HR_CONFIRMATION'
    
    time.sleep(1)
    
    # 4. HR确认（批准）
    print_info("步骤4：HR确认（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = hr_confirm(task['id'], True, "节假日加班已记录，将按3倍工资发放")
    assert response.status_code == 200
    print_success("HR确认完成")
    
    # 验证最终状态
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'APPROVED'
    assert instance['ended'] == True
    
    print_success("✅ 场景4测试通过！节假日加班流程正常完成")


def test_scenario_5_manager_rejected():
    """场景5：经理拒绝场景"""
    print_section("场景5：经理拒绝场景")
    
    # 1. 孙七提交加班申请
    print_info("步骤1：孙七提交加班申请...")
    overtime_data = {
        "applicantName": "孙七",
        "department": "市场部",
        "overtimeDate": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "startTime": "18:00:00",
        "endTime": "22:00:00",
        "hours": 4.0,
        "overtimeType": "WEEKDAY",
        "reason": "整理市场调研报告",
        "workContent": "数据分析和报告撰写",
        "compensationType": "REST"
    }
    
    response = apply_overtime(overtime_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"加班申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（拒绝）
    print_info("步骤2：直接经理审批（拒绝）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], False, "工作可以正常工作时间完成，不需要加班")
    assert response.status_code == 200
    print_success("经理审批完成（拒绝）")
    
    # 验证最终状态为已拒绝
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'REJECTED'
    assert instance['ended'] == True
    
    print_success("✅ 场景5测试通过！经理拒绝流程正常结束")


def test_scenario_6_dept_manager_rejected():
    """场景6：部门经理拒绝场景"""
    print_section("场景6：部门经理拒绝场景")
    
    # 1. 周八提交周末加班
    print_info("步骤1：周八提交周末加班...")
    overtime_data = {
        "applicantName": "周八",
        "department": "设计部",
        "overtimeDate": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "startTime": "10:00:00",
        "endTime": "19:00:00",
        "hours": 8.0,
        "overtimeType": "WEEKEND",
        "reason": "项目设计稿修改",
        "workContent": "UI设计优化",
        "compensationType": "REST"
    }
    
    response = apply_overtime(overtime_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"加班申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], True, "同意加班")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    time.sleep(1)
    
    # 3. 部门经理审批（拒绝）
    print_info("步骤3：部门经理审批（拒绝）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = dept_manager_approve(task['id'], False, "周末加班成本太高，建议工作日加班")
    assert response.status_code == 200
    print_success("部门经理审批完成（拒绝）")
    
    # 验证最终状态为已拒绝
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'REJECTED'
    assert instance['ended'] == True
    
    print_success("✅ 场景6测试通过！部门经理拒绝流程正常结束")


def test_scenario_7_hr_rejected():
    """场景7：HR拒绝场景"""
    print_section("场景7：HR拒绝场景")
    
    # 1. 吴九提交加班申请
    print_info("步骤1：吴九提交加班申请...")
    overtime_data = {
        "applicantName": "吴九",
        "department": "财务部",
        "overtimeDate": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "startTime": "18:00:00",
        "endTime": "20:00:00",
        "hours": 2.0,
        "overtimeType": "WEEKDAY",
        "reason": "月度财务报表整理",
        "workContent": "报表审核",
        "compensationType": "PAY"
    }
    
    response = apply_overtime(overtime_data)
    assert response.status_code == 200
    process_instance_id = response.json()['processInstanceId']
    print_success(f"加班申请已提交，流程ID: {process_instance_id}")
    
    time.sleep(1)
    
    # 2. 直接经理审批（批准）
    print_info("步骤2：直接经理审批（批准）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = manager_approve(task['id'], True, "同意加班")
    assert response.status_code == 200
    print_success("经理审批完成")
    
    time.sleep(1)
    
    # 3. HR确认（拒绝）
    print_info("步骤3：HR确认（拒绝）...")
    task = find_task_by_process_id(process_instance_id)
    assert task is not None
    
    response = hr_confirm(task['id'], False, "本月加班时长已达上限，不能继续加班")
    assert response.status_code == 200
    print_success("HR确认完成（拒绝）")
    
    # 验证最终状态为已拒绝
    response = get_process_instance(process_instance_id)
    instance = response.json()
    print_info(f"最终状态: {instance['statusDisplayName']}")
    assert instance['status'] == 'REJECTED'
    assert instance['ended'] == True
    
    print_success("✅ 场景7测试通过！HR拒绝流程正常结束")


# 主函数
def main():
    """运行所有测试场景"""
    print("\n")
    print(f"{Colors.BLUE}{'='*60}")
    print("加班申请模块测试")
    print(f"{'='*60}{Colors.END}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {BASE_URL}")
    print()
    
    test_results = []
    
    # 测试场景列表
    test_scenarios = [
        ("场景1：工作日短时间加班通过（≤2小时）", test_scenario_1_weekday_short_overtime_approved),
        ("场景2：工作日长时间加班通过（>2小时）", test_scenario_2_weekday_long_overtime_approved),
        ("场景3：周末加班通过", test_scenario_3_weekend_overtime_approved),
        ("场景4：节假日加班通过", test_scenario_4_holiday_overtime_approved),
        ("场景5：经理拒绝场景", test_scenario_5_manager_rejected),
        ("场景6：部门经理拒绝场景", test_scenario_6_dept_manager_rejected),
        ("场景7：HR拒绝场景", test_scenario_7_hr_rejected),
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
        print_success("加班申请模块测试完成，所有功能正常！")
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
