package com.application.ssh.project.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ImageMetadataDTO {
    private Long id;
    private String name;
    private String type;
    private long size;
    private LocalDateTime createdAt;
}

