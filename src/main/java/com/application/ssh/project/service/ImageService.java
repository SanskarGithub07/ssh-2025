package com.application.ssh.project.service;

import com.application.ssh.project.client.FlaskClient;
import com.application.ssh.project.dto.AnimalPredictionDTO;
import com.application.ssh.project.entity.AnimalPrediction;
import com.application.ssh.project.entity.ImageData;
import com.application.ssh.project.repository.AnimalPredictionRepository;
import com.application.ssh.project.repository.ImageDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@Service
public class ImageService {

    @Autowired
    private ImageDataRepository imageDataRepository;

    @Autowired
    private AnimalPredictionRepository predictionRepository;

    @Autowired
    private FlaskClient flaskClient;

    public AnimalPredictionDTO uploadAndPredict(MultipartFile file) throws IOException {
        ImageData imageData = new ImageData();
        imageData.setName(file.getOriginalFilename());
        imageData.setType(file.getContentType());
        imageData.setImageBytes(file.getBytes());
        imageData = imageDataRepository.save(imageData);

        ByteArrayResource resource = new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return file.getOriginalFilename();
            }
        };

        AnimalPredictionDTO dto = flaskClient.getAnimalPrediction(resource);

        AnimalPrediction prediction = AnimalPrediction.builder()
                .animalBiologicalClass(dto.getBiologicalClass())
                .animalOrder(dto.getOrder())
                .animalFamily(dto.getFamily())
                .animalGenus(dto.getGenus())
                .animalSpecies(dto.getSpecies())
                .animalCommonName(dto.getCommonName())
                .score(dto.getScore())
                .bboxX(dto.getBboxX())
                .bboxY(dto.getBboxY())
                .bboxWidth(dto.getBboxWidth())
                .bboxHeight(dto.getBboxHeight())
                .imageData(imageData)
                .build();

        predictionRepository.save(prediction);

        return dto;
    }

    public ImageData getImageById(Long id) {
        return imageDataRepository.findById(id).orElse(null);
    }
}
