import time
from sentry_sdk.ai.monitoring import ai_track, record_token_usage
import sentry_sdk
import requests
from openai import OpenAI

sentry_sdk.init(
    dsn="https://0262ca3cbbad6fe8b7f84e4f216cb352@sentry-dev.ru.tuna.am/2",
    send_default_pii=True,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    _experiments={
        "enable_logs": True,
    },
)


@ai_track("AI tool")
def some_workload_function(**kwargs):
    """
    This function is an example of calling arbitrary code with @ai_track so that it shows up in the Sentry trace
    """
    time.sleep(5)

@ai_track("LLM")
def some_llm_call():
    """
    This function is an example of calling an LLM provider that isn't officially supported by Sentry.
    """
    with sentry_sdk.start_span(op="ai.chat_completions.create.examplecom", name="Example.com LLM") as span:
        result = requests.get('https://example.com/api/llm-chat?question=say+hello').json()
        # this annotates the tokens used by the LLM so that they show up in the graphs in the dashboard
        record_token_usage(span, total_tokens=result["usage"]["total_tokens"])
        return result["text"]

@ai_track("My AI pipeline")
def some_pipeline():
    """
    The topmost level function with @ai_track gets the operation "ai.pipeline", which makes it show up
    in the table of AI pipelines in the Sentry LLM Monitoring dashboard.
    """
    client = OpenAI(
        model="gpt-4.1-nano", 
        temperature=0.1, 
        api_base='https://api.aitunnel.ru/v1/', 
        api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI'
    )
    # Data can be passed to the @ai_track annotation to include metadata
    some_workload_function(sentry_tags={"username": "artem"}, sentry_data={"data": "some longer data that provides context"})
    some_llm_call()
    response = (
        client.chat.completions.create(
            model="gpt-4.1-nano", messages=[{"role": "system", "content": "say hello"}]
        )
        .choices[0]
        .message.content
    )
    print(response)

with sentry_sdk.start_transaction(op="ai-inference", name="The result of the AI inference"):
    some_pipeline()

