import json
import logging
from collections.abc import Generator
from typing import Any, Dict
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# Import the base functionality
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import AgentCore Memory SDK directly
try:
    from bedrock_agentcore.memory import MemoryClient
    AGENTCORE_SDK_AVAILABLE = True
except ImportError as e:
    AGENTCORE_SDK_AVAILABLE = False
    MemoryClient = None
    print(f"Warning: bedrock-agentcore SDK import failed: {e}")

logger = logging.getLogger(__name__)


class AgentCoreMemoryTool(Tool):
    memory_client: Any = None
    memory_id: str = None
    actor_id: str = None
    session_id: str = None
    namespace: str = None
    
    def _initialize_memory_client(self, tool_parameters: dict[str, Any]) -> bool:
        """Initialize Memory client with AWS credentials like bedrock_retrieve"""
        try:
            # Get AWS credentials from tool parameters
            aws_region = tool_parameters.get("aws_region")
            aws_access_key_id = tool_parameters.get("aws_access_key_id")
            aws_secret_access_key = tool_parameters.get("aws_secret_access_key")

            # Initialize MemoryClient with region
            region = aws_region or 'us-east-1'
            
            if AGENTCORE_SDK_AVAILABLE:
                # Create client kwargs similar to bedrock_retrieve
                client_kwargs = {"region_name": region}
                
                # Only add credentials if both access key and secret key are provided
                if aws_access_key_id and aws_secret_access_key:
                    # For MemoryClient, we need to set environment variables or use boto3 session
                    import os
                    os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key_id
                    os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key
                    os.environ['AWS_REGION'] = region
                
                # Initialize MemoryClient without hardcoded credentials
                self.memory_client = MemoryClient(region_name=region)
                logger.info(f"Memory client initialized for region: {region}")
                return True
            else:
                logger.error("AgentCore Memory SDK not available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Memory client: {str(e)}")
            return False
    
    def _get_runtime_config(self, key: str, default_value: str) -> str:
        """Get configuration from runtime (AgentCore Memory Manager settings)"""
        try:
            # Try to get from runtime credentials/settings
            if self.runtime and hasattr(self.runtime, 'credentials'):
                credentials = self.runtime.credentials
                if credentials and key in credentials:
                    return credentials[key]
            
            # Fallback to default
            return default_value
        except Exception:
            return default_value
    
    def _record_information(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Record information to memory"""
        try:
            # Extract the information to record
            information = tool_parameters.get('information', '')
            
            if not information:
                yield self.create_text_message("Error: Information to record is required")
                return
            
            # Use instance variables
            memory_id = self.memory_id
            actor_id = self.actor_id
            session_id = self.session_id
            
            yield self.create_text_message(f"💾 Recording information for {actor_id}...")
            
            if self.memory_client:
                # Format messages for storage - treat the information as a user message with assistant acknowledgment
                messages = [
                    (information, "USER"),
                    ("Information recorded successfully.", "ASSISTANT")
                ]
                
                # Store conversation event
                result = self.memory_client.create_event(
                    memory_id=memory_id,
                    actor_id=actor_id,
                    session_id=session_id,
                    messages=messages
                )
                
                # Extract event ID from result
                event_id = "unknown"
                if isinstance(result, dict):
                    if 'event' in result:
                        event_id = result['event'].get('eventId', 'unknown')
                    elif 'eventId' in result:
                        event_id = result['eventId']
                
                # Format response
                response_data = {
                    'success': True,
                    'message': "Information recorded successfully",
                    'data': {
                        'event_id': event_id,
                        'memory_id': memory_id,
                        'actor_id': actor_id,
                        'session_id': session_id,
                        'information_length': len(information)
                    }
                }
                
                yield self.create_json_message(response_data)
            else:
                yield self.create_text_message("❌ AgentCore Memory SDK not available")
                
        except Exception as e:
            logger.error(f"Record information error: {str(e)}")
            yield self.create_text_message(f"Exception in record operation: {str(e)}")
    
    def _retrieve_history(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Retrieve conversation history using get_last_k_turns"""
        try:
            # Extract business parameters
            k = tool_parameters.get('max_results', 10)
            
            # Validate k (number of turns to retrieve)
            if k < 1 or k > 50:
                k = 10
            
            # Use instance variables
            memory_id = self.memory_id
            actor_id = self.actor_id
            session_id = self.session_id
            
            yield self.create_text_message(f"📚 Retrieving last {k} conversation turns for {actor_id} (session: {session_id})")
            
            if self.memory_client:
                # Retrieve last k conversation turns using get_last_k_turns
                events = self.memory_client.get_last_k_turns(
                    memory_id=memory_id,
                    actor_id=actor_id,
                    session_id=session_id,
                    k=k
                )
                
                # Format the events for better readability
                formatted_events = []
                
                if events and isinstance(events, list):
                    for i, event in enumerate(events):
                        # Each event is actually a list of messages
                        if isinstance(event, list):
                            formatted_event = {
                                'turn_number': i + 1,
                                'event_id': f'turn_{i+1}',
                                'timestamp': 'unknown',
                                'messages': event  # event is already the list of messages
                            }
                        elif isinstance(event, dict):
                            # Fallback for dict format
                            formatted_event = {
                                'turn_number': i + 1,
                                'event_id': event.get('eventId', f'turn_{i+1}'),
                                'timestamp': event.get('timestamp', 'unknown'),
                                'messages': event.get('messages', [])
                            }
                        else:
                            # Handle event objects with attributes
                            formatted_event = {
                                'turn_number': i + 1,
                                'event_id': getattr(event, 'eventId', f'turn_{i+1}'),
                                'timestamp': getattr(event, 'timestamp', 'unknown'),
                                'messages': getattr(event, 'messages', [])
                            }
                        formatted_events.append(formatted_event)
                
                # Format response
                response_data = {
                    'success': True,
                    'message': f"Retrieved last {len(formatted_events)} conversation turns successfully",
                    'data': {
                        'memory_id': memory_id,
                        'actor_id': actor_id,
                        'session_id': session_id,
                        'turns_requested': k,
                        'turns_retrieved': len(formatted_events),
                        'conversation_turns': formatted_events
                    }
                }
                
                yield self.create_json_message(response_data)
            else:
                yield self.create_text_message("❌ AgentCore Memory SDK not available")
                
        except Exception as e:
            logger.error(f"Retrieve history error: {str(e)}")
            yield self.create_text_message(f"Exception in retrieve operation: {str(e)}")
    
    def _search_memories(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Search for relevant memories"""
        try:
            # Extract business parameters
            search_query = tool_parameters.get('search_query', '')
            max_results = tool_parameters.get('max_results', 10)
            
            if not search_query:
                yield self.create_text_message("Error: Search query is required")
                return
            
            # Validate max_results
            if max_results < 1 or max_results > 20:
                max_results = 10
            
            # Use instance variables
            memory_id = self.memory_id
            actor_id = self.actor_id
            namespace = self.namespace
            
            yield self.create_text_message(f"🔍 Searching memories for: '{search_query}'")
            
            if self.memory_client:
                # Search memories using retrieve_memories method
                result = self.memory_client.retrieve_memories(
                    memory_id=memory_id,
                    actor_id=actor_id,
                    namespace=namespace,
                    query=search_query,
                    top_k=max_results
                )
                
                # Extract memories from response
                memories_list = result.get('memories', []) if isinstance(result, dict) else result
                
                # Ensure it's a list
                if not isinstance(memories_list, list):
                    memories_list = list(memories_list) if hasattr(memories_list, '__iter__') else []
                
                # Apply max_results limit if needed
                if max_results and len(memories_list) > max_results:
                    memories_list = memories_list[:max_results]
                
                # Process memories to ensure JSON serialization
                processed_memories = []
                for memory in memories_list:
                    if isinstance(memory, dict):
                        # Convert datetime objects to strings
                        processed_memory = {}
                        for key, value in memory.items():
                            if hasattr(value, 'isoformat'):  # datetime object
                                processed_memory[key] = value.isoformat()
                            else:
                                processed_memory[key] = value
                        processed_memories.append(processed_memory)
                    else:
                        processed_memories.append(str(memory))
                
                # Format response with detailed information
                response_data = {
                    'success': True,
                    'message': f"Found {len(processed_memories)} relevant memor(ies)",
                    'data': {
                        'memories_count': len(processed_memories),
                        'memory_id': memory_id,
                        'namespace': namespace,
                        'query': search_query,
                        'memories': processed_memories
                    }
                }
                
                # Create a formatted text response for better readability
                try:
                    formatted_response = f"tool response: {json.dumps(response_data, ensure_ascii=False, default=str)}"
                    yield self.create_text_message(formatted_response)
                except Exception as json_error:
                    # Fallback to simple response if JSON serialization fails
                    simple_response = f"Found {len(processed_memories)} memories for query: {search_query}"
                    yield self.create_text_message(simple_response)
            else:
                yield self.create_text_message("❌ AgentCore Memory SDK not available")
                
        except Exception as e:
            logger.error(f"Search memories error: {str(e)}")
            yield self.create_text_message(f"Exception in search operation: {str(e)}")
    
    def validate_parameters(self, parameters: dict[str, Any]) -> None:
        """
        Validate the parameters
        """
        operation = parameters.get('operation')
        if not operation:
            raise ValueError("operation is required")
        
        if operation not in ['record', 'retrieve', 'search']:
            raise ValueError("operation must be one of: record, retrieve, search")
        
        if operation == 'record' and not parameters.get('information'):
            raise ValueError("information is required for record operation")
        
        if operation == 'search' and not parameters.get('search_query'):
            raise ValueError("search_query is required for search operation")

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        invoke tools
        """
        try:
            # Debug: Log received parameters
            logger.info(f"Received parameters: {list(tool_parameters.keys())}")
            
            # Check operation first
            operation = tool_parameters.get("operation")
            if not operation:
                yield self.create_text_message("❌ Please select an operation (record/retrieve/search)")
                return
            
            # Initialize Memory client if not already initialized
            if not self.memory_client:
                if not self._initialize_memory_client(tool_parameters):
                    yield self.create_text_message("❌ Failed to initialize AgentCore Memory client")
                    return

            # Get required parameters
            if not self.memory_id:
                self.memory_id = tool_parameters.get("memory_id")
                if not self.memory_id:
                    yield self.create_text_message("❌ Please provide memory_id from AWS Console")
                    return
            
            if not self.actor_id:
                self.actor_id = tool_parameters.get("actor_id")
                if not self.actor_id:
                    yield self.create_text_message("❌ Please provide actor_id")
                    return
                
            if not self.session_id:
                self.session_id = tool_parameters.get("session_id")
                if not self.session_id:
                    yield self.create_text_message("❌ Please provide session_id")
                    return
                
            # Namespace is only required for search
            if operation == "search":
                if not self.namespace:
                    self.namespace = tool_parameters.get("namespace")
                    if not self.namespace:
                        yield self.create_text_message("❌ Please provide namespace for search operation")
                        return
            else:
                # Set namespace for non-search operations if provided
                if not self.namespace:
                    self.namespace = tool_parameters.get("namespace")

            # Route to appropriate operation
            if operation == 'record':
                yield from self._record_information(tool_parameters)
            elif operation == 'retrieve':
                yield from self._retrieve_history(tool_parameters)
            elif operation == 'search':
                yield from self._search_memories(tool_parameters)
            else:
                yield self.create_text_message(f"❌ Unknown operation: {operation}")

        except Exception as e:
            logger.error(f"Invoke error: {str(e)}", exc_info=True)
            yield self.create_text_message(f"❌ Internal error: {str(e)}")