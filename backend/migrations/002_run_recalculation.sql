-- 002: source-data provenance and recalculation lineage on decision_runs.
-- Fresh databases get these columns from 001_initial.sql; this script upgrades an existing one.
-- Rows created before this upgrade keep empty source_fingerprint and are treated as never-stale
-- until a new run or recalculation records a fingerprint.

ALTER TABLE decision_runs
	ADD COLUMN source_fingerprint VARCHAR(64) NOT NULL DEFAULT '' AFTER error,
	ADD COLUMN source_signature JSON NULL AFTER source_fingerprint,
	ADD COLUMN recalc_of_id INTEGER NULL AFTER source_signature,
	ADD COLUMN recalc_seq INTEGER NOT NULL DEFAULT 0 AFTER recalc_of_id,
	ADD COLUMN recalc_status VARCHAR(20) NOT NULL DEFAULT '' AFTER recalc_seq,
	ADD CONSTRAINT fk_decision_runs_recalc_of FOREIGN KEY(recalc_of_id) REFERENCES decision_runs (id)
;
