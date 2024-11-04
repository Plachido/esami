-- MySQL Script generated by MySQL Workbench
-- Mon Nov  4 20:25:26 2024
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema professore
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema professore
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `professore` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `professore` ;

-- -----------------------------------------------------
-- Table `professore`.`classe`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`classe` (
  `anno_scolastico` VARCHAR(9) NOT NULL,
  `anno` INT NOT NULL,
  `sezione` CHAR(1) NOT NULL,
  PRIMARY KEY (`anno_scolastico`, `anno`, `sezione`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `professore`.`alunno`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`alunno` (
  `nome` VARCHAR(50) NOT NULL,
  `cognome` VARCHAR(50) NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `anno_scolastico` VARCHAR(9) NULL DEFAULT NULL,
  `anno` INT NULL DEFAULT NULL,
  `sezione` CHAR(1) NULL DEFAULT NULL,
  PRIMARY KEY (`username`),
  INDEX `anno_scolastico` (`anno_scolastico` ASC, `anno` ASC, `sezione` ASC) VISIBLE,
  CONSTRAINT `alunno_ibfk_1`
    FOREIGN KEY (`anno_scolastico` , `anno` , `sezione`)
    REFERENCES `professore`.`classe` (`anno_scolastico` , `anno` , `sezione`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `professore`.`amministratore`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`amministratore` (
  `nome` VARCHAR(50) NOT NULL,
  `cognome` VARCHAR(50) NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`username`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `professore`.`professore`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`professore` (
  `nome` VARCHAR(50) NOT NULL,
  `cognome` VARCHAR(50) NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`username`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `professore`.`test`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`test` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `professore_username` VARCHAR(50) NOT NULL,
  `descrizione` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `professore_username` (`professore_username` ASC) VISIBLE,
  CONSTRAINT `test_ibfk_1`
    FOREIGN KEY (`professore_username`)
    REFERENCES `professore`.`professore` (`username`))
ENGINE = InnoDB
AUTO_INCREMENT = 37
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `professore`.`codice`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`codice` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `data_generazione` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `test_id` INT UNSIGNED NOT NULL,
  `exam_duration` INT NULL DEFAULT NULL,
  `validity_time` INT NULL DEFAULT NULL,
  `stopped` TINYINT(1) NULL DEFAULT '0',
  `active` TINYINT(1) NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  INDEX `test_id` (`test_id` ASC) VISIBLE,
  CONSTRAINT `codice_ibfk_1`
    FOREIGN KEY (`test_id`)
    REFERENCES `professore`.`test` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 58
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `professore`.`domanda`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`domanda` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `testo` TEXT NOT NULL,
  `test_id` INT UNSIGNED NOT NULL,
  `active` TINYINT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  INDEX `test_id` (`test_id` ASC) VISIBLE,
  CONSTRAINT `domanda_ibfk_1`
    FOREIGN KEY (`test_id`)
    REFERENCES `professore`.`test` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 9
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `professore`.`insegna`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`insegna` (
  `professore_username` VARCHAR(50) NOT NULL,
  `anno_scolastico` VARCHAR(9) NOT NULL,
  `anno` INT NOT NULL,
  `sezione` CHAR(1) NOT NULL,
  PRIMARY KEY (`professore_username`, `anno_scolastico`, `anno`, `sezione`),
  INDEX `anno_scolastico` (`anno_scolastico` ASC, `anno` ASC, `sezione` ASC) VISIBLE,
  CONSTRAINT `insegna_ibfk_1`
    FOREIGN KEY (`professore_username`)
    REFERENCES `professore`.`professore` (`username`),
  CONSTRAINT `insegna_ibfk_2`
    FOREIGN KEY (`anno_scolastico` , `anno` , `sezione`)
    REFERENCES `professore`.`classe` (`anno_scolastico` , `anno` , `sezione`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `professore`.`opzione`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`opzione` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `testo` TEXT NOT NULL,
  `vero` TINYINT(1) NOT NULL,
  `valore` INT NULL DEFAULT NULL,
  `domanda_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `domanda_id` (`domanda_id` ASC) VISIBLE,
  CONSTRAINT `opzione_ibfk_1`
    FOREIGN KEY (`domanda_id`)
    REFERENCES `professore`.`domanda` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 19
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `professore`.`risposta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`risposta` (
  `alunno_username` VARCHAR(50) NOT NULL,
  `codice_id` INT UNSIGNED NOT NULL,
  `domanda_id` INT UNSIGNED NOT NULL,
  `opzione_id` INT UNSIGNED NULL DEFAULT NULL,
  `ordine` INT NULL DEFAULT NULL,
  PRIMARY KEY (`alunno_username`, `codice_id`, `domanda_id`),
  INDEX `codice_id` (`codice_id` ASC) VISIBLE,
  INDEX `domanda_id` (`domanda_id` ASC) VISIBLE,
  INDEX `opzione_id` (`opzione_id` ASC) VISIBLE,
  CONSTRAINT `risposta_ibfk_1`
    FOREIGN KEY (`alunno_username`)
    REFERENCES `professore`.`alunno` (`username`),
  CONSTRAINT `risposta_ibfk_2`
    FOREIGN KEY (`codice_id`)
    REFERENCES `professore`.`codice` (`id`),
  CONSTRAINT `risposta_ibfk_3`
    FOREIGN KEY (`domanda_id`)
    REFERENCES `professore`.`domanda` (`id`),
  CONSTRAINT `risposta_ibfk_4`
    FOREIGN KEY (`opzione_id`)
    REFERENCES `professore`.`opzione` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `professore`.`session`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`session` (
  `session_id` VARCHAR(255) NOT NULL,
  `user_id` VARCHAR(50) NOT NULL,
  `test_id` INT UNSIGNED NULL DEFAULT NULL,
  `active` TINYINT(1) NULL DEFAULT '1',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`session_id`),
  INDEX `user_id` (`user_id` ASC) VISIBLE,
  INDEX `test_id` (`test_id` ASC) VISIBLE,
  CONSTRAINT `session_ibfk_1`
    FOREIGN KEY (`user_id`)
    REFERENCES `professore`.`professore` (`username`),
  CONSTRAINT `session_ibfk_2`
    FOREIGN KEY (`test_id`)
    REFERENCES `professore`.`test` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `professore`.`test_alunno`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `professore`.`test_alunno` (
  `alunno_username` VARCHAR(50) NOT NULL,
  `codice_id` INT UNSIGNED NOT NULL,
  `voto` DECIMAL(5,2) NULL DEFAULT NULL,
  `start_time` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `submission_date` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`alunno_username`, `codice_id`),
  INDEX `codice_id` (`codice_id` ASC) VISIBLE,
  CONSTRAINT `test_alunno_ibfk_1`
    FOREIGN KEY (`alunno_username`)
    REFERENCES `professore`.`alunno` (`username`),
  CONSTRAINT `test_alunno_ibfk_2`
    FOREIGN KEY (`codice_id`)
    REFERENCES `professore`.`codice` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;