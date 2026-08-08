import json
import random
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.roadmap import Roadmap, RoadmapWeek, RoadmapTask
from app.schemas.roadmap import RoadmapSetupRequest, TaskStatusUpdateRequest
from app.services.analytics_service import AnalyticsService
from app.services.aptitude_service import AptitudeService
from app.agents.core import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

class RoadmapService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)
        self.aptitude_service = AptitudeService(db)
        self.llm = get_llm(temperature=0.3, streaming=False)

    def _analyze_user_profile(self, user_id: str):
        # 1. Get Analytics overview (for DSA/general progress)
        overview = self.analytics_service.get_dashboard_overview(user_id)
        
        # 2. Get Aptitude progress
        apt_progress = self.aptitude_service.get_user_progress(user_id)
        
        # We can also check interview history if needed, but for MVP we use basic thresholds
        dsa_solved = overview.questions_solved if hasattr(overview, 'questions_solved') else overview.get('questions_solved', 0)
        apt_accuracy = apt_progress.get('overall_accuracy', 0)
        apt_weakest = apt_progress.get('weakest_topic')
        
        profile = {
            "dsa_level": "beginner" if dsa_solved < 10 else "intermediate" if dsa_solved < 50 else "advanced",
            "aptitude_level": "beginner" if apt_accuracy < 40 else "intermediate" if apt_accuracy < 70 else "advanced",
            "aptitude_weak_topic": apt_weakest,
            "dsa_solved": dsa_solved,
            "aptitude_accuracy": float(apt_accuracy)
        }
        return profile

    def _generate_deterministic_tasks(self, profile: dict, request: RoadmapSetupRequest):
        tasks = []
        days_per_week = 5 # Assume 5 days of study per week
        total_days = request.duration_weeks * days_per_week
        
        # Determine focus splits based on profile
        # If aptitude accuracy is low, bias towards aptitude
        apt_weight = 0.4
        dsa_weight = 0.4
        interview_weight = 0.2
        
        if profile["aptitude_level"] == "beginner":
            apt_weight = 0.5
            dsa_weight = 0.3
        elif profile["dsa_level"] == "beginner":
            apt_weight = 0.3
            dsa_weight = 0.5
            
        topics_pool = {
            "Aptitude": ["Percentages", "Ratio", "Profit & Loss", "Time & Work", "Logical Reasoning"],
            "DSA": ["Arrays", "Strings", "Linked Lists", "Trees", "Dynamic Programming"],
            "Interview": ["OOP Fundamentals", "System Design Basics", "Behavioral STAR", "Mock Interview"]
        }
        
        if request.target_company:
            topics_pool["Company"] = [f"{request.target_company} Previous Questions", f"{request.target_company} Interview Patterns"]
            interview_weight -= 0.1
            company_weight = 0.1
        else:
            company_weight = 0.0

        for week in range(1, request.duration_weeks + 1):
            week_tasks = []
            for day in range(1, days_per_week + 1):
                rand_val = random.random()
                
                if rand_val < apt_weight:
                    category = "Aptitude"
                elif rand_val < apt_weight + dsa_weight:
                    category = "DSA"
                elif rand_val < apt_weight + dsa_weight + interview_weight:
                    category = "Interview"
                else:
                    category = "Company"
                
                # Pick a topic
                # If they have a weak topic, inject it frequently in week 1
                if category == "Aptitude" and week == 1 and profile["aptitude_weak_topic"]:
                    topic = profile["aptitude_weak_topic"]
                else:
                    topic = random.choice(topics_pool.get(category, ["General Practice"]))
                
                # Build Task
                week_tasks.append({
                    "day_number": day,
                    "topic": topic,
                    "activity": f"Practice {category} concepts: {topic}",
                    "estimated_time": request.daily_time_minutes,
                    "difficulty": "Medium",
                    "expected_outcome": f"Improve accuracy in {topic}."
                })
            tasks.append({
                "week_number": week,
                "focus_area": "Fundamentals" if week == 1 else "Advanced Practice",
                "tasks": week_tasks
            })
            
        return tasks

    def _generate_ai_summary(self, profile: dict, request: RoadmapSetupRequest):
        prompt = f"""You are a Placement Mentor. Based on the student's data, generate a 2-sentence encouraging summary of why their roadmap is structured this way.
Data:
- Target Role: {request.target_role}
- Target Company: {request.target_company or 'None'}
- DSA Questions Solved: {profile['dsa_solved']}
- Aptitude Accuracy: {profile['aptitude_accuracy']}%
- Weakest Aptitude Topic: {profile['aptitude_weak_topic'] or 'Unknown'}

Provide ONLY the summary string. No formatting or quotes."""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip().replace('"', '')
        except:
            return "This customized roadmap focuses on strengthening your core fundamentals based on your recent activity."

    def generate_roadmap(self, user_id: str, request: RoadmapSetupRequest) -> Roadmap:
        # Check for existing active roadmap and deactivate it
        existing = self.db.query(Roadmap).filter_by(user_id=user_id, is_active=True).first()
        version = 1
        if existing:
            existing.is_active = False
            version = existing.version + 1
            self.db.commit()

        # 1. Analyze profile
        profile = self._analyze_user_profile(user_id)
        
        # 2. Build deterministic tasks
        weeks_data = self._generate_deterministic_tasks(profile, request)
        
        # 3. AI Summary
        ai_summary = self._generate_ai_summary(profile, request)
        
        # 4. Persist
        roadmap = Roadmap(
            user_id=user_id,
            target_role=request.target_role,
            target_company=request.target_company,
            duration_weeks=request.duration_weeks,
            daily_time_minutes=request.daily_time_minutes,
            ai_recommendation_summary=ai_summary,
            version=version,
            is_active=True
        )
        self.db.add(roadmap)
        self.db.flush() # get ID
        
        for w_data in weeks_data:
            week = RoadmapWeek(
                roadmap_id=roadmap.id,
                week_number=w_data["week_number"],
                focus_area=w_data["focus_area"]
            )
            self.db.add(week)
            self.db.flush()
            
            for t_data in w_data["tasks"]:
                task = RoadmapTask(
                    week_id=week.id,
                    day_number=t_data["day_number"],
                    topic=t_data["topic"],
                    activity=t_data["activity"],
                    estimated_time=t_data["estimated_time"],
                    difficulty=t_data["difficulty"],
                    expected_outcome=t_data["expected_outcome"]
                )
                self.db.add(task)
                
        self.db.commit()
        self.db.refresh(roadmap)
        return roadmap

    def get_current_roadmap(self, user_id: str):
        roadmap = self.db.query(Roadmap).filter_by(user_id=user_id, is_active=True).first()
        if not roadmap:
            return None
            
        # Calculate progress
        total_tasks = 0
        completed_tasks = 0
        
        for w in roadmap.weeks:
            for t in w.tasks:
                total_tasks += 1
                if t.status == 'completed':
                    completed_tasks += 1
                    
        roadmap.total_tasks = total_tasks
        roadmap.tasks_completed = completed_tasks
        roadmap.completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return roadmap

    def get_roadmap_by_id(self, user_id: str, roadmap_id: str):
        roadmap = self.db.query(Roadmap).filter_by(id=roadmap_id, user_id=user_id).first()
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        return roadmap

    def update_task_status(self, user_id: str, task_id: str, status_req: TaskStatusUpdateRequest):
        task = self.db.query(RoadmapTask).filter(RoadmapTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        # Verify ownership
        roadmap = task.week.roadmap
        if roadmap.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
            
        task.status = status_req.status
        self.db.commit()
        return {"message": f"Task marked as {status_req.status}"}
