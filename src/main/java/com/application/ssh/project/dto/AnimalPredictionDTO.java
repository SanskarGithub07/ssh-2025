package com.application.ssh.project.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class AnimalPredictionDTO {
    private String biologicalClass;   // mammalia
    private String order;             // carnivora
    private String family;            // ursidae
    private String genus;             // ursus
    private String species;           // americanus
    private String commonName;        // american black bear

    private double score;             // 0.9899

    // Bounding box coordinates (relative positions 0.0 - 1.0)
    private double bboxX;             // 0.4331
    private double bboxY;             // 0.4284
    private double bboxWidth;         // 0.3232
    private double bboxHeight;        // 0.3223
}

