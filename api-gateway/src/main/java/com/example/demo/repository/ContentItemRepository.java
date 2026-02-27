package com.example.demo.repository;

import com.example.demo.model.ContentItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ContentItemRepository extends JpaRepository<ContentItem, Long> {
    // Spring Boot automatically writes the basic CRUD operations for us!
}