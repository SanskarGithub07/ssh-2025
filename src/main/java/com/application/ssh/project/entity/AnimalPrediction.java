package com.application.ssh.project.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "animal_predictions")
@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class AnimalPrediction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String animalBiologicalClass;
    private String animalOrder;
    private String animalFamily;
    private String animalGenus;
    private String animalSpecies;
    private String animalCommonName;

    private double score;

    private double bboxX;
    private double bboxY;
    private double bboxWidth;
    private double bboxHeight;

    @OneToOne
    @JoinColumn(name = "image_id")
    private ImageData imageData;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }
}

