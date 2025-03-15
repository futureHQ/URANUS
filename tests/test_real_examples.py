import pytest
import asyncio
import os
from pathlib import Path
from uranus.agent.reactive_agent import ReactiveAgent
from uranus.tool.system_tool import SystemInfoTool
from uranus.tool.file_operations import FileOperationsTool
from tests.mocks.mock_llm import MockLLM


@pytest.mark.asyncio
async def test_travel_planner():
    """Test a real-world travel planning scenario."""
    # Create a reactive agent with travel planning capabilities
    agent = ReactiveAgent(
        name="TravelPlanner",
        description="An AI assistant that helps plan travel itineraries.",
        system_prompt="""You are TravelPlanner, an AI assistant specialized in creating travel itineraries.
        You can help users plan their trips by suggesting destinations, activities, and accommodations.
        You can also create and manage travel-related files.""",
        next_step_prompt="What else would you like to know about your trip?"
    )
    
    # Replace the LLM with our mock
    agent.llm = MockLLM()
    
    # Add travel-specific responses to the mock LLM
    agent.llm.responses.update({
        "I want to plan a 3-day trip to Tokyo, Japan. Can you help me create an itinerary?": 
            "I'd be happy to help you plan a 3-day trip to Tokyo! Here's a basic outline:\n\nDay 1: Visit Asakusa and Senso-ji Temple, explore Ueno Park\nDay 2: Check out Shibuya Crossing and Meiji Shrine\nDay 3: Visit Akihabara and Tokyo Skytree\n\nWould you like me to create a detailed itinerary file?",
        
        "Please create a file called tokyo_itinerary.txt with a basic 3-day plan":
            "I've created the file tokyo_itinerary.txt with a basic 3-day plan for Tokyo.",
        
        "Show me the content of the tokyo_itinerary.txt file":
            "The content of tokyo_itinerary.txt is:\n\nTOKYO 3-DAY ITINERARY\n\nDay 1:\n- Morning: Visit Asakusa and Senso-ji Temple\n- Afternoon: Explore Ueno Park and museums\n- Evening: Dinner in Asakusa area\n\nDay 2:\n- Morning: Visit Shibuya Crossing and shopping\n- Afternoon: Explore Meiji Shrine and Yoyogi Park\n- Evening: Dinner in Shibuya\n\nDay 3:\n- Morning: Visit Akihabara for electronics and anime\n- Afternoon: Tokyo Skytree for city views\n- Evening: Farewell dinner in Shinjuku",
        
        "Add a visit to Tokyo Tower on day 2 to the itinerary":
            "I've updated the tokyo_itinerary.txt file to include a visit to Tokyo Tower on day 2."
    })
    
    # Register tools
    agent.tools.register(SystemInfoTool())
    agent.tools.register(FileOperationsTool())
    
    # Create a test workspace for travel planning
    test_dir = Path.home() / "uranus_workspace" / "travel_planning"
    os.makedirs(test_dir, exist_ok=True)
    
    # Run a series of travel planning interactions
    responses = []
    
    # First interaction: Initial travel inquiry
    response1 = await agent.run("I want to plan a 3-day trip to Tokyo, Japan. Can you help me create an itinerary?")
    responses.append(response1)
    
    # Second interaction: Create an itinerary file
    response2 = await agent.run("Please create a file called tokyo_itinerary.txt with a basic 3-day plan")
    responses.append(response2)
    
    # Third interaction: Read the itinerary
    response3 = await agent.run("Show me the content of the tokyo_itinerary.txt file")
    responses.append(response3)
    
    # Fourth interaction: Update the itinerary
    response4 = await agent.run("Add a visit to Tokyo Tower on day 2 to the itinerary")
    responses.append(response4)
    
    # Print the full conversation for debugging
    print("\n".join(responses))
    
    # Cleanup
    if os.path.exists(test_dir / "tokyo_itinerary.txt"):
        os.remove(test_dir / "tokyo_itinerary.txt")
    
    # Verify some expected content in the responses
    assert any("Tokyo" in response for response in responses)
    assert any("itinerary" in response for response in responses)