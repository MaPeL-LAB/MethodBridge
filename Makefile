.PHONY: validate test dry-run readiness integrity gate

validate:
	python scripts/validate_repository.py
	python scripts/validate_sources.py
	python scripts/validate_dataset.py
	python scripts/detect_train_eval_leakage.py

integrity:
	python scripts/validate_markdown_links.py

test:
	python -m pytest -q

dry-run:
	python scripts/run_evaluation.py --dry-run

readiness:
	python scripts/verify_submission_readiness.py

gate: validate integrity dry-run test
