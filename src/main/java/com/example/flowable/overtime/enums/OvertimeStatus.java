package com.example.flowable.overtime.enums;

/**
 * 加班申请状态枚举
 * 
 * @author Generated
 */
public enum OvertimeStatus {
    
    /**
     * 已提交（初始状态）
     */
    SUBMITTED("已提交", "加班申请已提交，等待处理"),
    
    /**
     * 待直接经理审批
     */
    PENDING_MANAGER_APPROVAL("待直接经理审批", "等待直接经理审批"),
    
    /**
     * 待部门经理审批（周末/节假日加班）
     */
    PENDING_DEPT_MANAGER_APPROVAL("待部门经理审批", "等待部门经理审批"),
    
    /**
     * 待HR确认
     */
    PENDING_HR_CONFIRMATION("待HR确认", "等待HR确认加班记录"),
    
    /**
     * 已批准
     */
    APPROVED("已批准", "加班申请已批准"),
    
    /**
     * 已拒绝
     */
    REJECTED("已拒绝", "加班申请已被拒绝"),
    
    /**
     * 已补偿
     */
    COMPENSATED("已补偿", "加班已调休或发放加班费");
    
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
    OvertimeStatus(String displayName, String description) {
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
    public static OvertimeStatus fromDisplayName(String displayName) {
        for (OvertimeStatus status : values()) {
            if (status.displayName.equals(displayName)) {
                return status;
            }
        }
        return null;
    }
}