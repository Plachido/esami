CREATE DATABASE professore;

-- Tabella professore
CREATE TABLE professore (
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

-- Tabella classe
CREATE TABLE classe (
    anno_scolastico VARCHAR(9) NOT NULL,
    anno INT NOT NULL,
    sezione CHAR(1) NOT NULL,
    PRIMARY KEY (anno_scolastico, anno, sezione)
);

-- Tabella insegna (relazione molti-a-molti tra professore e classe)
CREATE TABLE insegna (
    professore_username VARCHAR(50) NOT NULL,
    anno_scolastico VARCHAR(9) NOT NULL,
    anno INT NOT NULL,
    sezione CHAR(1) NOT NULL,
    FOREIGN KEY (professore_username) REFERENCES professore(username),
    FOREIGN KEY (anno_scolastico, anno, sezione) REFERENCES classe(anno_scolastico, anno, sezione),
    PRIMARY KEY (professore_username, anno_scolastico, anno, sezione)
);

-- Tabella alunno
CREATE TABLE alunno (
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    anno_scolastico VARCHAR(9),
    anno INT,
    sezione CHAR(1),
    FOREIGN KEY (anno_scolastico, anno, sezione) REFERENCES classe(anno_scolastico, anno, sezione)
);

-- Tabella test
CREATE TABLE test (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    professore_username VARCHAR(50) NOT NULL,
    FOREIGN KEY (professore_username) REFERENCES professore(username)
);

-- Tabella domanda (associata a test)
CREATE TABLE domanda (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    testo TEXT NOT NULL,
    test_id INT UNSIGNED NOT NULL,
    FOREIGN KEY (test_id) REFERENCES test(id)
);

-- Tabella opzione (associata a domanda)
CREATE TABLE opzione (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    testo TEXT NOT NULL,
    vero BOOLEAN NOT NULL,
    valore INT,
    domanda_id INT UNSIGNED NOT NULL,
    FOREIGN KEY (domanda_id) REFERENCES domanda(id)
);

-- Tabella codice (per generare istanze di un test)
CREATE TABLE codice (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    data_generazione DATE NOT NULL,
    test_id INT UNSIGNED NOT NULL,
    FOREIGN KEY (test_id) REFERENCES test(id)
);

-- Tabella test_alunno (relazione molti-a-molti tra alunno e codice di test)
CREATE TABLE test_alunno (
    alunno_username VARCHAR(50) NOT NULL,
    codice_id INT UNSIGNED NOT NULL,
    voto DECIMAL(5, 2),
    PRIMARY KEY (alunno_username, codice_id),
    FOREIGN KEY (alunno_username) REFERENCES alunno(username),
    FOREIGN KEY (codice_id) REFERENCES codice(id)
);

-- Tabella risposta (traccia le risposte di ciascun alunno a ogni domanda del test)
CREATE TABLE risposta (
    alunno_username VARCHAR(50) NOT NULL,
    codice_id INT UNSIGNED NOT NULL,
    domanda_id INT UNSIGNED NOT NULL,
    opzione_id INT UNSIGNED,
    PRIMARY KEY (alunno_username, codice_id, domanda_id),
    FOREIGN KEY (alunno_username) REFERENCES alunno(username),
    FOREIGN KEY (codice_id) REFERENCES codice(id),
    FOREIGN KEY (domanda_id) REFERENCES domanda(id),
    FOREIGN KEY (opzione_id) REFERENCES opzione(id)
);
