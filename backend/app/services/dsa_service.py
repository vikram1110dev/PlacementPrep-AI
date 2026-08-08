from sqlalchemy.orm import Session
from app.repositories.dsa_repository import DSARepository
from app.services.judge0_service import Judge0Service
from app.models.dsa import SubmissionStatus
from app.schemas.dsa import ExecutionResult

class DSAService:
    def __init__(self, db: Session):
        self.repo = DSARepository(db)
        self.judge = Judge0Service()

    def get_problems(self, difficulty: str = None, category: str = None):
        return self.repo.get_problems(difficulty, category)
        
    def get_problem(self, problem_id: str):
        return self.repo.get_problem_by_id(problem_id)
        
    def get_sample_test_cases(self, problem_id: str):
        return self.repo.get_test_cases(problem_id, include_hidden=False)

    async def run_code(self, user_id: str, problem_id: str, language: str, code: str, test_case_id: str = None) -> ExecutionResult:
        problem = self.repo.get_problem_by_id(problem_id)
        if not problem:
            raise ValueError("Problem not found")

        # Get test cases (run against sample tests only)
        if test_case_id:
            test_cases = [self.repo.get_test_case_by_id(test_case_id)]
            if not test_cases[0] or test_cases[0].problem_id != problem_id:
                raise ValueError("Test case not found or does not belong to this problem")
        else:
            test_cases = self.repo.get_test_cases(problem_id, include_hidden=False)
            if not test_cases:
                raise ValueError("No sample test cases found for this problem")

        # Run against the first test case for simplicity in 'run'
        # In a full system, you would loop and return an array of results
        tc = test_cases[0]
        result = await self.judge.run_single_test(code, language, tc.input_data, tc.expected_output)

        return ExecutionResult(
            status=result.status_description,
            output=result.stdout,
            expected_output=tc.expected_output,
            execution_time=result.time,
            memory_usage=result.memory,
            error_message=result.compile_output or result.stderr,
            passed=(result.status_id == 3) # 3 is Accepted in Judge0
        )

    async def submit_code(self, user_id: str, problem_id: str, language: str, code: str) -> dict:
        problem = self.repo.get_problem_by_id(problem_id)
        if not problem:
            raise ValueError("Problem not found")

        # Submit runs against ALL test cases (including hidden)
        test_cases = self.repo.get_test_cases(problem_id, include_hidden=True)
        if not test_cases:
            raise ValueError("No test cases found for this problem")

        passed_count = 0
        total_time = 0.0
        max_memory = 0.0
        final_status = SubmissionStatus.ACCEPTED
        error_msg = None

        for tc in test_cases:
            result = await self.judge.run_single_test(code, language, tc.input_data, tc.expected_output)
            
            if result.time:
                total_time += result.time
            if result.memory and result.memory > max_memory:
                max_memory = result.memory

            if result.status_id == 3:
                passed_count += 1
            else:
                # Map Judge0 status to our enum
                mapping = {
                    4: SubmissionStatus.WRONG_ANSWER,
                    5: SubmissionStatus.TIME_LIMIT_EXCEEDED,
                    6: SubmissionStatus.COMPILATION_ERROR,
                    7: SubmissionStatus.RUNTIME_ERROR,
                    8: SubmissionStatus.RUNTIME_ERROR,
                    9: SubmissionStatus.RUNTIME_ERROR,
                    10: SubmissionStatus.RUNTIME_ERROR,
                    11: SubmissionStatus.RUNTIME_ERROR,
                    12: SubmissionStatus.RUNTIME_ERROR,
                }
                final_status = mapping.get(result.status_id, SubmissionStatus.UNKNOWN_ERROR)
                error_msg = result.compile_output or result.stderr
                # Break early on failure to prevent running remaining tests unnecessarily
                break

        # Save submission
        submission = self.repo.save_submission(
            user_id=user_id,
            problem_id=problem_id,
            language=language,
            code=code,
            status=final_status,
            passed_tests=passed_count,
            total_tests=len(test_cases),
            execution_time=total_time,
            memory_usage=max_memory,
            error_message=error_msg
        )

        return {
            "status": final_status.value,
            "passed_tests": passed_count,
            "total_tests": len(test_cases),
            "execution_time": total_time,
            "memory_usage": max_memory,
            "error_message": error_msg
        }

    def get_user_submissions(self, user_id: str):
        return self.repo.get_user_submissions(user_id)

    def get_submission(self, submission_id: str, user_id: str):
        return self.repo.get_submission_by_id(submission_id, user_id)

    def get_recommendations(self, user_id: str):
        return self.repo.get_recommendations(user_id)
