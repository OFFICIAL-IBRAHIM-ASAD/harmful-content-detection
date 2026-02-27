package com.example.demo.controller;

import com.example.demo.model.ContentItem;
import com.example.demo.service.ModerationService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/content")
public class ContentController {

    private final ModerationService moderationService;

    public ContentController(ModerationService moderationService) {
        this.moderationService = moderationService;
    }

    @PostMapping("/submit")
    public ResponseEntity<ContentItem> submitContent(@RequestBody ContentItem item) {
        // Pass the incoming JSON payload to our Stage 1 Bouncer
        ContentItem processedItem = moderationService.processIncomingContent(item);
        return ResponseEntity.ok(processedItem);
    }
}