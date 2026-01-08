"""LangChain agent setup for chatbot."""

from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from src.core.config import settings
from typing import List, Dict


class ChatbotAgent:
    """Agentic chatbot with tools."""
    
    def __init__(self):
        """Initialize the chatbot agent."""
        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize tools
        self.tools = [
            DuckDuckGoSearchRun(
                name="web_search",
                description="Search the web for current information. Use this when you need to find recent information, facts, news, or any information you don't have in your training data."
            )
        ]
        
        # System message
        self.system_message = """You are a helpful AI assistant with access to web search capabilities. 

When answering questions:
- Use the web search tool when you need current information or facts you're unsure about
- Provide clear, accurate, and helpful responses
- Be conversational and friendly
- If you use search results, incorporate them naturally into your response
- Always cite sources when using searched information"""
        
        # Create agent using LangGraph
        self.agent = create_react_agent(
            self.llm, 
            self.tools,
            prompt=self.system_message
        )
    
    async def chat(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Process a chat message and return the agent's response.
        
        Args:
            message: User message
            chat_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            Agent's response
        """
        # Convert chat history to LangChain format
        messages = []
        if chat_history:
            for msg in chat_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # Add current message
        messages.append(HumanMessage(content=message))
        
        # Execute agent
        result = await self.agent.ainvoke({"messages": messages})
        
        # Extract the last message (assistant's response)
        last_message = result["messages"][-1]
        return last_message.content
    
    async def generate_title(self, first_message: str) -> str:
        """
        Generate a conversation title based on the first message.
        
        Args:
            first_message: The first user message in the conversation
            
        Returns:
            A short title for the conversation
        """
        # Use a simple LLM call without tools for title generation
        title_llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )
        
        prompt = f"""Generate a short, concise title (3-6 words) for a conversation that starts with this message:

"{first_message}"

Return ONLY the title, nothing else."""
        
        response = await title_llm.ainvoke([HumanMessage(content=prompt)])
        title = response.content.strip().strip('"').strip("'")
        
        # Ensure title is not too long
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title


# Create singleton instance
chatbot_agent = ChatbotAgent()
