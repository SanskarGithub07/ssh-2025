package com.application.ssh.project.client;

import com.application.ssh.project.dto.AnimalPredictionDTO;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.service.annotation.HttpExchange;
import org.springframework.web.service.annotation.PostExchange;

@HttpExchange()
public interface FlaskClient {
    @PostExchange(
            url = "/api/predict",
            contentType = MediaType.MULTIPART_FORM_DATA_VALUE
    )
    AnimalPredictionDTO getAnimalPrediction(@RequestPart("image") Resource file);
}
