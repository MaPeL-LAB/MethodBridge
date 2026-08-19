PROTECTED_DECISIONS = {
    "primary_user", "adtc_domain", "cross_disciplinary_pairing",
    "contribution_boundary", "held_out_split", "human_authority",
    "final_model", "final_quantization", "public_prompts",
    "submission_authorization",
}


def requires_human_approval(decision: str) -> bool:
    return decision in PROTECTED_DECISIONS
