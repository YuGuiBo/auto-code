package com.example.flowable.overtime.model;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalTime;

/**
 * 加班申请DTO
 * 
 * @author Generated
 */
@Data
public class OvertimeDTO {
    
    /**
     * 申请人姓名
     */
    private String applicantName;
    
    /**
     * 部门
     */
    private String department;
    
    /**
     * 加班日期
     */
    private LocalDate overtimeDate;
    
    /**
     * 开始时间
     */
    private LocalTime startTime;
    
    /**
     * 结束时间
     */
    private LocalTime endTime;
    
    /**
     * 加班时长（小时）
     */
    private Double hours;
    
    /**
     * 加班类型（WEEKDAY-工作日, WEEKEND-周末, HOLIDAY-节假日）
     */
    private String overtimeType;
    
    /**
     * 加班原因
     */
    private String reason;
    
    /**
     * 工作内容
     */
    private String workContent;
    
    /**
     * 补偿方式（REST-调休, PAY-加班费）
     */
    private String compensationType;
}