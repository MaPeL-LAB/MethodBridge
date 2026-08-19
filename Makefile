.PHONY: validate test dry-run readiness integrity hardware-contract evidence campaign claims prelocal release-check gate

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

campaign:
	python scripts/validate_local_model_campaign.py

claims:
	python scripts/validate_public_claims.py

prelocal: campaign claims
	python scripts/verify_local_model_handoff.py
	python -m pytest -q tests/model_engineering tests/governance/test_public_claims_gate.py

release-check:
	python scripts/prepare_model_release.py --check

test:
	python -m pytest -q

dry-run:
	python scripts/run_evaluation.py --dry-run

readiness:
	python scripts/verify_submission_readiness.py

gate: validate integrity hardware-contract evidence campaign claims dry-run test
