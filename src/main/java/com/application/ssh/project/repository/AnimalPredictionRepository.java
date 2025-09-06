package com.application.ssh.project.repository;

import com.application.ssh.project.entity.AnimalPrediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AnimalPredictionRepository extends JpaRepository<AnimalPrediction, Long> {
}
