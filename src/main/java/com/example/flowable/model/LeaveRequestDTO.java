package com.example.flowable.model;

import lombok.Data;
import java.time.LocalDate;

/**
 * 请假申请DTO
 * 
 * @author Generated
 */
@Data
public class LeaveRequestDTO {
    
    /**
     * 申请人姓名
     */
    private String applicantName;
    
    /**
     * 请假天数
     */
    private Integer leaveDays;
    
    /**
     * 剩余假期天数
     */
    private Integer remainingDays;
    
    /**
     * 请假原因
     */
    private String reason;
    
    /**
     * 开始日期
     */
    private LocalDate startDate;
    
    /**
     * 结束日期
     */
    private LocalDate endDate;
    
    /**
     * 请假类型（年假、病假、事假等）
     */
    private String leaveType;
}