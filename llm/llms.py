import os
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables from .env file
load_dotenv()


# --- LLM Provider Functions (CrewAI best practices) ---
def get_openai_llm(model, temperature):
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1/")
    return LLM(
        model=model,
        temperature=temperature,
        api_key=api_key,
        base_url=api_base,
    )


def get_groq_llm(model, temperature):
    api_key = os.getenv("GROQ_API_KEY")
    return LLM(
        model=model,
        temperature=temperature,
        api_key=api_key,
    )


def get_ollama_llm(model, temperature):
    host = os.getenv("OLLAMA_HOST")
    return LLM(
        model=model,
        temperature=temperature,
        base_url=host,
    )


def get_gemini_llm(model, temperature):
    api_key = os.getenv("GEMINI_API_KEY")
    return LLM(
        model=model,
        temperature=temperature,
        api_key=api_key,
    )


def gpt_4_1_mini(temperature=0.7):
    return get_openai_llm("openai/gpt-4.1-mini", temperature)


def gpt_4_1_nano(temperature=0.7):
    return get_openai_llm("openai/gpt-4.1-nano", temperature)


def gemini_2_0_flash(temperature=0.7):
    return get_gemini_llm("gemini/gemini-2.0-flash", temperature)


def gemini_2_0_flash_lite(temperature=0.7):
    return get_gemini_llm("gemini/gemini-2.0-flash-lite", temperature)


def deepseek_r1_8b_ollama(temperature=0.7):
    return get_ollama_llm("ollama/deepseek-r1:8b", temperature)


def deepseek_r1_8b_groq(temperature=0.7):
    return get_groq_llm("groq/deepseek-r1:8b", temperature)


def llama3_3_ollama(temperature=0.7):
    return get_ollama_llm("ollama/llama3.3:latest", temperature)


def llama3_3_groq(temperature=0.7):
    return get_groq_llm("groq/llama3.3:latest", temperature)
