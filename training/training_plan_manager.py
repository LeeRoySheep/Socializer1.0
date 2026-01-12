"""
Training Plan Manager - Adaptive Personalized Learning System

LOCATION: training/training_plan_manager.py
PURPOSE: Manage automatic training plans with personalized learning adaptation

KEY FEATURES:
    1. SUBCONSCIOUS TRAINING: Basic skills taught subtly through natural conversation
    2. WEB RESEARCH: Fetches up-to-date best practices from internet on demand
    3. ADAPTIVE LEARNING: Adjusts approach based on user's learning style
    4. PERSONALIZATION: Everyone learns differently - system adapts to individual

LEARNING STYLES SUPPORTED:
    - Visual: Uses examples, scenarios, imagery
    - Auditory: Explains concepts verbally, uses dialogue
    - Kinesthetic: Hands-on practice, exercises, role-play
    - Reading/Writing: Provides written explanations, notes
    - Adaptive: System automatically detects best approach

DESIGN PRINCIPLES:
    - OOP: Clean separation of concerns, single responsibility
    - Test-Driven: All features tested before deployment
    - Documented: Comprehensive docstrings and comments

AUTHOR: Socializer Development Team
DATE: 2024-12-16
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from datamanager.data_manager import DataManager
from datamanager.data_model import User, Training, UserSkill, Skill
from memory.secure_memory_manager import SecureMemoryManager
from app.ote_logger import get_logger

# Web search for up-to-date best practices
try:
    from langchain_tavily import TavilySearch
    tavily_search = TavilySearch(max_results=5)
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    tavily_search = None

logger = get_logger()


# =============================================================================
# LEARNING STYLE DEFINITIONS
# =============================================================================

class LearningStyle:
    """
    Enumeration of supported learning styles.
    
    Each person learns differently. This system detects and adapts to:
    - VISUAL: Learns through seeing, examples, diagrams, scenarios
    - AUDITORY: Learns through listening, dialogue, verbal explanations
    - KINESTHETIC: Learns through doing, practice, role-play, exercises
    - READING_WRITING: Learns through reading, writing, note-taking
    - ADAPTIVE: System automatically detects and combines styles
    
    Attributes:
        STYLE_PROMPTS: Dict mapping style to AI prompt instructions
    """
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    ADAPTIVE = "adaptive"  # Default: system detects best approach
    
    # Learning style characteristics for AI prompt generation
    STYLE_PROMPTS = {
        "visual": (
            "Use vivid scenarios and examples. "
            "Paint pictures with words. "
            "Describe situations the user can visualize."
        ),
        "auditory": (
            "Explain concepts through dialogue. "
            "Use conversational teaching style. "
            "Ask questions and engage in discussion."
        ),
        "kinesthetic": (
            "Provide hands-on exercises and practice scenarios. "
            "Give role-play situations. "
            "Let user practice and get feedback."
        ),
        "reading_writing": (
            "Provide clear written explanations. "
            "Offer structured information. "
            "Give tips they can remember and apply."
        ),
        "adaptive": (
            "Observe how the user responds and adapt your teaching style. "
            "Try different approaches (examples, exercises, explanations) "
            "and use what works best for this individual."
        )
    }


class TrainingPlanManager:
    """
    Manages automatic training plans with adaptive personalized learning.
    
    This class implements a sophisticated training system that:
    
    1. SUBCONSCIOUS TRAINING:
       - Basic skills (empathy, active listening) taught subtly
       - Training feels like natural, helpful conversation
       - No explicit "lesson" feel unless user asks for it
    
    2. WEB RESEARCH INTEGRATION:
       - Fetches latest training best practices from internet
       - Keeps training approaches up-to-date
       - Adapts to current research findings
    
    3. ADAPTIVE LEARNING:
       - Detects user's preferred learning style
       - Adjusts teaching approach based on responses
       - Tracks what works for each individual
    
    4. PERSONALIZATION:
       - Everyone learns differently
       - System remembers what works for each user
       - Progress tracked and approach refined over time
    
    Attributes:
        dm: DataManager instance for database operations
        web_search_enabled: Whether web research is available
        
    Example:
        >>> manager = TrainingPlanManager(data_manager)
        >>> plan = manager.get_or_create_training_plan(user)
        >>> context = manager.get_training_context_for_prompt(user)
    """
    
    # Default training plan structure
    DEFAULT_TRAINING = {
        "empathy_training": {
            "skill_name": "empathy",
            "description": "Understanding and sharing feelings of others",
            "duration_days": 30,
            "milestones": [
                {"level": 2, "description": "Recognizing emotions in text"},
                {"level": 4, "description": "Responding with empathetic phrases"},
                {"level": 6, "description": "Asking follow-up questions about feelings"},
                {"level": 8, "description": "Providing emotional support naturally"},
                {"level": 10, "description": "Mastery: Authentic empathetic communication"}
            ],
            "priority": "high",
            "auto_start": True
        },
        "conversation_training": {
            "skill_name": "active_listening",
            "description": "Active listening and engaging conversation",
            "duration_days": 30,
            "milestones": [
                {"level": 2, "description": "Using acknowledgment phrases"},
                {"level": 4, "description": "Asking clarifying questions"},
                {"level": 6, "description": "Summarizing what others said"},
                {"level": 8, "description": "Building on others' ideas"},
                {"level": 10, "description": "Mastery: Natural conversational flow"}
            ],
            "priority": "high",
            "auto_start": True
        }
    }
    
    def __init__(self, data_manager: DataManager):
        """
        Initialize TrainingPlanManager.
        
        Args:
            data_manager: DataManager instance for database operations
        """
        self.dm = data_manager
        # Note: SecureMemoryManager created per-user when needed (requires user object)
        logger.logger.info("✅ TrainingPlanManager initialized")
    
    def get_or_create_training_plan(self, user: User) -> Dict[str, Any]:
        """
        Get existing training plan or create a new one for user.
        
        This is called when user logs in to ensure they have a training plan.
        Creates default empathy + conversation training if none exists.
        
        Args:
            user: User object from database
            
        Returns:
            Dictionary containing training plan with current progress
            
        Example:
            {
                "empathy_training": {
                    "current_level": 3,
                    "target_level": 10,
                    "progress_percent": 30,
                    "next_milestone": "Asking follow-up questions about feelings",
                    "status": "active"
                },
                "conversation_training": {...},
                "message_count": 3,  # For tracking 5th message
                "last_check": "2025-11-30T17:00:00"
            }
        """
        logger.logger.info(f"Loading training plan for user {user.id} ({user.username})")
        
        try:
            # Try to load encrypted training data from memory
            training_data = self._load_encrypted_training_data(user)
            
            if training_data:
                logger.logger.info(f"✅ Loaded existing training plan for user {user.id}")
                return training_data
            
            # No training plan exists - create default one
            logger.logger.info(f"🆕 Creating default training plan for user {user.id}")
            training_data = self._create_default_training_plan(user)
            
            # Save encrypted training data
            self._save_encrypted_training_data(user, training_data)
            
            return training_data
            
        except Exception as e:
            logger.logger.error(f"Error loading/creating training plan: {e}", exc_info=True)
            return self._get_empty_training_plan()
    
    def _create_default_training_plan(self, user: User) -> Dict[str, Any]:
        """
        Create default training plan with empathy + conversation training.
        
        Args:
            user: User object
            
        Returns:
            Dictionary with default training plan structure
        """
        training_data = {
            "user_id": user.id,
            "created_at": datetime.utcnow().isoformat(),
            "message_count": 0,
            "last_progress_check": None,
            "trainings": {}
        }
        
        # Create training entries for default skills
        for training_key, training_config in self.DEFAULT_TRAINING.items():
            skill_name = training_config["skill_name"]
            
            # Get or create skill in database
            skill = self.dm.get_or_create_skill(skill_name)
            
            if skill:
                # Get current skill level
                current_level = self.dm.get_skilllevel_for_user(user.id, skill.id) or 0
                
                # Create training record in database
                training = Training(
                    user_id=user.id,
                    skill_id=skill.id,
                    status="active" if training_config.get("auto_start") else "pending",
                    progress=current_level / 10.0,  # Convert level (0-10) to progress (0.0-1.0)
                    notes=f"Auto-started: {training_config['description']}"
                )
                self.dm.add_training(training)
                
                # Add to training data
                training_data["trainings"][training_key] = {
                    "skill_id": skill.id,
                    "skill_name": skill_name,
                    "description": training_config["description"],
                    "current_level": current_level,
                    "target_level": 10,
                    "progress_percent": current_level * 10,
                    "status": training.status,
                    "started_at": training.started_at.isoformat() if training.started_at else None,
                    "milestones": training_config["milestones"],
                    "next_milestone": self._get_next_milestone(current_level, training_config["milestones"])
                }
        
        logger.logger.info(f"✅ Created default training plan with {len(training_data['trainings'])} trainings")
        return training_data
    
    def _get_next_milestone(self, current_level: int, milestones: List[Dict]) -> Optional[str]:
        """
        Get next milestone description based on current level.
        
        Args:
            current_level: Current skill level (0-10)
            milestones: List of milestone dictionaries
            
        Returns:
            Description of next milestone or None if completed
        """
        for milestone in milestones:
            if current_level < milestone["level"]:
                return milestone["description"]
        return None  # All milestones completed
    
    def should_check_progress(self, user: User) -> bool:
        """
        Check if it's time to evaluate progress (every 5th message).
        
        Args:
            user: User object
            
        Returns:
            True if progress check should happen, False otherwise
        """
        try:
            training_data = self._load_encrypted_training_data(user)
            if not training_data:
                return False
            
            message_count = training_data.get("message_count", 0)
            
            # Check every 5th message
            if message_count > 0 and message_count % 5 == 0:
                logger.logger.info(f"✅ Progress check triggered for user {user.id} (message #{message_count})")
                return True
            
            return False
            
        except Exception as e:
            logger.logger.error(f"Error checking progress: {e}")
            return False
    
    def increment_message_count(self, user: User):
        """
        Increment message count for progress tracking.
        
        Call this for every user message.
        
        Args:
            user: User object
        """
        try:
            training_data = self._load_encrypted_training_data(user)
            if training_data:
                training_data["message_count"] = training_data.get("message_count", 0) + 1
                self._save_encrypted_training_data(user, training_data)
                logger.logger.debug(f"Message count for user {user.id}: {training_data['message_count']}")
        except Exception as e:
            logger.logger.error(f"Error incrementing message count: {e}")
    
    def update_training_progress(self, user: User, skill_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update training progress based on skill analysis.
        
        Called every 5th message to check progress.
        
        Args:
            user: User object
            skill_analysis: Results from SkillEvaluator
            
        Returns:
            Updated training data with new progress
        """
        logger.logger.info(f"Updating training progress for user {user.id}")
        
        try:
            training_data = self._load_encrypted_training_data(user)
            if not training_data:
                return {}
            
            # Update last progress check timestamp
            training_data["last_progress_check"] = datetime.utcnow().isoformat()
            
            # Update each active training based on skill analysis
            skills_updated = skill_analysis.get("skills_updated", [])
            
            for skill_update in skills_updated:
                skill_name = skill_update.get("skill")
                new_level = skill_update.get("new_level", 0)
                
                # Find matching training
                for training_key, training_info in training_data["trainings"].items():
                    if training_info["skill_name"] == skill_name:
                        training_info["current_level"] = new_level
                        training_info["progress_percent"] = new_level * 10
                        training_info["next_milestone"] = self._get_next_milestone(
                            new_level, 
                            training_info["milestones"]
                        )
                        
                        # Update database
                        skill = self.dm.get_or_create_skill(skill_name)
                        if skill:
                            self.dm.update_training_status(
                                user.id, 
                                skill.id, 
                                "completed" if new_level >= 10 else "active"
                            )
                        
                        logger.logger.info(f"✅ Updated {skill_name}: level {new_level}/10")
            
            # Save updated training data
            self._save_encrypted_training_data(user, training_data)
            
            return training_data
            
        except Exception as e:
            logger.logger.error(f"Error updating training progress: {e}", exc_info=True)
            return {}
    
    def get_login_reminder(self, user: User) -> str:
        """
        Generate login message with training reminders.
        
        Args:
            user: User object
            
        Returns:
            Formatted login message with training status
            
        Example:
            "Welcome back, John! 🎯
            
            Your Active Trainings:
            • Empathy: Level 3/10 - Keep practicing empathetic responses!
            • Active Listening: Level 5/10 - Great progress on clarifying questions!"
        """
        try:
            training_data = self._load_encrypted_training_data(user)
            if not training_data or not training_data.get("trainings"):
                return f"Welcome back, {user.username}! 👋"
            
            reminder_parts = [f"Welcome back, {user.username}! 🎯\n"]
            
            active_trainings = [
                t for t in training_data["trainings"].values() 
                if t.get("status") == "active"
            ]
            
            if active_trainings:
                reminder_parts.append("\n**Your Active Trainings:**")
                for training in active_trainings:
                    level = training["current_level"]
                    name = training["skill_name"].replace("_", " ").title()
                    next_milestone = training.get("next_milestone")
                    
                    if next_milestone:
                        reminder_parts.append(
                            f"• **{name}**: Level {level}/10 - Next: {next_milestone}"
                        )
                    else:
                        reminder_parts.append(
                            f"• **{name}**: Level {level}/10 - 🎉 Almost mastered!"
                        )
            
            return "\n".join(reminder_parts)
            
        except Exception as e:
            logger.logger.error(f"Error generating login reminder: {e}")
            return f"Welcome back, {user.username}! 👋"
    
    def get_training_context_for_prompt(self, user: User) -> str:
        """
        Get training plan context to add to AI system prompt.
        
        Args:
            user: User object
            
        Returns:
            Formatted string with training context for system prompt
        """
        try:
            training_data = self._load_encrypted_training_data(user)
            if not training_data or not training_data.get("trainings"):
                return ""
            
            context_parts = [
                "\n🎯 **ACTIVE TRAINING PLAN**",
                f"User {user.username} is currently training in:"
            ]
            
            for training_key, training_info in training_data["trainings"].items():
                if training_info.get("status") == "active":
                    skill_name = training_info["skill_name"].replace("_", " ").title()
                    level = training_info["current_level"]
                    next_milestone = training_info.get("next_milestone")
                    
                    context_parts.append(
                        f"• **{skill_name}** (Level {level}/10): {training_info['description']}"
                    )
                    if next_milestone:
                        context_parts.append(f"  Next milestone: {next_milestone}")
            
            # Add learning style instructions
            learning_style = training_data.get("learning_style", LearningStyle.ADAPTIVE)
            style_prompt = LearningStyle.STYLE_PROMPTS.get(
                learning_style, 
                LearningStyle.STYLE_PROMPTS["adaptive"]
            )
            
            context_parts.extend([
                f"\n**USER'S LEARNING STYLE: {learning_style.upper()}**",
                f"Teaching approach: {style_prompt}",
                "\n**SUBCONSCIOUS TRAINING (Default Mode):**",
                "- Basic training happens SUBTLY through natural conversation",
                "- DO NOT explicitly say 'I'm training you' or 'This is a lesson'",
                "- Model good empathy and communication in YOUR responses",
                "- Weave learning moments naturally into helpful conversation",
                "- The user should feel helped, not lectured",
                "\n**EXPLICIT TRAINING (When User Asks):**",
                "- When user EXPLICITLY asks for training (e.g., 'teach me', 'help me practice'):",
                "  * Then provide ACTIVE, DIRECT training with exercises",
                "  * Give specific scenarios adapted to their learning style",
                "  * Offer feedback on their responses",
                "  * Make it interactive and engaging",
                "\n**ADAPTIVE PERSONALIZATION:**",
                "- Everyone learns differently - observe what works for THIS user",
                "- If they respond well to examples, use more examples",
                "- If they prefer practice, give more exercises",
                "- Adjust your approach based on their engagement",
                "- Track progress using the skill_evaluator tool"
            ])
            
            # Add best practices if available
            for training_key, training_info in training_data["trainings"].items():
                if training_info.get("latest_best_practices"):
                    practices = training_info["latest_best_practices"]
                    context_parts.append(
                        f"\n**Latest Research for {training_info['skill_name']}:**"
                    )
                    context_parts.append(
                        f"(Updated: {practices.get('fetched_at', 'N/A')[:10]})"
                    )
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.logger.error(f"Error getting training context: {e}")
            return ""
    
    def save_logout_progress(self, user: User, final_analysis: Optional[Dict] = None):
        """
        Save all progress data on logout.
        
        Args:
            user: User object
            final_analysis: Optional final skill analysis from conversation
        """
        logger.logger.info(f"Saving logout progress for user {user.id}")
        
        try:
            training_data = self._load_encrypted_training_data(user)
            if not training_data:
                return
            
            # Add logout timestamp
            training_data["last_logout"] = datetime.utcnow().isoformat()
            
            # If final analysis provided, update once more
            if final_analysis:
                self.update_training_progress(user, final_analysis)
            
            # Save encrypted
            self._save_encrypted_training_data(user, training_data)
            
            logger.logger.info(f"✅ Logout progress saved for user {user.id}")
            
        except Exception as e:
            logger.logger.error(f"Error saving logout progress: {e}", exc_info=True)
    
    def _load_encrypted_training_data(self, user: User) -> Optional[Dict[str, Any]]:
        """
        Load encrypted training data from SecureMemoryManager.
        
        Args:
            user: User object
            
        Returns:
            Decrypted training data or None if not found
        """
        try:
            # Create SecureMemoryManager for this user
            memory_manager = SecureMemoryManager(self.dm, user)
            
            # Load from memory system (already encrypted)
            memory_data = memory_manager.get_current_memory()
            
            if memory_data and "training_plan" in memory_data:
                return memory_data["training_plan"]
            
            return None
            
        except Exception as e:
            logger.logger.error(f"Error loading encrypted training data: {e}")
            return None
    
    def _save_encrypted_training_data(self, user: User, training_data: Dict[str, Any]):
        """
        Save training data encrypted via SecureMemoryManager.
        
        Args:
            user: User object
            training_data: Training data to encrypt and save
        """
        try:
            # Create SecureMemoryManager for this user
            memory_manager = SecureMemoryManager(self.dm, user)
            
            # Get current memory structure
            current_memory = memory_manager._current_memory
            
            # Update training plan section
            current_memory["training_plan"] = training_data
            
            # Update metadata
            from datetime import datetime
            current_memory["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Encrypt and save to database
            encrypted = memory_manager._encryptor.encrypt_memory(current_memory)
            self.dm.update_user_memory(user.id, encrypted)
            
            logger.logger.debug(f"✅ Encrypted training data saved for user {user.id}")
            
        except Exception as e:
            logger.logger.error(f"Error saving encrypted training data: {e}", exc_info=True)
    
    def _get_empty_training_plan(self) -> Dict[str, Any]:
        """Return empty training plan structure."""
        return {
            "trainings": {},
            "message_count": 0,
            "last_progress_check": None,
            "learning_style": LearningStyle.ADAPTIVE,
            "best_practices_updated": None
        }
    
    # =========================================================================
    # WEB RESEARCH FOR UP-TO-DATE BEST PRACTICES
    # =========================================================================
    
    def fetch_latest_best_practices(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch latest training best practices from web research.
        
        Uses Tavily search to find current research and best practices
        for teaching specific social skills. Results are cached in the
        training plan to avoid repeated searches.
        
        Args:
            skill_name: Name of skill to research (e.g., 'empathy')
            
        Returns:
            Dictionary with research findings or None if unavailable
            
        Example:
            >>> practices = manager.fetch_latest_best_practices('empathy')
            >>> print(practices['techniques'])
        """
        if not WEB_SEARCH_AVAILABLE or not tavily_search:
            logger.logger.warning("Web search not available for best practices")
            return None
        
        try:
            # Search for current best practices
            query = f"best practices teaching {skill_name} skills 2024 2025 techniques exercises"
            logger.logger.info(f"🔍 Fetching best practices for: {skill_name}")
            
            results = tavily_search.invoke(query)
            
            best_practices = {
                "skill": skill_name,
                "query": query,
                "research_summary": str(results)[:1000],  # Limit size
                "fetched_at": datetime.utcnow().isoformat(),
                "source": "web_research"
            }
            
            logger.logger.info(f"✅ Retrieved best practices for {skill_name}")
            return best_practices
            
        except Exception as e:
            logger.logger.error(f"Error fetching best practices: {e}")
            return None
    
    def update_training_with_best_practices(self, user: User) -> bool:
        """
        Update user's training plan with latest best practices from web.
        
        Called periodically (e.g., weekly) to ensure training stays current
        with latest research and techniques.
        
        Args:
            user: User object
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            training_data = self._load_encrypted_training_data(user)
            if not training_data:
                return False
            
            # Check if we need to update (only once per week)
            last_update = training_data.get("best_practices_updated")
            if last_update:
                last_update_date = datetime.fromisoformat(last_update)
                if (datetime.utcnow() - last_update_date).days < 7:
                    logger.logger.debug("Best practices recently updated, skipping")
                    return True
            
            # Fetch best practices for each active training
            for training_key, training_info in training_data.get("trainings", {}).items():
                if training_info.get("status") == "active":
                    skill_name = training_info.get("skill_name")
                    practices = self.fetch_latest_best_practices(skill_name)
                    if practices:
                        training_info["latest_best_practices"] = practices
            
            # Update timestamp
            training_data["best_practices_updated"] = datetime.utcnow().isoformat()
            
            # Save updated data
            self._save_encrypted_training_data(user, training_data)
            
            logger.logger.info(f"✅ Updated best practices for user {user.id}")
            return True
            
        except Exception as e:
            logger.logger.error(f"Error updating best practices: {e}")
            return False
    
    # =========================================================================
    # ADAPTIVE LEARNING - PERSONALIZED TO USER'S STYLE
    # =========================================================================
    
    def get_user_learning_style(self, user: User) -> str:
        """
        Get user's detected or preferred learning style.
        
        Learning styles:
        - visual: Learns through examples, scenarios, imagery
        - auditory: Learns through dialogue, verbal explanations
        - kinesthetic: Learns through practice, exercises, role-play
        - reading_writing: Learns through written explanations
        - adaptive: System automatically adjusts (default)
        
        Args:
            user: User object
            
        Returns:
            Learning style string
        """
        try:
            training_data = self._load_encrypted_training_data(user)
            if training_data:
                return training_data.get("learning_style", LearningStyle.ADAPTIVE)
            return LearningStyle.ADAPTIVE
        except Exception:
            return LearningStyle.ADAPTIVE
    
    def set_user_learning_style(self, user: User, style: str) -> bool:
        """
        Set user's preferred learning style.
        
        Args:
            user: User object
            style: One of: visual, auditory, kinesthetic, reading_writing, adaptive
            
        Returns:
            True if successful, False otherwise
        """
        valid_styles = [
            LearningStyle.VISUAL,
            LearningStyle.AUDITORY,
            LearningStyle.KINESTHETIC,
            LearningStyle.READING_WRITING,
            LearningStyle.ADAPTIVE
        ]
        
        if style not in valid_styles:
            logger.logger.warning(f"Invalid learning style: {style}")
            return False
        
        try:
            training_data = self._load_encrypted_training_data(user)
            if not training_data:
                training_data = self._get_empty_training_plan()
            
            training_data["learning_style"] = style
            self._save_encrypted_training_data(user, training_data)
            
            logger.logger.info(f"✅ Set learning style to '{style}' for user {user.id}")
            return True
            
        except Exception as e:
            logger.logger.error(f"Error setting learning style: {e}")
            return False
    
    def detect_learning_style_from_responses(
        self, 
        user: User, 
        user_responses: List[str]
    ) -> str:
        """
        Analyze user responses to detect preferred learning style.
        
        This method examines how the user responds to different teaching
        approaches and determines what works best for them.
        
        Args:
            user: User object
            user_responses: List of user's recent responses
            
        Returns:
            Detected learning style
            
        Note:
            This is a heuristic approach. The AI will also adapt
            in real-time based on conversation flow.
        """
        if not user_responses:
            return LearningStyle.ADAPTIVE
        
        # Analyze response patterns
        combined = " ".join(user_responses).lower()
        
        # Simple heuristic detection (AI does more sophisticated adaptation)
        scores = {
            LearningStyle.VISUAL: 0,
            LearningStyle.AUDITORY: 0,
            LearningStyle.KINESTHETIC: 0,
            LearningStyle.READING_WRITING: 0
        }
        
        # Visual indicators
        if any(w in combined for w in ["show", "see", "picture", "imagine", "example"]):
            scores[LearningStyle.VISUAL] += 1
        
        # Auditory indicators
        if any(w in combined for w in ["tell", "explain", "discuss", "talk", "hear"]):
            scores[LearningStyle.AUDITORY] += 1
        
        # Kinesthetic indicators
        if any(w in combined for w in ["try", "practice", "do", "exercise", "hands-on"]):
            scores[LearningStyle.KINESTHETIC] += 1
        
        # Reading/Writing indicators
        if any(w in combined for w in ["read", "write", "list", "notes", "summary"]):
            scores[LearningStyle.READING_WRITING] += 1
        
        # Get highest scoring style
        if max(scores.values()) > 0:
            detected = max(scores, key=scores.get)
            logger.logger.info(f"Detected learning style: {detected}")
            return detected
        
        return LearningStyle.ADAPTIVE
    
    def get_learning_style_prompt(self, user: User) -> str:
        """
        Get AI prompt instructions based on user's learning style.
        
        Args:
            user: User object
            
        Returns:
            String with teaching style instructions for AI
        """
        style = self.get_user_learning_style(user)
        return LearningStyle.STYLE_PROMPTS.get(style, LearningStyle.STYLE_PROMPTS["adaptive"])
