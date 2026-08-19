from methodbridge.contracts import EvaluationCase, ReadinessResult

def test_contracts_construct():
    case=EvaluationCase("x","f","p",("a",),("b",),True)
    assert case.bootstrap_executable
    assert ReadinessResult(False,["x"]).blockers == ["x"]
