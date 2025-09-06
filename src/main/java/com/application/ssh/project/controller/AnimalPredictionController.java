package com.application.ssh.project.controller;

import com.application.ssh.project.dto.AnimalPredictionDTO;
import com.application.ssh.project.service.AnimalPredictionService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/prediction")
@RequiredArgsConstructor
public class AnimalPredictionController {
    private final AnimalPredictionService predictionService;

    @GetMapping("/")
    public ResponseEntity<List<AnimalPredictionDTO>> getAllPredictions() {
        return ResponseEntity.ok(predictionService.getAllPredictions());
    }

    @GetMapping("/{id}")
    public ResponseEntity<AnimalPredictionDTO> getPredictionById(@PathVariable Long id) {
        return predictionService.getPredictionById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
