"""
Agent LLM Module - Specialized LLM integration for agents
Provides streaming responses, model configuration, and token management
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from dataclasses import dataclass, field
from enum import Enum
import time
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelType(Enum):
    LOCAL = "local"
    API = "api"
    HYBRID = "hybrid"

class ResponseFormat(Enum):
    TEXT = "text"
    JSON = "json"
    STRUCTURED = "structured"

@dataclass
class ModelConfig:
    name: str
    model_type: ModelType
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    context_window: int = 8192
    response_format: ResponseFormat = ResponseFormat.TEXT
    streaming: bool = True
    timeout: float = 30.0
    retry_attempts: int = 3
    api_key: Optional[str] = None
    model_path: Optional[str] = None

@dataclass
class LLMRequest:
    messages: List[Dict[str, str]]
    model_config: ModelConfig
    tools: List[Dict[str, Any]] = field(default_factory=list)
    tool_choice: str = "auto"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMResponse:
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"
    model: str = ""
    response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float = 0.0

class AgentLLM:
    def __init__(self, default_config: ModelConfig = None):
        self.default_config = default_config or ModelConfig(
            name="mistral-7b-instruct",
            model_type=ModelType.LOCAL,
            model_path="models/mistral-7b-instruct.gguf"
        )
        
        # Model configurations by agent type
        self.agent_configs = {
            "researcher": ModelConfig(
                name="mistral-7b-instruct",
                model_type=ModelType.LOCAL,
                temperature=0.3,  # Lower temperature for research
                max_tokens=2048,
                response_format=ResponseFormat.STRUCTURED
            ),
            "developer": ModelConfig(
                name="mistral-7b-instruct",
                model_type=ModelType.LOCAL,
                temperature=0.1,  # Very low temperature for code
                max_tokens=4096,
                response_format=ResponseFormat.TEXT
            ),
            "analyst": ModelConfig(
                name="mistral-7b-instruct",
                model_type=ModelType.LOCAL,
                temperature=0.5,
                max_tokens=3072,
                response_format=ResponseFormat.JSON
            )
        }
        
        # Token usage tracking
        self.token_usage: Dict[str, TokenUsage] = {}
        self.total_usage = TokenUsage(0, 0, 0)
        
        # Request statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_tokens_used": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Response cache
        self.response_cache: Dict[str, LLMResponse] = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a complete response from the LLM
        """
        start_time = time.time()
        
        try:
            self.stats["total_requests"] += 1
            
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.response_cache:
                cached_response = self.response_cache[cache_key]
                if time.time() - cached_response.metadata.get("cached_at", 0) < self.cache_ttl:
                    self.stats["cache_hits"] += 1
                    return cached_response
            
            self.stats["cache_misses"] += 1
            
            # Generate response
            if request.model_config.streaming:
                response = await self._generate_streaming_response(request)
            else:
                response = await self._generate_non_streaming_response(request)
            
            # Update response time
            response.response_time = time.time() - start_time
            
            # Cache response
            response.metadata["cached_at"] = time.time()
            self.response_cache[cache_key] = response
            
            # Update statistics
            self._update_stats(response, success=True)
            
            return response
            
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            self._update_stats(None, success=False)
            
            # Return error response
            return LLMResponse(
                content=f"Error: {str(e)}",
                response_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    async def stream_response(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Stream response chunks from the LLM
        """
        start_time = time.time()
        accumulated_content = ""
        
        try:
            self.stats["total_requests"] += 1
            
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.response_cache:
                cached_response = self.response_cache[cache_key]
                if time.time() - cached_response.metadata.get("cached_at", 0) < self.cache_ttl:
                    self.stats["cache_hits"] += 1
                    # Stream cached response
                    for chunk in self._chunk_content(cached_response.content):
                        yield chunk
                    return
            
            self.stats["cache_misses"] += 1
            
            # Stream from model
            async for chunk in self._stream_from_model(request):
                accumulated_content += chunk
                yield chunk
            
            # Cache complete response
            response = LLMResponse(
                content=accumulated_content,
                response_time=time.time() - start_time,
                metadata={"cached_at": time.time()}
            )
            self.response_cache[cache_key] = response
            
            # Update statistics
            self._update_stats(response, success=True)
            
        except Exception as e:
            logger.error(f"LLM streaming failed: {e}")
            self._update_stats(None, success=False)
            yield f"Error: {str(e)}"
    
    async def _generate_streaming_response(self, request: LLMRequest) -> LLMResponse:
        """
        Generate streaming response internally
        """
        content = ""
        async for chunk in self.stream_response(request):
            content += chunk
        
        return LLMResponse(
            content=content,
            response_time=0.0,  # Will be updated by caller
            metadata={"streaming": True}
        )
    
    async def _generate_non_streaming_response(self, request: LLMRequest) -> LLMResponse:
        """
        Generate non-streaming response
        """
        # For now, implement as streaming then combine
        return await self._generate_streaming_response(request)
    
    async def _stream_from_model(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Stream response from the actual model
        """
        try:
            if request.model_config.model_type == ModelType.LOCAL:
                async for chunk in self._stream_local_model(request):
                    yield chunk
            elif request.model_config.model_type == ModelType.API:
                async for chunk in self._stream_api_model(request):
                    yield chunk
            else:
                # Hybrid implementation
                async for chunk in self._stream_hybrid_model(request):
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Model streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    async def _stream_local_model(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Stream from local model (e.g., llama.cpp)
        """
        try:
            # This would integrate with llama-cpp-python or similar
            # For now, simulate streaming response
            
            messages = request.messages
            system_prompt = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                elif msg["role"] == "user":
                    user_messages.append(msg["content"])
            
            # Simulate model response
            prompt = "\n".join(user_messages)
            
            # Simulate streaming chunks
            response_text = self._simulate_model_response(prompt, request.model_config)
            
            for chunk in self._chunk_content(response_text):
                yield chunk
                await asyncio.sleep(0.01)  # Simulate processing delay
                
        except Exception as e:
            logger.error(f"Local model streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    async def _stream_api_model(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Stream from API model (e.g., OpenAI)
        """
        try:
            # This would integrate with OpenAI API or similar
            # For now, fall back to local simulation
            async for chunk in self._stream_local_model(request):
                yield chunk
                
        except Exception as e:
            logger.error(f"API model streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    async def _stream_hybrid_model(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Stream from hybrid model (local + API)
        """
        try:
            # Try local first, fallback to API
            async for chunk in self._stream_local_model(request):
                yield chunk
                
        except Exception as e:
            logger.warning(f"Local model failed, trying API: {e}")
            async for chunk in self._stream_api_model(request):
                yield chunk
    
    def _simulate_model_response(self, prompt: str, config: ModelConfig) -> str:
        """
        Simulate model response for testing
        """
        # Simple simulation based on prompt content
        if "research" in prompt.lower():
            return """I'll help you research this topic. Let me search for relevant information and provide you with a comprehensive analysis.

Based on my analysis, here are the key findings:

1. **Primary Results**: The topic shows significant interest in the research community
2. **Recent Developments**: There have been several breakthroughs in this area
3. **Expert Opinions**: Leading researchers suggest promising future directions

Would you like me to dive deeper into any specific aspect of this research?"""
        
        elif "code" in prompt.lower() or "develop" in prompt.lower():
            return """I'll help you develop a solution. Let me analyze the requirements and create appropriate code.

Here's my approach:

```python
def solve_problem():
    """
    Implement solution based on requirements
    """
    # Step 1: Analyze the problem
    requirements = analyze_requirements()
    
    # Step 2: Design solution
    solution = design_solution(requirements)
    
    # Step 3: Implement
    return implement_solution(solution)

if __name__ == "__main__":
    result = solve_problem()
    print(f"Result: {result}")
```

This implementation provides a clean, modular approach that can be easily extended. Let me know if you'd like me to elaborate on any specific part."""
        
        else:
            return """I understand your request. Let me process this information and provide you with a thoughtful response.

Based on the context you've provided, I can see this requires careful consideration of multiple factors. Here's my analysis:

**Key Points:**
- The situation involves several interconnected elements
- There are both opportunities and challenges to consider
- A systematic approach would be most effective

**Recommendations:**
1. Start with a clear assessment of the current state
2. Identify the most critical factors to address
3. Develop a step-by-step action plan
4. Monitor progress and adjust as needed

Would you like me to elaborate on any of these points or focus on a specific aspect?"""
    
    def _chunk_content(self, content: str, chunk_size: int = 50) -> List[str]:
        """
        Split content into chunks for streaming
        """
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            chunks.append(chunk)
        return chunks
    
    def _generate_cache_key(self, request: LLMRequest) -> str:
        """
        Generate cache key for request
        """
        import hashlib
        
        # Create a normalized representation of the request
        cache_data = {
            "messages": request.messages,
            "model": request.model_config.name,
            "temperature": request.model_config.temperature,
            "max_tokens": request.model_config.max_tokens
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _update_stats(self, response: Optional[LLMResponse], success: bool):
        """
        Update request statistics
        """
        if success:
            self.stats["successful_requests"] += 1
            if response:
                # Update average response time
                total_requests = self.stats["total_requests"]
                current_avg = self.stats["average_response_time"]
                self.stats["average_response_time"] = (
                    (current_avg * (total_requests - 1) + response.response_time) / total_requests
                )
                
                # Update token usage
                if response.usage:
                    self.total_usage.prompt_tokens += response.usage.get("prompt_tokens", 0)
                    self.total_usage.completion_tokens += response.usage.get("completion_tokens", 0)
                    self.total_usage.total_tokens += response.usage.get("total_tokens", 0)
        else:
            self.stats["failed_requests"] += 1
    
    def get_config_for_agent(self, agent_role: str) -> ModelConfig:
        """
        Get model configuration for specific agent role
        """
        return self.agent_configs.get(agent_role, self.default_config)
    
    def set_agent_config(self, agent_role: str, config: ModelConfig):
        """
        Set model configuration for specific agent role
        """
        self.agent_configs[agent_role] = config
        logger.info(f"Set config for agent role: {agent_role}")
    
    def create_request(self, messages: List[Dict[str, str]], agent_role: str = None,
                      tools: List[Dict[str, Any]] = None) -> LLMRequest:
        """
        Create LLM request with appropriate configuration
        """
        config = self.get_config_for_agent(agent_role) if agent_role else self.default_config
        
        return LLMRequest(
            messages=messages,
            model_config=config,
            tools=tools or [],
            metadata={"agent_role": agent_role} if agent_role else {}
        )
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive usage statistics
        """
        return {
            "token_usage": {
                "prompt_tokens": self.total_usage.prompt_tokens,
                "completion_tokens": self.total_usage.completion_tokens,
                "total_tokens": self.total_usage.total_tokens,
                "estimated_cost": self.total_usage.cost
            },
            "request_stats": self.stats.copy(),
            "cache_stats": {
                "cache_size": len(self.response_cache),
                "cache_hit_rate": self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"])
            },
            "agent_configs": {
                role: {
                    "name": config.name,
                    "model_type": config.model_type.value,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens
                }
                for role, config in self.agent_configs.items()
            }
        }
    
    def clear_cache(self):
        """
        Clear response cache
        """
        self.response_cache.clear()
        logger.info("LLM response cache cleared")
    
    def reset_statistics(self):
        """
        Reset usage statistics
        """
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_tokens_used": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        self.total_usage = TokenUsage(0, 0, 0)
        logger.info("LLM usage statistics reset")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on LLM system
        """
        try:
            # Test request
            test_request = self.create_request([
                {"role": "user", "content": "Hello, this is a health check."}
            ])
            
            start_time = time.time()
            response = await self.generate_response(test_request)
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response.content and not response.content.startswith("Error:") else "unhealthy",
                "response_time": response_time,
                "cache_size": len(self.response_cache),
                "total_requests": self.stats["total_requests"],
                "success_rate": self.stats["successful_requests"] / max(1, self.stats["total_requests"]),
                "default_model": self.default_config.name
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": time.time() - start_time
            }
