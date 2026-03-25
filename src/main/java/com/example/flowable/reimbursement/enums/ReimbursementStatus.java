package com.example.flowable.reimbursement.enums;

/**
 * 报销申请状态枚举
 * 
 * @author Generated
 */
public enum ReimbursementStatus {
    
    /**
     * 已提交（初始状态）
     */
    SUBMITTED("已提交", "报销申请已提交，等待处理"),
    
    /**
     * 待直接经理审批
     */
    PENDING_MANAGER_APPROVAL("待直接经理审批", "等待直接经理审批"),
    
    /**
     * 待部门经理审批（仅大额报销>1000元）
     */
    PENDING_DEPT_MANAGER_APPROVAL("待部门经理审批", "等待部门经理审批"),
    
    /**
     * 待财务审批
     */
    PENDING_FINANCE_APPROVAL("待财务审批", "等待财务部门审批"),
    
    /**
     * 已批准
     */
    APPROVED("已批准", "报销申请已批准，等待打款"),
    
    /**
     * 已拒绝
     */
    REJECTED("已拒绝", "报销申请已被拒绝");
    
    /**
     * 状态名称（中文）
     */
    private final String displayName;
    
    /**
     * 状态描述
     */
    private final String description;
    
    /**
     * 构造函数
     * 
     * @param displayName 显示名称
     * @param description 描述
     */
    ReimbursementStatus(String displayName, String description) {
        this.displayName = displayName;
        this.description = description;
    }
    
    /**
     * 获取显示名称
     * 
     * @return 显示名称
     */
    public String getDisplayName() {
        return displayName;
    }
    
    /**
     * 获取描述
     * 
     * @return 描述
     */
    public String getDescription() {
        return description;
    }
    
    /**
     * 根据显示名称获取枚举
     * 
     * @param displayName 显示名称
     * @return 枚举值，如果未找到返回null
     */
    public static ReimbursementStatus fromDisplayName(String displayName) {
        for (ReimbursementStatus status : values()) {
            if (status.displayName.equals(displayName)) {
                return status;
            }
        }
        return null;
    }
}