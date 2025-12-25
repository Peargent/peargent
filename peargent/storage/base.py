"""
Base classes for history management.

This module provides core interfaces and data structures for storing and retrieving
conversation history.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import os
from jinja2 import Environment, FileSystemLoader

# Initialize Jinja2 environment for templates
_templates_dir = os.path.join(os.path.dirname(__file__), "..", "_templates")
_jinja_env = Environment(loader=FileSystemLoader(_templates_dir))


class Message:
    """Represents a single message in a conversation."""

    def __init__(
        self,
        role: str,
        content: Any,
        agent: Optional[str] = None,
        tool_call: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a message.

        Args:
            role: Message role (user, assistant, tool, system)
            content: Message content (str or dict)
            agent: Name of agent that created this message
            tool_call: Tool call information if role is 'tool'
            metadata: Additional metadata (tokens, latency, etc.)
            message_id: Unique message identifier
            timestamp: Message timestamp
        """
        self.id = message_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.now()
        self.role = role
        self.content = content
        self.agent = agent
        self.tool_call = tool_call
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        """Convert message to dictionary format."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "role": self.role,
            "content": self.content,
            "agent": self.agent,
            "tool_call": self.tool_call,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        """Create message from dictionary format."""
        return cls(
            message_id=data.get("id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None,
            role=data["role"],
            content=data["content"],
            agent=data.get("agent"),
            tool_call=data.get("tool_call"),
            metadata=data.get("metadata", {})
        )


class Thread:
    """Represents a conversation thread with multiple messages."""

    def __init__(
        self,
        thread_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize a thread.

        Args:
            thread_id: Unique thread identifier
            metadata: Thread metadata (user_id, tags, etc.)
            created_at: Thread creation timestamp
            updated_at: Last update timestamp
        """
        self.id = thread_id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.metadata = metadata or {}
        self.messages: List[Message] = []

    def add_message(self, message: Message):
        """Add a message to the thread."""
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_messages(self, role: Optional[str] = None, agent: Optional[str] = None) -> List[Message]:
        """
        Get messages filtered by role or agent.

        Args:
            role: Filter by message role
            agent: Filter by agent name

        Returns:
            List of filtered messages
        """
        messages = self.messages
        if role:
            messages = [m for m in messages if m.role == role]
        if agent:
            messages = [m for m in messages if m.agent == agent]
        return messages

    def trim_messages(self, strategy: str = "last", count: int = 10, keep_system: bool = True) -> int:
        """
        Trim messages to manage context window size.

        Args:
            strategy: "first" (keep first N), "last" (keep last N),
                     "first_last" (remove middle, keep first+last N)
            count: Number of messages to keep
            keep_system: Always preserve system messages

        Returns:
            Number of messages removed
        """
        if count >= len(self.messages):
            return 0

        system_messages = []
        non_system_messages = []

        if keep_system:
            for msg in self.messages:
                if msg.role == "system":
                    system_messages.append(msg)
                else:
                    non_system_messages.append(msg)
        else:
            non_system_messages = self.messages[:]

        initial_count = len(non_system_messages)

        if strategy == "last":
            # Keep last N messages
            non_system_messages = non_system_messages[-count:]
        elif strategy == "first":
            # Keep first N messages
            non_system_messages = non_system_messages[:count]
        elif strategy == "first_last":
            # Keep first N/2 and last N/2
            half = count // 2
            first_part = non_system_messages[:half]
            last_part = non_system_messages[-(count - half):]
            non_system_messages = first_part + last_part

        # Reconstruct messages list
        self.messages = system_messages + non_system_messages
        self.updated_at = datetime.now()

        return initial_count - len(non_system_messages)

    def delete_message(self, message_id: str) -> bool:
        """
        Delete a specific message by ID.

        Args:
            message_id: ID of message to delete

        Returns:
            True if deleted, False if not found
        """
        initial_length = len(self.messages)
        self.messages = [m for m in self.messages if m.id != message_id]

        if len(self.messages) < initial_length:
            self.updated_at = datetime.now()
            return True
        return False

    def delete_messages(self, message_ids: List[str]) -> int:
        """
        Delete multiple messages by IDs.

        Args:
            message_ids: List of message IDs to delete

        Returns:
            Number of messages deleted
        """
        initial_length = len(self.messages)
        id_set = set(message_ids)
        self.messages = [m for m in self.messages if m.id not in id_set]

        deleted_count = initial_length - len(self.messages)
        if deleted_count > 0:
            self.updated_at = datetime.now()
        return deleted_count

    def summarize_messages(self, model: Any, start_index: int = 0, end_index: Optional[int] = None, keep_recent: int = 5) -> Message:
        """
        Summarize a range of messages using an LLM and replace them with a summary.

        This is useful for managing long conversations while preserving context.
        Similar to LangChain's SummarizationMiddleware.

        Args:
            model: LLM model instance with a generate() method
            start_index: Index to start summarizing from (default: 0)
            end_index: Index to stop summarizing at (default: len-keep_recent)
            keep_recent: Number of recent messages to keep unsummarized (default: 5)

        Returns:
            The summary Message object

        Example:
            thread.summarize_messages(model, keep_recent=10)
            # Summarizes all but the last 10 messages
        """
        if end_index is None:
            end_index = max(0, len(self.messages) - keep_recent)

        if start_index >= end_index:
            raise ValueError("start_index must be less than end_index")

        messages_to_summarize = self.messages[start_index:end_index]

        if not messages_to_summarize:
            raise ValueError("No messages to summarize")

        # Build conversation text
        conversation_text = []
        for msg in messages_to_summarize:
            if msg.role == "tool":
                tool_name = msg.tool_call.get("name", "unknown") if msg.tool_call else "unknown"
                tool_output = msg.content
                conversation_text.append(f"[Tool: {tool_name}] {tool_output}")
            else:
                conversation_text.append(f"[{msg.role.capitalize()}] {msg.content}")

        conversation_str = "\n".join(conversation_text)

        # Generate summary using template
        template = _jinja_env.get_template("summarization_prompt.j2")
        summary_prompt = template.render(conversation_text=conversation_str)

        summary_content = model.generate(summary_prompt)

        # Create summary message
        summary_message = Message(
            role="system",
            content=f"[Summary of {len(messages_to_summarize)} messages]\n{summary_content}",
            metadata={
                "type": "summary",
                "original_message_count": len(messages_to_summarize),
                "summarized_at": datetime.now().isoformat()
            }
        )

        # Replace messages with summary
        before = self.messages[:start_index]
        after = self.messages[end_index:]
        self.messages = before + [summary_message] + after
        self.updated_at = datetime.now()

        return summary_message

    def to_dict(self) -> Dict:
        """Convert thread to dictionary format."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "messages": [msg.to_dict() for msg in self.messages]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Thread":
        """Create thread from dictionary format."""
        thread = cls(
            thread_id=data.get("id"),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None
        )
        thread.messages = [Message.from_dict(msg) for msg in data.get("messages", [])]
        return thread


class HistoryStore(ABC):
    """Abstract base class for history storage backends."""

    @abstractmethod
    def create_thread(self, metadata: Optional[Dict] = None) -> str:
        """
        Create a new conversation thread.

        Args:
            metadata: Thread metadata

        Returns:
            Thread ID
        """
        pass

    @abstractmethod
    def get_thread(self, thread_id: str) -> Optional[Thread]:
        """
        Retrieve a thread by ID.

        Args:
            thread_id: Thread identifier

        Returns:
            Thread object or None if not found
        """
        pass

    @abstractmethod
    def append_message(
        self,
        thread_id: str,
        role: str,
        content: Any,
        agent: Optional[str] = None,
        tool_call: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Message:
        """
        Append a message to a thread.

        Args:
            thread_id: Thread identifier
            role: Message role
            content: Message content
            agent: Agent name
            tool_call: Tool call information
            metadata: Message metadata

        Returns:
            Created message
        """
        pass

    @abstractmethod
    def get_messages(self, thread_id: str) -> List[Message]:
        """
        Get all messages in a thread.

        Args:
            thread_id: Thread identifier

        Returns:
            List of messages
        """
        pass

    @abstractmethod
    def list_threads(self) -> List[str]:
        """
        List all thread IDs.

        Returns:
            List of thread IDs
        """
        pass

    @abstractmethod
    def delete_thread(self, thread_id: str) -> bool:
        """
        Delete a thread.

        Args:
            thread_id: Thread identifier

        Returns:
            True if deleted, False if not found
        """
        pass


class FunctionalHistoryStore(HistoryStore):
    """
    Function-based history storage backend.

    This allows users to create custom storage backends by providing simple functions
    instead of subclassing HistoryStore. Perfect for quick prototypes or simple backends.

    Example:
        >>> import json
        >>> threads = {}
        >>>
        >>> def my_create_thread(metadata=None):
        ...     thread = Thread(metadata=metadata)
        ...     threads[thread.id] = thread
        ...     return thread.id
        >>>
        >>> def my_get_thread(thread_id):
        ...     return threads.get(thread_id)
        >>>
        >>> def my_append_message(thread_id, role, content, **kwargs):
        ...     thread = threads.get(thread_id)
        ...     if not thread:
        ...         raise ValueError(f"Thread {thread_id} not found")
        ...     msg = Message(role=role, content=content, **kwargs)
        ...     thread.add_message(msg)
        ...     return msg
        >>>
        >>> def my_get_messages(thread_id):
        ...     thread = threads.get(thread_id)
        ...     return thread.messages if thread else []
        >>>
        >>> def my_list_threads():
        ...     return list(threads.keys())
        >>>
        >>> def my_delete_thread(thread_id):
        ...     return threads.pop(thread_id, None) is not None
        >>>
        >>> # Create store with your functions
        >>> store = FunctionalHistoryStore(
        ...     create_thread_fn=my_create_thread,
        ...     get_thread_fn=my_get_thread,
        ...     append_message_fn=my_append_message,
        ...     get_messages_fn=my_get_messages,
        ...     list_threads_fn=my_list_threads,
        ...     delete_thread_fn=my_delete_thread
        ... )
        >>>
        >>> # Use with ConversationHistory
        >>> history = ConversationHistory(store=store)
    """

    def __init__(
        self,
        create_thread_fn,
        get_thread_fn,
        append_message_fn,
        get_messages_fn,
        list_threads_fn,
        delete_thread_fn
    ):
        """
        Initialize functional storage backend.

        Args:
            create_thread_fn: Function(metadata: Optional[Dict]) -> str
            get_thread_fn: Function(thread_id: str) -> Optional[Thread]
            append_message_fn: Function(thread_id: str, role: str, content: Any,
                                        agent: Optional[str], tool_call: Optional[Dict],
                                        metadata: Optional[Dict]) -> Message
            get_messages_fn: Function(thread_id: str) -> List[Message]
            list_threads_fn: Function() -> List[str]
            delete_thread_fn: Function(thread_id: str) -> bool
        """
        self._create_thread_fn = create_thread_fn
        self._get_thread_fn = get_thread_fn
        self._append_message_fn = append_message_fn
        self._get_messages_fn = get_messages_fn
        self._list_threads_fn = list_threads_fn
        self._delete_thread_fn = delete_thread_fn

    def create_thread(self, metadata: Optional[Dict] = None) -> str:
        """Create a new conversation thread using provided function."""
        return self._create_thread_fn(metadata=metadata)

    def get_thread(self, thread_id: str) -> Optional[Thread]:
        """Retrieve a thread by ID using provided function."""
        return self._get_thread_fn(thread_id)

    def append_message(
        self,
        thread_id: str,
        role: str,
        content: Any,
        agent: Optional[str] = None,
        tool_call: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Message:
        """Append a message to a thread using provided function."""
        return self._append_message_fn(
            thread_id=thread_id,
            role=role,
            content=content,
            agent=agent,
            tool_call=tool_call,
            metadata=metadata
        )

    def get_messages(self, thread_id: str) -> List[Message]:
        """Get all messages in a thread using provided function."""
        return self._get_messages_fn(thread_id)

    def list_threads(self) -> List[str]:
        """List all thread IDs using provided function."""
        return self._list_threads_fn()

    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread using provided function."""
        return self._delete_thread_fn(thread_id)
