# ============================================================================
# FILE: agents/base_agent.py (FIXED - Complete version)
# ============================================================================
from abc import ABC, abstractmethod
from typing import Dict

class BaseAgent(ABC):
    """Base class for all agents"""
    
    @abstractmethod
    async def execute(self, query: str, domain: str, **kwargs) -> Dict:
        """Execute agent task"""
        pass
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "name": self.__class__.__name__,
            "available": True
        }