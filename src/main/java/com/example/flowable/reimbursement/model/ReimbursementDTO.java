package com.example.flowable.reimbursement.model;

import java.time.LocalDate;
import java.util.List;

/**
 * 报销申请数据传输对象
 * 
 * @author Generated
 */
public class ReimbursementDTO {
    
    /**
     * 申请人姓名
     */
    private String applicantName;
    
    /**
     * 部门
     */
    private String department;
    
    /**
     * 报销类型（差旅、餐费、办公用品等）
     */
    private String reimbursementType;
    
    /**
     * 报销金额
     */
    private Double amount;
    
    /**
     * 币种（CNY、USD等）
     */
    private String currency;
    
    /**
     * 费用发生日期
     */
    private LocalDate expenseDate;
    
    /**
     * 费用说明
     */
    private String description;
    
    /**
     * 发票号码
     */
    private String invoiceNumber;
    
    /**
     * 附件列表（发票扫描件等）
     */
    private List<String> attachments;
    
    /**
     * 收款账号
     */
    private String bankAccount;
    
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
    
    public String getReimbursementType() {
        return reimbursementType;
    }
    
    public void setReimbursementType(String reimbursementType) {
        this.reimbursementType = reimbursementType;
    }
    
    public Double getAmount() {
        return amount;
    }
    
    public void setAmount(Double amount) {
        this.amount = amount;
    }
    
    public String getCurrency() {
        return currency;
    }
    
    public void setCurrency(String currency) {
        this.currency = currency;
    }
    
    public LocalDate getExpenseDate() {
        return expenseDate;
    }
    
    public void setExpenseDate(LocalDate expenseDate) {
        this.expenseDate = expenseDate;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public String getInvoiceNumber() {
        return invoiceNumber;
    }
    
    public void setInvoiceNumber(String invoiceNumber) {
        this.invoiceNumber = invoiceNumber;
    }
    
    public List<String> getAttachments() {
        return attachments;
    }
    
    public void setAttachments(List<String> attachments) {
        this.attachments = attachments;
    }
    
    public String getBankAccount() {
        return bankAccount;
    }
    
    public void setBankAccount(String bankAccount) {
        this.bankAccount = bankAccount;
    }
    
    @Override
    public String toString() {
        return "ReimbursementDTO{" +
                "applicantName='" + applicantName + '\'' +
                ", department='" + department + '\'' +
                ", reimbursementType='" + reimbursementType + '\'' +
                ", amount=" + amount +
                ", currency='" + currency + '\'' +
                ", expenseDate=" + expenseDate +
                ", description='" + description + '\'' +
                ", invoiceNumber='" + invoiceNumber + '\'' +
                ", bankAccount='" + bankAccount + '\'' +
                '}';
    }
}