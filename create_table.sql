CREATE DATABASE professore;

-- Tabella professore
CREATE TABLE professore (
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

-- Tabella anno_scolastico
CREATE TABLE anno_scolastico (
    anno_scolastico VARCHAR(9) PRIMARY KEY
);

-- Tabella classe
CREATE TABLE classe (
    anno_scolastico VARCHAR(9) NOT NULL,
    anno INT NOT NULL,
    sezione CHAR(1) NOT NULL,
    PRIMARY KEY (anno_scolastico, anno, sezione),
    FOREIGN KEY (anno_scolastico) REFERENCES anno_scolastico(anno_scolastico)
);

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
    FOREIGN KEY (anno_scolastico) REFERENCES anno_scolastico(anno_scolastico),
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
    exam_duration int not null,
    validity_time int not null,
    test_id INT UNSIGNED NOT NULL,
    FOREIGN KEY (test_id) REFERENCES test(id)
);
-- Tabella test_alunno (relazione molti-a-molti tra alunno e codice di test)
CREATE TABLE test_alunno (
    alunno_username VARCHAR(50) NOT NULL,
    codice_id INT UNSIGNED NOT NULL,
    voto DECIMAL(5, 2),
    start_time datetime,
    submission_date datetime,
    PRIMARY KEY (alunno_username, codice_id),
    FOREIGN KEY (alunno_username) REFERENCES alunno(username) ON DELETE CASCADE,
    FOREIGN KEY (codice_id) REFERENCES codice(id) ON DELETE CASCADE
);

-- Tabella risposta (traccia le risposte di ciascun alunno a ogni domanda del test)
CREATE TABLE risposta (
    alunno_username VARCHAR(50) NOT NULL,
    codice_id INT UNSIGNED NOT NULL,
    domanda_id INT UNSIGNED NOT NULL,
    opzione_id INT UNSIGNED,
    ordine int,
    PRIMARY KEY (alunno_username, codice_id, domanda_id),
    FOREIGN KEY (alunno_username) REFERENCES alunno(username) ON DELETE CASCADE,
    FOREIGN KEY (codice_id) REFERENCES codice(id) ON DELETE CASCADE,
    FOREIGN KEY (domanda_id) REFERENCES domanda(id) ON DELETE CASCADE,
    FOREIGN KEY (opzione_id) REFERENCES opzione(id) ON DELETE CASCADE
);



CREATE VIEW student_grades AS
SELECT 
    al.nome AS nome_studente,
    al.cognome AS cognome_studente,
    al.anno_scolastico,
    al.anno,
    al.sezione,
    cd.id AS codice_id,
    cd.test_id AS test_id,
    ta.submission_date AS submission_date,
    COUNT(CASE WHEN op.vero = TRUE AND rsp.opzione_id IS NOT NULL THEN 1 END) AS risposte_corrette,
    COUNT(CASE WHEN op.vero = FALSE AND rsp.opzione_id IS NOT NULL THEN 1 END) AS risposte_errate,
    COUNT(dm.id) - COUNT(rsp.domanda_id) AS risposte_non_date,
    COALESCE(SUM(CASE WHEN op.vero = TRUE THEN op.valore ELSE 0 END), 0) AS punteggio,
    COUNT(DISTINCT rsp.domanda_id) AS punteggio_massimo
FROM 
    alunno al
JOIN 
    test_alunno ta ON al.username = ta.alunno_username
JOIN 
    codice cd ON ta.codice_id = cd.id
JOIN 
    domanda dm ON dm.test_id = cd.test_id
LEFT JOIN 
    risposta rsp ON rsp.alunno_username = al.username AND rsp.codice_id = cd.id AND rsp.domanda_id = dm.id
LEFT JOIN 
    opzione op ON rsp.opzione_id = op.id
GROUP BY 
    al.nome, al.cognome, al.anno_scolastico, al.anno, al.sezione, cd.id, cd.test_id, ta.submission_date;
