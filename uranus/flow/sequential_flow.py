from typing import Dict, List, Optional, Any, Union

from pydantic import Field

from uranus.flow.base_flow import BaseFlow
from uranus.agent.base_agent import BaseAgent
from uranus.core.logger import logger


class SequentialFlow(BaseFlow):
    """A flow that executes agents in sequence."""
    
    agent_sequence: List[str] = Field(default_factory=list)
    
    def __init__(
        self, 
        agents: Union[BaseAgent, List[BaseAgent], Dict[str, BaseAgent]], 
        **data
    ):
        """Initialize the sequential flow."""
        super().__init__(agents, **data)
        
        # Set agent_sequence to all agent keys if not specified
        if not self.agent_sequence:
            self.agent_sequence = list(self.agents.keys())
    
    async def execute(self, input_text: str) -> str:
        """Execute agents in sequence."""
        try:
            if not self.agents:
                raise ValueError("No agents available")
                
            current_input = input_text
            results = []
            
            # Execute each agent in sequence
            for agent_key in self.agent_sequence:
                if agent_key not in self.agents:
                    logger.warning(f"Agent '{agent_key}' not found, skipping")
                    continue
                    
                agent = self.agents[agent_key]
                logger.info(f"Executing agent: {agent_key}")
                
                # Execute the agent with the current input
                result = await agent.run(current_input)
                results.append(result)
                
                # Use the result as input for the next agent
                current_input = result
                
            # Combine all results
            final_result = "\n\n".join(results)
            return final_result
            
        except Exception as e:
            logger.error(f"Error in SequentialFlow: {str(e)}")
            return f"Execution failed: {str(e)}"