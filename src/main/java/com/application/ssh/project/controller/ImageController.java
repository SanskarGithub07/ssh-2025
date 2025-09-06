package com.application.ssh.project.controller;

import com.application.ssh.project.dto.AnimalPredictionDTO;
import com.application.ssh.project.entity.ImageData;
import com.application.ssh.project.service.ImageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/images")
public class ImageController {

    @Autowired
    private ImageService imageService;

    @PostMapping("/upload")
    public ResponseEntity<?> uploadImage(@RequestParam("file") MultipartFile file) {
        try {
            AnimalPredictionDTO prediction = imageService.uploadAndPredict(file);
            return ResponseEntity.ok(prediction);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to upload image.");
        }
    }

    @GetMapping("/{id}")
    public ResponseEntity<byte[]> getImage(@PathVariable Long id) {
        ImageData imageData = imageService.getImageById(id);
        if (imageData != null) {
            return ResponseEntity.ok()
                    .contentType(org.springframework.http.MediaType.valueOf(imageData.getType()))
                    .body(imageData.getImageBytes());
        }
        return ResponseEntity.notFound().build();
    }
}
