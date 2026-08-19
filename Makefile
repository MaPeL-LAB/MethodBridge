.PHONY: validate test dry-run readiness integrity hardware-contract gate

validate:
	python scripts/validate_repository.py
	python scripts/validate_sources.py
	python scripts/validate_dataset.py
	python scripts/detect_train_eval_leakage.py

integrity:
	python scripts/validate_markdown_links.py

hardware-contract:
	python scripts/check_adtc_host.py
	python -m pytest -q tests/hardware
	bash -n scripts/run_adtc_simulated_profile.sh
	bash -n scripts/run_adtc_reference_profile.sh
	bash -n scripts/capture_adtc_hardware_evidence.sh

test:
	python -m pytest -q

dry-run:
	python scripts/run_evaluation.py --dry-run

readiness:
	python scripts/verify_submission_readiness.py

gate: validate integrity hardware-contract dry-run test
