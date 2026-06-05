from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model="llama3.1:8b",
    model_provider="ollama",
    base_url="https://oa1.gxlky.com.cn/ollama",
    temperature=0.1,
)

resp = llm.invoke("你好")
print(f"[直接调用] {resp.content}")