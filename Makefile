.PHONY: validate test dry-run readiness integrity hardware-contract evidence gate

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

evidence:
	python scripts/validate_model_evidence_boundary.py
	python -m pytest -q tests/inference tests/governance/test_model_evidence_status.py

test:
	python -m pytest -q

dry-run:
	python scripts/run_evaluation.py --dry-run

readiness:
	python scripts/verify_submission_readiness.py

gate: validate integrity hardware-contract evidence dry-run test
