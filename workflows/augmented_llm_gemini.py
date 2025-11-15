# workflows/augmented_llm_gemini.py
"""
Deterministic Gemini LLM wrapper:
- Public methods are synchronous and deterministic.
- Async implementation lives in _chat_with_tools_async for callers that explicitly await it.
- If a public method is called while an event loop is already running, we raise a clear error
  instructing the caller to await the async API instead.
"""

import google.generativeai as genai
from typing import Dict, Any, List, Optional, Tuple
import logging
import asyncio

logger = logging.getLogger(__name__)


class GeminiAugmentedLLM:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro"):
        self.api_key = api_key
        self.model_name = model_name
        try:
            genai.configure(api_key=api_key)
        except Exception:
            logger.debug("genai.configure(...) not available; continuing.")
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception:
            self.model = model_name
        self.log = logging.getLogger(__name__)

    # --- PUBLIC synchronous wrapper ---
    def chat_with_tools(
        self,
        model: Optional[str] = None,
        system_message: str = "",
        messages: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 8192,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Synchronous public API. If called when an asyncio event loop is running in this thread,
        raise a RuntimeError telling the caller to await the async API instead.
        Otherwise run the async implementation to completion and return the dict result.
        """
        messages = messages or []
        tools = tools or []

        # If there's a running event loop in this thread, require await
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                raise RuntimeError(
                    "chat_with_tools() was called in a running asyncio event loop. "
                    "Use 'await llm._chat_with_tools_async(...)' or provide an async wrapper."
                )
        except RuntimeError:
            # get_event_loop can raise if there's no loop - treat as no loop
            pass

        # Run the async impl synchronously and return result
        return asyncio.run(
            self._chat_with_tools_async(
                model=model,
                system_message=system_message,
                messages=messages,
                tools=tools,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        )

    # Provide an explicit async API callers can use when they are in async contexts
    async def _chat_with_tools_async(
        self,
        model: Optional[str] = None,
        system_message: str = "",
        messages: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 8192,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Actual async implementation that can be awaited by async callers.
        Returns a dict: {"content": str, "tool_calls": list}
        """
        messages = messages or []
        tools = tools or []

        try:
            # resolve model object
            if model:
                try:
                    current_model = genai.GenerativeModel(model)
                except Exception:
                    current_model = model
            else:
                current_model = self.model

            # build simple prompt
            prompt_parts = []
            if system_message:
                prompt_parts.append(f"System: {system_message}")
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role}: {content}")
            if tools:
                tools_info = "Tools:\n" + "\n".join(
                    f"- {t.get('name','?')}: {t.get('description','')}" for t in tools
                )
                prompt_parts.append(tools_info)
            full_prompt = "\n\n".join(prompt_parts) or "Hello"

            # Run potentially blocking library call in executor
            def _generate():
                try:
                    if hasattr(current_model, "generate_content"):
                        # attempt to build GenerationConfig if available
                        gen_conf = None
                        try:
                            gen_types = getattr(genai, "types", genai)
                            if hasattr(gen_types, "GenerationConfig"):
                                gen_conf = gen_types.GenerationConfig(
                                    max_output_tokens=max_tokens, temperature=temperature
                                )
                        except Exception:
                            gen_conf = None

                        if gen_conf is not None:
                            return current_model.generate_content(full_prompt, generation_config=gen_conf)
                        return current_model.generate_content(full_prompt)
                    if hasattr(genai, "generate_text"):
                        return genai.generate_text(full_prompt)
                    return {"text": f"[fallback] {full_prompt}"}
                except Exception as e:
                    return {"text": f"[error] {str(e)}"}

            response = await asyncio.get_event_loop().run_in_executor(None, _generate)

            # normalize response into text
            if isinstance(response, dict):
                response_text = response.get("text") or response.get("content") or str(response)
            else:
                response_text = getattr(response, "text", None) or str(response)

            # extract very simple tool call markers
            tool_calls = []
            if tools:
                for t in tools:
                    name = t.get("name", "")
                    if name and f"{name}(" in response_text:
                        tool_calls.append({"name": name, "input": {}})

            return {"content": response_text, "tool_calls": tool_calls}

        except Exception as e:
            self.log.exception("Error in GeminiAugmentedLLM._chat_with_tools_async")
            return {"content": f"Error: {str(e)}", "tool_calls": []}

    # --- Convenience synchronous __call__ (keeps older code working) ---
    def __call__(
        self,
        model: Optional[str] = None,
        system_message: str = "",
        messages: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 8192,
        temperature: float = 0.2,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Synchronous convenience wrapper that returns (content, tool_calls).
        If called inside running loop, raise RuntimeError telling user to await _chat_with_tools_async.
        """
        result = self.chat_with_tools(
            model=model,
            system_message=system_message,
            messages=messages,
            tools=tools,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = result.get("content", "")
        tool_calls = result.get("tool_calls", [])
        return content, tool_calls
