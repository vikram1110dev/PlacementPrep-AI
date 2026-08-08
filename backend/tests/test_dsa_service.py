import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.dsa_service import DSAService
from app.services.judge0_service import Judge0Result
from app.models.dsa import SubmissionStatus

@pytest.mark.asyncio
async def test_run_code():
    # Mock dependencies
    db_mock = MagicMock()
    service = DSAService(db_mock)
    
    # Mock Repository
    mock_problem = MagicMock()
    mock_problem.id = "123"
    service.repo.get_problem_by_id = MagicMock(return_value=mock_problem)
    
    mock_tc = MagicMock()
    mock_tc.id = "tc1"
    mock_tc.input_data = "1 2"
    mock_tc.expected_output = "3"
    service.repo.get_test_cases = MagicMock(return_value=[mock_tc])

    # Mock Judge0
    service.judge.run_single_test = AsyncMock(return_value=Judge0Result(
        status_id=3,
        status_description="Accepted",
        stdout="3\n",
        time=0.012,
        memory=15.4
    ))
    
    result = await service.run_code("user1", "123", "python", "print(3)")
    
    assert result.passed is True
    assert result.status == "Accepted"
    assert result.execution_time == 0.012

@pytest.mark.asyncio
async def test_submit_code():
    db_mock = MagicMock()
    service = DSAService(db_mock)
    
    # Mock Repository
    mock_problem = MagicMock()
    mock_problem.id = "123"
    service.repo.get_problem_by_id = MagicMock(return_value=mock_problem)
    
    mock_tc1 = MagicMock()
    mock_tc1.id = "tc1"
    
    mock_tc2 = MagicMock()
    mock_tc2.id = "tc2"
    
    service.repo.get_test_cases = MagicMock(return_value=[mock_tc1, mock_tc2])
    
    service.repo.save_submission = MagicMock()

    # Mock Judge0
    # First returns Accepted, Second returns Wrong Answer
    service.judge.run_single_test = AsyncMock(side_effect=[
        Judge0Result(status_id=3, status_description="Accepted", time=0.01, memory=10.0),
        Judge0Result(status_id=4, status_description="Wrong Answer", time=0.01, memory=10.0),
    ])
    
    res = await service.submit_code("user1", "123", "python", "code")
    
    assert res["passed_tests"] == 1
    assert res["total_tests"] == 2
    assert res["status"] == SubmissionStatus.WRONG_ANSWER.value
    
    # Verify save_submission was called
    service.repo.save_submission.assert_called_once()
