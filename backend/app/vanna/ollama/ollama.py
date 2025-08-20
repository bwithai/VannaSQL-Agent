import json
import re

from httpx import Timeout

from ..base import VannaBase
from ..exceptions import DependencyError


class Ollama(VannaBase):
  def __init__(self, config=None):

    try:
      ollama = __import__("ollama")
    except ImportError:
      raise DependencyError(
        "You need to install required dependencies to execute this method, run command:"
        " \npip install ollama"
      )

    if not config:
      raise ValueError("config must contain at least Ollama model")
    if 'model' not in config.keys():
      raise ValueError("config must contain at least Ollama model")
    self.host = config.get("ollama_host", "http://localhost:11434")
    self.model = config["model"]
    if ":" not in self.model:
      self.model += ":latest"

    self.ollama_timeout = config.get("ollama_timeout", 240.0)

    self.ollama_client = ollama.Client(self.host, timeout=Timeout(self.ollama_timeout))
    self.keep_alive = config.get('keep_alive', None)
    self.ollama_options = config.get('options', {})
    self.num_ctx = self.ollama_options.get('num_ctx', 2048)
    self.__pull_model_if_ne(self.ollama_client, self.model)

  @staticmethod
  def __pull_model_if_ne(ollama_client, model):
    model_response = ollama_client.list()
    model_lists = [model_element['model'] for model_element in
                   model_response.get('models', [])]
    if model not in model_lists:
      ollama_client.pull(model)

  def system_message(self, message: str) -> any:
    return {"role": "system", "content": message}

  def user_message(self, message: str) -> any:
    return {"role": "user", "content": message}

  def assistant_message(self, message: str) -> any:
    return {"role": "assistant", "content": message}

  def extract_sql(self, llm_response):
    """
    Extracts the first SQL statement after the word 'select', ignoring case,
    matches until the first semicolon, three backticks, or the end of the string,
    and removes three backticks if they exist in the extracted string.

    Args:
    - llm_response (str): The string to search within for an SQL statement.

    Returns:
    - str: The first SQL statement found, with three backticks removed, or an empty string if no match is found.
    """
    # Remove ollama-generated extra characters
    llm_response = llm_response.replace("\\_", "_")
    llm_response = llm_response.replace("\\", "")

    # Regular expression to find ```sql' and capture until '```'
    sql = re.search(r"```sql\n((.|\n)*?)(?=;|\[|```)", llm_response, re.DOTALL)
    # Regular expression to find 'select, with (ignoring case) and capture until ';', [ (this happens in case of mistral) or end of string
    select_with = re.search(r'(select|(with.*?as \())(.*?)(?=;|\[|```)',
                            llm_response,
                            re.IGNORECASE | re.DOTALL)
    if sql:
      self.log(
        f"Output from LLM: {llm_response} \nExtracted SQL: {sql.group(1)}")
      return sql.group(1).replace("```", "")
    elif select_with:
      self.log(
        f"Output from LLM: {llm_response} \nExtracted SQL: {select_with.group(0)}")
      return select_with.group(0)
    else:
      return llm_response

  def submit_prompt(self, prompt, **kwargs) -> str:
    self.log(
      f"Ollama parameters:\n"
      f"model={self.model},\n"
      f"options={self.ollama_options},\n"
      f"keep_alive={self.keep_alive}")
    self.log(f"Prompt Content:\n{json.dumps(prompt, ensure_ascii=False)}")
    
    # Check if streaming is requested
    stream = kwargs.get('stream', False)
    think = kwargs.get('think', False)
    
    if stream:
      # Return streaming generator for real-time responses
      return self._submit_prompt_stream(prompt, think=think)
    
    response_dict = self.ollama_client.chat(model=self.model,
                                            messages=prompt,
                                            stream=False,
                                            options=self.ollama_options,
                                            keep_alive=self.keep_alive,
                                            think=think if self._supports_thinking() else False)

    self.log(f"Ollama Response:\n{str(response_dict)}")

    return response_dict['message']['content']

  def _supports_thinking(self) -> bool:
    """Check if the current model supports thinking mode."""
    thinking_models = [
      'qwen3:4b', 'qwen3:8b'
    ]
    return any(model in self.model.lower() for model in thinking_models)

  def _submit_prompt_stream(self, prompt, think=False):
    """Submit prompt with streaming support for real-time thinking."""
    try:
      # Only enable thinking for supported models
      use_thinking = think and self._supports_thinking()
      
      stream = self.ollama_client.chat(
        model=self.model,
        messages=prompt,
        stream=True,
        options=self.ollama_options,
        keep_alive=self.keep_alive,
        think=use_thinking
      )
      
      thinking_complete = False
      full_response = ""
      
      for chunk in stream:
        chunk_data = {
          'type': 'chunk',
          'thinking': None,
          'content': None,
          'thinking_complete': thinking_complete
        }
        
        # Handle thinking content
        if (hasattr(chunk, 'message') and hasattr(chunk.message, 'thinking') 
            and chunk.message.thinking and not thinking_complete):
          chunk_data['type'] = 'thinking'
          chunk_data['thinking'] = chunk.message.thinking
          yield chunk_data
        
        # Handle response content
        if (hasattr(chunk, 'message') and hasattr(chunk.message, 'content') 
            and chunk.message.content):
          if not thinking_complete:
            thinking_complete = True
            chunk_data['thinking_complete'] = True
            chunk_data['type'] = 'thinking_end'
            yield chunk_data
          
          chunk_data['type'] = 'content'
          chunk_data['content'] = chunk.message.content
          full_response += chunk.message.content
          yield chunk_data
      
      # Send final completion signal
      yield {
        'type': 'complete',
        'full_response': full_response,
        'thinking_complete': thinking_complete
      }
      
    except Exception as e:
      self.log(f"Error in streaming: {e}")
      yield {
        'type': 'error',
        'error': str(e)
      }
