package com.application.ssh.project.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "image_data")
@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ImageData {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String type;

    @Lob // For large objects, store as BLOB/LONGBLOB
    @Column(name = "image_bytes", length = 100000)
    private byte[] imageBytes;

    @OneToOne(mappedBy = "imageData", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private AnimalPrediction prediction;
}
