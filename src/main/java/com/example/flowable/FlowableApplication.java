package com.example.flowable;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Flowable Demo 应用启动类
 * 
 * @author Generated
 * @date 2026-03-11
 */
@SpringBootApplication
public class FlowableApplication {

    public static void main(String[] args) {
        SpringApplication.run(FlowableApplication.class, args);
        System.out.println("\n========================================");
        System.out.println("Flowable Demo Application Started!");
        System.out.println("访问地址: http://localhost:8080");
        System.out.println("========================================\n");
    }
}