package com.example.flowable.businesstrip.model;

import java.time.LocalDate;

/**
 * 出差申请数据传输对象
 * 
 * @author Generated
 */
public class BusinessTripDTO {
    
    /**
     * 申请人姓名
     */
    private String applicantName;
    
    /**
     * 部门
     */
    private String department;
    
    /**
     * 出差目的地
     */
    private String destination;
    
    /**
     * 出发日期
     */
    private LocalDate startDate;
    
    /**
     * 返回日期
     */
    private LocalDate endDate;
    
    /**
     * 出差天数
     */
    private Integer days;
    
    /**
     * 出差目的
     */
    private String purpose;
    
    /**
     * 交通方式（飞机、火车、汽车）
     */
    private String transportation;
    
    /**
     * 住宿要求（经济型、商务型）
     */
    private String accommodation;
    
    /**
     * 预计费用
     */
    private Double estimatedCost;
    
    /**
     * 同行人员
     */
    private String companions;
    
    /**
     * 出差期间联系电话
     */
    private String contactPhone;
    
    // Getter and Setter methods
    
    public String getApplicantName() {
        return applicantName;
    }
    
    public void setApplicantName(String applicantName) {
        this.applicantName = applicantName;
    }
    
    public String getDepartment() {
        return department;
    }
    
    public void setDepartment(String department) {
        this.department = department;
    }
    
    public String getDestination() {
        return destination;
    }
    
    public void setDestination(String destination) {
        this.destination = destination;
    }
    
    public LocalDate getStartDate() {
        return startDate;
    }
    
    public void setStartDate(LocalDate startDate) {
        this.startDate = startDate;
    }
    
    public LocalDate getEndDate() {
        return endDate;
    }
    
    public void setEndDate(LocalDate endDate) {
        this.endDate = endDate;
    }
    
    public Integer getDays() {
        return days;
    }
    
    public void setDays(Integer days) {
        this.days = days;
    }
    
    public String getPurpose() {
        return purpose;
    }
    
    public void setPurpose(String purpose) {
        this.purpose = purpose;
    }
    
    public String getTransportation() {
        return transportation;
    }
    
    public void setTransportation(String transportation) {
        this.transportation = transportation;
    }
    
    public String getAccommodation() {
        return accommodation;
    }
    
    public void setAccommodation(String accommodation) {
        this.accommodation = accommodation;
    }
    
    public Double getEstimatedCost() {
        return estimatedCost;
    }
    
    public void setEstimatedCost(Double estimatedCost) {
        this.estimatedCost = estimatedCost;
    }
    
    public String getCompanions() {
        return companions;
    }
    
    public void setCompanions(String companions) {
        this.companions = companions;
    }
    
    public String getContactPhone() {
        return contactPhone;
    }
    
    public void setContactPhone(String contactPhone) {
        this.contactPhone = contactPhone;
    }
    
    @Override
    public String toString() {
        return "BusinessTripDTO{" +
                "applicantName='" + applicantName + '\'' +
                ", department='" + department + '\'' +
                ", destination='" + destination + '\'' +
                ", startDate=" + startDate +
                ", endDate=" + endDate +
                ", days=" + days +
                ", purpose='" + purpose + '\'' +
                ", transportation='" + transportation + '\'' +
                ", accommodation='" + accommodation + '\'' +
                ", estimatedCost=" + estimatedCost +
                ", companions='" + companions + '\'' +
                ", contactPhone='" + contactPhone + '\'' +
                '}';
    }
}