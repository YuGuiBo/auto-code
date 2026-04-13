package com.example.flowable.dynamic.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.io.IOException;
import java.nio.file.*;
import java.util.concurrent.TimeUnit;

/**
 * 流程配置文件监听器
 * 实现热更新功能 - 监听配置文件变化并自动重新加载
 * 
 * @author Auto-Code Platform
 */
@Slf4j
@Component
public class ProcessConfigWatcher {
    
    @Autowired
    private ProcessConfigLoader configLoader;
    
    private WatchService watchService;
    private Thread watchThread;
    private volatile boolean running = true;
    
    @PostConstruct
    public void init() {
        try {
            // 获取配置目录路径（现在配置文件在processes目录及其子目录中）
            Path configPath = Paths.get("src/main/resources/processes");
            
            // 如果是打包后的环境，尝试使用 classpath
            if (!Files.exists(configPath)) {
                log.warn("开发环境配置目录不存在，热更新功能将不可用");
                log.info("生产环境请使用 Actuator 的 /refresh 端点进行配置更新");
                return;
            }
            
            // 创建监听服务
            watchService = FileSystems.getDefault().newWatchService();
            
            // 递归注册所有子目录
            registerRecursive(configPath);
            
            // 启动监听线程
            startWatching();
            
            log.info("✅ 配置文件热更新监听已启动: {}", configPath);
            
        } catch (IOException e) {
            log.error("❌ 启动配置文件监听失败", e);
        }
    }
    
    /**
     * 递归注册目录及其所有子目录
     */
    private void registerRecursive(Path path) throws IOException {
        // 注册当前目录
        path.register(watchService,
            StandardWatchEventKinds.ENTRY_CREATE,
            StandardWatchEventKinds.ENTRY_MODIFY,
            StandardWatchEventKinds.ENTRY_DELETE);
        
        // 递归注册所有子目录
        try (var stream = Files.walk(path, 10)) {
            stream.filter(Files::isDirectory)
                  .forEach(dir -> {
                      try {
                          dir.register(watchService,
                              StandardWatchEventKinds.ENTRY_CREATE,
                              StandardWatchEventKinds.ENTRY_MODIFY,
                              StandardWatchEventKinds.ENTRY_DELETE);
                      } catch (IOException e) {
                          log.error("❌ 注册监听目录失败: {}", dir, e);
                      }
                  });
        }
    }
    
    /**
     * 启动监听线程
     */
    private void startWatching() {
        watchThread = new Thread(() -> {
            log.info("配置文件监听线程已启动");
            
            while (running) {
                try {
                    WatchKey key = watchService.poll(3, TimeUnit.SECONDS);
                    
                    if (key == null) {
                        continue;
                    }
                    
                    for (WatchEvent<?> event : key.pollEvents()) {
                        WatchEvent.Kind<?> kind = event.kind();
                        
                        if (kind == StandardWatchEventKinds.OVERFLOW) {
                            continue;
                        }
                        
                        Path filename = (Path) event.context();
                        String fileStr = filename.toString();
                        
                        // 只处理 .yml 或 .yaml 文件
                        if (fileStr.endsWith(".yml") || fileStr.endsWith(".yaml")) {
                            log.info("🔍 检测到配置文件变化: {} - {}", kind.name(), fileStr);
                            
                            // 延迟一小段时间，避免文件还在写入
                            Thread.sleep(500);
                            
                            // 重新加载配置
                            configLoader.reloadConfigs();
                            
                            log.info("✅ 配置已自动更新");
                        }
                    }
                    
                    key.reset();
                    
                } catch (InterruptedException e) {
                    log.info("配置文件监听线程被中断");
                    break;
                } catch (Exception e) {
                    log.error("❌ 处理配置文件变化时出错", e);
                }
            }
            
            log.info("配置文件监听线程已停止");
        }, "process-config-watcher");
        
        watchThread.setDaemon(true);
        watchThread.start();
    }
    
    /**
     * 停止监听
     */
    @PreDestroy
    public void destroy() {
        running = false;
        
        if (watchService != null) {
            try {
                watchService.close();
            } catch (IOException e) {
                log.error("❌ 关闭配置文件监听服务失败", e);
            }
        }
        
        if (watchThread != null) {
            watchThread.interrupt();
        }
        
        log.info("配置文件监听已停止");
    }
}
