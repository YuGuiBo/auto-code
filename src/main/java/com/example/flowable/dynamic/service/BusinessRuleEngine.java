package com.example.flowable.dynamic.service;

import com.example.flowable.dynamic.model.BusinessRule;
import lombok.extern.slf4j.Slf4j;
import org.springframework.expression.Expression;
import org.springframework.expression.ExpressionParser;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.StandardEvaluationContext;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * 业务规则引擎
 * 使用Spring Expression Language (SpEL)执行业务规则
 * 
 * @author Auto-Code Platform
 */
@Slf4j
@Service
public class BusinessRuleEngine {
    
    private final ExpressionParser parser = new SpelExpressionParser();
    
    /**
     * 评估业务规则
     * 返回第一个匹配的规则，如果没有匹配则返回null
     * 
     * @param rules 规则列表
     * @param variables 变量上下文
     * @return 匹配的规则，如果没有匹配则返回null
     */
    public BusinessRule evaluateRules(List<BusinessRule> rules, Map<String, Object> variables) {
        if (rules == null || rules.isEmpty()) {
            return null;
        }
        
        // 创建SpEL评估上下文
        StandardEvaluationContext context = new StandardEvaluationContext();
        
        // 设置根对象为 variables Map，这样可以直接使用变量名
        context.setRootObject(variables);
        
        // 将所有变量也注册为命名变量（支持 #variableName 语法）
        for (Map.Entry<String, Object> entry : variables.entrySet()) {
            context.setVariable(entry.getKey(), entry.getValue());
        }
        
        // 按顺序评估规则
        for (BusinessRule rule : rules) {
            try {
                String condition = rule.getCondition();
                
                // 解析并执行表达式
                Expression expression = parser.parseExpression(condition);
                Boolean result = expression.getValue(context, Boolean.class);
                
                if (Boolean.TRUE.equals(result)) {
                    log.info("✅ 规则匹配: {} -> 状态: {}", condition, rule.getStatus());
                    return rule;
                }
                
            } catch (Exception e) {
                log.error("❌ 评估规则失败: {} - {}", rule.getCondition(), e.getMessage());
                log.error("变量上下文: {}", variables);
            }
        }
        
        return null;
    }
    
    /**
     * 评估单个条件表达式
     * 
     * @param condition 条件表达式
     * @param variables 变量上下文
     * @return 评估结果，出错时返回false
     */
    public boolean evaluateCondition(String condition, Map<String, Object> variables) {
        try {
            StandardEvaluationContext context = new StandardEvaluationContext();
            
            // 设置根对象为 variables Map，这样可以直接使用变量名
            context.setRootObject(variables);
            
            // 将所有变量也注册为命名变量（支持 #variableName 语法）
            for (Map.Entry<String, Object> entry : variables.entrySet()) {
                context.setVariable(entry.getKey(), entry.getValue());
            }
            
            Expression expression = parser.parseExpression(condition);
            Boolean result = expression.getValue(context, Boolean.class);
            
            return Boolean.TRUE.equals(result);
            
        } catch (Exception e) {
            log.error("❌ 评估条件失败: {} - {}", condition, e.getMessage());
            log.error("变量上下文: {}", variables);
            return false;
        }
    }
}