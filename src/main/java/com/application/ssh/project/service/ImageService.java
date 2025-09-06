package com.application.ssh.project.service;

import com.application.ssh.project.entity.ImageData;
import com.application.ssh.project.repository.ImageDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@Service
public class ImageService {

    @Autowired
    private ImageDataRepository imageDataRepository;

    public ImageData uploadImage(MultipartFile file) throws IOException {
        ImageData imageData = new ImageData();
        imageData.setName(file.getOriginalFilename());
        imageData.setType(file.getContentType());
        imageData.setImageBytes(file.getBytes());
        return imageDataRepository.save(imageData);
    }

    public ImageData getImageById(Long id) {
        return imageDataRepository.findById(id).orElse(null);
    }
}