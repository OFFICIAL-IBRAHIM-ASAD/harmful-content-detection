package com.example.demo.service;

import com.example.demo.model.ContentItem;
import com.example.demo.repository.ContentItemRepository;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class ModerationService {

    private final ContentItemRepository repository;
    private final StringRedisTemplate redisTemplate;
    
    // Initialize it directly instead of asking Spring to inject it
    private final ObjectMapper objectMapper = new ObjectMapper();

    // A simulated list of known adversarial botnet IPs
    private final List<String> blacklistedIps = List.of("192.168.1.99", "10.0.0.5", "172.16.0.42");

    // We removed ObjectMapper from this constructor
    public ModerationService(ContentItemRepository repository, StringRedisTemplate redisTemplate) {
        this.repository = repository;
        this.redisTemplate = redisTemplate;
    }

    public ContentItem processIncomingContent(ContentItem item) {
        // 1. Assign timestamp upon arrival
        item.setTimestamp(LocalDateTime.now());

        // 2. Metadata Heuristic Check (Stage 1)
        if (item.getIpAddress() != null && blacklistedIps.contains(item.getIpAddress())) {
            item.setStatus("AUTO_DROPPED");
            System.out.println("🚨 STAGE 1 ALERT: Content dropped from known bad IP: " + item.getIpAddress());
            return repository.save(item); // Save and stop here. Do NOT send to Redis.
        }

        item.setStatus("PENDING_STAGE_2");
        System.out.println("✅ STAGE 1 PASS: Content accepted, routing to Stage 2...");
        
        // 3. Save the valid record to PostgreSQL
        ContentItem savedItem = repository.save(item);

        // 4. Push to Redis Queue for the Python ML Service
        try {
            // objectMapper is now ready to use!
            String message = objectMapper.writeValueAsString(savedItem);
            redisTemplate.opsForList().rightPush("stage2-fasttext-queue", message);
            System.out.println("🚀 REDIS: Successfully pushed item ID " + savedItem.getId() + " to the fastText queue!");
        } catch (Exception e) {
            System.err.println("❌ REDIS ERROR: Failed to push to queue: " + e.getMessage());
        }

        return savedItem;
    }
}