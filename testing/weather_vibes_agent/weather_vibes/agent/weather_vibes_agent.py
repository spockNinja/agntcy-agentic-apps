"""
Weather Vibes Agent implementation using the Simple Agent Framework.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader

from agent_framework.agent import Agent
from agent_framework.state import AgentState
from agent_framework.utils.llm import OpenAIChat
from agent_framework.utils.logging import AgentLogger

from ..tools import WeatherTool, RecommendationsTool, YouTubeTool
from .descriptor import WEATHER_VIBES_DESCRIPTOR

class WeatherVibesAgent(Agent):
    """
    Agent that provides weather information, recommendations, and matching videos.
    Implements the Agent Connect Protocol (ACP) for standardized communication.
    """
    
    def __init__(self, agent_id: str = "weather_vibes"):
        super().__init__(agent_id=agent_id)
        
        # Initialize state
        self.state = AgentState()
        self.state.set("search_history", [])
        self.state.set("favorite_locations", [])
        
        # Set up template environment
        template_dir = Path(__file__).parent.parent / "templates"
        self.template_env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True
        )
