.PHONY: validate test dry-run readiness

validate:
	python scripts/validate_repository.py
	python scripts/validate_sources.py
	python scripts/validate_dataset.py
	python scripts/detect_train_eval_leakage.py

test:
	python -m pytest -q

dry-run:
	python scripts/run_evaluation.py --dry-run

readiness:
	python scripts/verify_submission_readiness.py
