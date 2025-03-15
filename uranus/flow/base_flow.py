from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field

from uranus.agent.base_agent import BaseAgent
from uranus.core.logger import logger


class BaseFlow(BaseModel, ABC):
    """Base class for all flows."""
    
    agents: Dict[str, BaseAgent]
    primary_agent_key: Optional[str] = None
    
    def __init__(
        self, 
        agents: Union[BaseAgent, List[BaseAgent], Dict[str, BaseAgent]], 
        **data
    ):
        """Initialize the flow with agents."""
        # Process agents into a dictionary
        agents_dict = {}
        
        if isinstance(agents, BaseAgent):
            # Single agent
            agents_dict[agents.name] = agents
            data["primary_agent_key"] = agents.name
        elif isinstance(agents, list):
            # List of agents
            for agent in agents:
                agents_dict[agent.name] = agent
            if agents and "primary_agent_key" not in data:
                data["primary_agent_key"] = agents[0].name
        elif isinstance(agents, dict):
            # Dictionary of agents
            agents_dict = agents
            if agents and "primary_agent_key" not in data:
                data["primary_agent_key"] = next(iter(agents))
                
        # Initialize with processed data
        super().__init__(agents=agents_dict, **data)
    
    @property
    def primary_agent(self) -> Optional[BaseAgent]:
        """Get the primary agent."""
        if not self.primary_agent_key or self.primary_agent_key not in self.agents:
            return None
        return self.agents[self.primary_agent_key]
    
    @abstractmethod
    async def execute(self, input_text: str) -> str:
        """Execute the flow with the given input."""
        pass