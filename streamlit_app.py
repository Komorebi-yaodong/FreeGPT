import asyncio
import streamlit as st
import g4f
from g4f.Provider import ProviderUtils

from g4f.models import ModelUtils,_all_models



########################### 一些样式 ###########################

button_style1 = """
    <style>
        .stButton>button {
            font-size: 12px;
            padding: 8px 35px;
        }
    </style>
"""
st.markdown(button_style1, unsafe_allow_html=True)
########################### 初始参数 ###########################
if "models_list" not in st.session_state:
    st.session_state._models_str = _all_models
    st.session_state.models_list = ModelUtils.convert
if "providers_list" not in st.session_state:
    st.session_state._providers_str = list(ProviderUtils.convert.keys())

    st.session_state.providers_list = ProviderUtils.convert

if "model" not in st.session_state:
    st.session_state["model"] = st.session_state._models_str[0]
    st.session_state["temperature"] = 1.0
    st.session_state["max_tokens"] = 1000
    st.session_state["memory"] = True
    st.session_state["g4fmodel"] = st.session_state.models_list[st.session_state["model"]]
    st.session_state["provider"] = st.session_state.providers_list[st.session_state._providers_str[0]]
    st.session_state["providers_available"] = st.session_state._providers_str
    st.session_state["stream"] = True
    st.session_state["chat"] = True
if "session" not in st.session_state:
    st.session_state["session"] = []
if "sys_prompt" not in st.session_state:
    st.session_state["sys_prompt"] = "You are an AI assistant."
if "dialogue_history" not in st.session_state:
    st.session_state["dialogue_history"] = [{'role':'system','content':st.session_state.sys_prompt},]

########################### function ###########################
header =  st.empty()
header.write("<h2> Chat-"+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
show_talk = st.container()
show_test = st.container()

def chatg4f(message,dialogue_history,session,stream=st.session_state["stream"],model=st.session_state.g4fmodel,provider=st.session_state.provider,temperature=st.session_state.temperature,max_tokens=st.session_state.max_tokens):
    # 将当前消息添加到对话历史中
    session.append(message)
    dialogue_history.append(message)
    # 发送请求给 OpenAI GPT
    if stream:
        response = g4f.ChatCompletion.create(
            model=model,
            provider = provider,
            messages=dialogue_history,
            temperature=temperature, # 控制模型输出的随机程度
            max_tokens=max_tokens,  # 控制生成回复的最大长度
            stream=stream
        )
    else:
        response = g4f.ChatCompletion.create(
            model=model,
            provider = provider,
            messages=dialogue_history,
            temperature=temperature, # 控制模型输出的随机程度
            max_tokens=max_tokens,  # 控制生成回复的最大长度
        )
    show()
    reply = {'role':'assistant','content':""}
    with show_talk.chat_message(reply['role']):
        line = st.empty()
        for message in response:
            reply['content'] += message
            line.empty()
            line.write(reply['content'])
    session.append(reply)
    if not st.session_state["memory"]:
        dialogue_history.pop()
    else:
        dialogue_history.append(reply)


def show():
    for section in st.session_state["session"]:
        with show_talk.chat_message(section['role']):
            st.write(section['content'],unsafe_allow_html=True)


########################### 侧边栏：设置、测试 ###########################


# 侧边栏
with st.sidebar:

    # 设置
    with st.container():
        with st.expander("Settings"):
            st.session_state["model"] = st.selectbox('models', st.session_state._models_str)
            provider = st.selectbox('provider', st.session_state.providers_available)
            memory = st.toggle('memory', st.session_state["memory"])
            st.session_state["stream"] =  st.toggle('stream', ["True","False"])
            temperature = st.slider('temperature', 0.0, 2.0, st.session_state["temperature"])
            max_tokens = st.text_input('max_tokens', st.session_state["max_tokens"])
            if st.button('Save'):
                st.session_state.g4fmodel = st.session_state.models_list[st.session_state["model"]]
                st.session_state.provider = st.session_state.providers_list[provider]
                st.session_state["temperature"] =temperature
                st.session_state["memory"] =memory
                st.session_state["max_tokens"] = max_tokens
                st.balloons()


    with st.container():
        sys_prompt = st.text_input('sys_prompt', st.session_state["sys_prompt"])
        if st.button('Submit'):
            st.session_state["sys_prompt"] = sys_prompt
            st.session_state["dialogue_history"].append({'role':'system','content':st.session_state["sys_prompt"]})

    with st.container():
        st.session_state["chat"] = st.toggle('Test | Chat', [True,False])

            
    with st.container():
        if st.button('Clear'):
            # 处理新文件
            st.session_state.dialogue_history = [{'role':'system','content':st.session_state.sys_prompt},]
            # 重置会话
            st.session_state["session"] = []  


########################### 聊天展示区 ###########################

if st.session_state["chat"]:
    # 用户输入区域
    prompt = st.chat_input("Send a message")
    if prompt:
        message = {"role":"user","content":prompt}
        chatg4f(message,st.session_state["dialogue_history"],st.session_state["session"])
else:
    with show_test:
        async def run_provider(content,model,provider: g4f.Provider.BaseProvider):
            try:
                response = await g4f.ChatCompletion.create_async(
                    model=model,
                    messages=[{"role": "user", "content": content}],
                    provider=provider,
                )
                st.session_state.providers_available.append(provider.__name__)
                show_test.write("***")
                show_test.write(f"**{provider.__name__}:** {response}")
                # print(f"{provider.__name__}:", response)
            except Exception as e:
                show_test.write("***")
                show_test.write(f"*{provider.__name__}*: {e}")
                # print(f"{provider.__name__}:", e)
                
        async def run_all(content,model):
            calls = [
                run_provider(content,model,provider) for provider in st.session_state.providers_list.values()
            ]
            await asyncio.gather(*calls)

        def test_provider(content,model):
            asyncio.run(run_all(content,model))
            
    header.write("<h2> Test-"+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
    content = st.chat_input("Send a test message")
    if content:
        st.session_state.providers_available = []
        test_provider(content,st.session_state.g4fmodel)
        

        
        
