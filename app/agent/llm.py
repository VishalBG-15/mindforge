import json
import os
from pathlib import Path
from typing import Type, TypeVar

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ValidationError


class AgentConfigurationError(RuntimeError):
    pass


class AgentProviderError(RuntimeError):
    pass


class AgentResponseError(RuntimeError):
    pass


ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


def request_structured_response(
    system_prompt: str,
    user_prompt: str,
    response_model: Type[ResponseModel],
) -> ResponseModel:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AgentConfigurationError(
            "OPENAI_API_KEY is not configured. Add it to the environment or .env file."
        )

    try:
        client = OpenAI(api_key=api_key, timeout=45.0)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except OpenAIError as exc:
        raise AgentProviderError("The OpenAI coaching request could not be completed.") from exc

    if not response.choices:
        raise AgentResponseError("The OpenAI coaching response did not contain a completion.")
    content = response.choices[0].message.content
    if not content:
        raise AgentResponseError("The OpenAI coaching response was empty.")

    try:
        payload = json.loads(content)
        return response_model.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise AgentResponseError(
            f"The OpenAI coaching response did not match the required "
            f"{response_model.__name__} structure."
        ) from exc
