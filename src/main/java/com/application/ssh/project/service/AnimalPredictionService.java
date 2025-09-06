package com.application.ssh.project.service;

import com.application.ssh.project.dto.AnimalPredictionDTO;
import com.application.ssh.project.entity.AnimalPrediction;
import com.application.ssh.project.repository.AnimalPredictionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AnimalPredictionService {

    private final AnimalPredictionRepository predictionRepository;

    public List<AnimalPredictionDTO> getAllPredictions() {
        return predictionRepository.findAll()
                .stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }

    public Optional<AnimalPredictionDTO> getPredictionById(Long id) {
        return predictionRepository.findById(id).map(this::mapToDTO);
    }

    private AnimalPredictionDTO mapToDTO(AnimalPrediction prediction) {
        return AnimalPredictionDTO.builder()
                .biologicalClass(prediction.getAnimalBiologicalClass())
                .order(prediction.getAnimalOrder())
                .family(prediction.getAnimalFamily())
                .genus(prediction.getAnimalGenus())
                .species(prediction.getAnimalSpecies())
                .commonName(prediction.getAnimalCommonName())
                .score(prediction.getScore())
                .bboxX(prediction.getBboxX())
                .bboxY(prediction.getBboxY())
                .bboxWidth(prediction.getBboxWidth())
                .bboxHeight(prediction.getBboxHeight())
                .predictionCreatedAt(prediction.getCreatedAt())
                .build();
    }
}

