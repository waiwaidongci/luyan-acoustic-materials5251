
CREATE TABLE audits (
	id INTEGER NOT NULL AUTO_INCREMENT,
	actor VARCHAR(160) NOT NULL,
	action VARCHAR(180) NOT NULL,
	status_code INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id)
)

;


CREATE TABLE candidate_studies (
	id INTEGER NOT NULL AUTO_INCREMENT,
	code VARCHAR(40) NOT NULL,
	name VARCHAR(140) NOT NULL,
	context VARCHAR(1000) NOT NULL,
	source_file VARCHAR(140) NOT NULL,
	material_ids JSON NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (code)
)

;


CREATE TABLE material_samples (
	id INTEGER NOT NULL AUTO_INCREMENT,
	code VARCHAR(40) NOT NULL,
	name VARCHAR(100) NOT NULL,
	family VARCHAR(100) NOT NULL,
	absorption DOUBLE NOT NULL,
	impact DOUBLE NOT NULL,
	carbon DOUBLE NOT NULL,
	price DOUBLE NOT NULL,
	thickness DOUBLE NOT NULL,
	batch VARCHAR(100) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (code)
)

;


CREATE TABLE users (
	id INTEGER NOT NULL AUTO_INCREMENT,
	email VARCHAR(160) NOT NULL,
	name VARCHAR(80) NOT NULL,
	`role` VARCHAR(20) NOT NULL,
	password_hash VARCHAR(250) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (email)
)

;


CREATE TABLE criteria (
	id INTEGER NOT NULL AUTO_INCREMENT,
	study_id INTEGER NOT NULL,
	code VARCHAR(30) NOT NULL,
	name VARCHAR(100) NOT NULL,
	unit VARCHAR(50) NOT NULL,
	direction VARCHAR(20) NOT NULL,
	center_weight DOUBLE NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (study_id, code),
	FOREIGN KEY(study_id) REFERENCES candidate_studies (id)
)

;


CREATE TABLE decision_runs (
	id INTEGER NOT NULL AUTO_INCREMENT,
	name VARCHAR(140) NOT NULL,
	study_id INTEGER NOT NULL,
	center_weights JSON NOT NULL,
	concentration DOUBLE NOT NULL,
	repeats INTEGER NOT NULL,
	seed INTEGER NOT NULL,
	status VARCHAR(20) NOT NULL,
	snapshot JSON NOT NULL,
	summary JSON NOT NULL,
	result JSON NOT NULL,
	error VARCHAR(600) NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (name),
	FOREIGN KEY(study_id) REFERENCES candidate_studies (id)
)

;


CREATE TABLE trial_notes (
	id INTEGER NOT NULL AUTO_INCREMENT,
	name VARCHAR(140) NOT NULL,
	run_id INTEGER NOT NULL,
	sample_id INTEGER NOT NULL,
	protocol VARCHAR(1800) NOT NULL,
	status VARCHAR(20) NOT NULL,
	reviewer_note VARCHAR(1000) NOT NULL,
	reviewed_by VARCHAR(140) NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (name),
	FOREIGN KEY(run_id) REFERENCES decision_runs (id),
	FOREIGN KEY(sample_id) REFERENCES material_samples (id)
)

;
