import streamlit as st
from chatfile import collect_file,pdf_transofrm
from openai import OpenAI
import g4f
from g4f.Provider   import (
    AiChatOnline,
    OnlineGpt,
    ChatBase,
    GeekGpt,
    Hashnode,
    Liaobots,
    Phind,
    Koala,
    Bard,
)

_providers = {
    'AiChatOnline':AiChatOnline,
    'OnlineGpt':OnlineGpt,
    'Liaobots':Liaobots,
    'Hashnode':Hashnode,
    'ChatBase':ChatBase,
    'GeekGpt':GeekGpt,
    'Koala':Koala,
    'Phind':Phind,
    'Bard':Bard,
}

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
header =  st.empty()
show_talk = st.container()
if "current_file" not in st.session_state:
    st.session_state["current_file"] = "<h2 style='text-align: center; color: grey;'>"+"当前无文件"+"</h2>"
header.write(st.session_state.current_file, unsafe_allow_html=True)
if "base_url" not in st.session_state:
    st.session_state["base_url"] = ""
    st.session_state["api_key"] = ""
    st.session_state["model"] = "gpt-3.5-turbo"
    st.session_state["temperature"] = 0.7
    st.session_state["max_tokens"] = 1000
    st.session_state["memory"] = False
    st.session_state["g4fmodel"] = "gpt-3.5-turbo-16k"
    st.session_state["mode"] = "Gpt4Free"
    st.session_state["provider"] = _providers['OnlineGpt']
    st.session_state["stream"] = True
if "session" not in st.session_state:
    st.session_state["session"] = []
if "dialogue_history" not in st.session_state:
    st.session_state["dialogue_history"] = []
if "client" not in st.session_state:
    st.session_state["client"] = OpenAI(
        api_key=st.session_state.api_key,
        base_url = st.session_state.base_url,
    )

########################### function ###########################

def chatg4f(flag,message,dialogue_history,session,stream=st.session_state["stream"],model=st.session_state.g4fmodel,provider=st.session_state.provider,temperature=st.session_state.temperature,max_tokens=st.session_state.max_tokens):
    # 将当前消息添加到对话历史中
    if flag:
        session.append(message)
        dialogue_history.append(message)
    # 发送请求给 OpenAI GPT
    response = g4f.ChatCompletion.create(
        model=model,
        provider = provider,
        messages=dialogue_history,
        temperature=temperature, # 控制模型输出的随机程度
        max_tokens=max_tokens,  # 控制生成回复的最大长度
        stream=stream
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
        if flag:
            dialogue_history.pop()
        else:
            dialogue_history.append(reply)
    else:
        dialogue_history.append(reply)

def chatmd(flag,message,dialogue_history,session,model=st.session_state.model,temperature=st.session_state.temperature,max_tokens=st.session_state.max_tokens):
    # 将当前消息添加到对话历史中
    if flag:
        session.append(message)
        dialogue_history.append(message)
    # 发送请求给 OpenAI GPT
    # print(dialogue_history)
    response = st.session_state.client.chat.completions.create(
        model=model,
        messages=dialogue_history,
        temperature=temperature, # 控制模型输出的随机程度
        max_tokens=max_tokens,  # 控制生成回复的最大长度
        stream=True, # 是否是流式生成
    )
    show()
    reply = {'role':'assistant','content':""}
    with show_talk.chat_message(reply['role']):
        line = st.empty()
        for part in response:
            reply['content'] += part.choices[0].delta.content or ""
            line.empty()
            line.write(reply['content'])
    session.append(reply)
    if not st.session_state["memory"]:
        if flag:
            dialogue_history.pop()
        else:
            dialogue_history.append(reply)
    else:
        dialogue_history.append(reply)


def show():
    for section in st.session_state["session"]:
        with show_talk.chat_message(section['role']):
            st.write(section['content'],unsafe_allow_html=True)


###########################侧边栏：新的会话、历史记录、设置###########################


# 侧边栏
with st.sidebar:

    # 新的文件
    with st.container():
        new_file = st.file_uploader("选择文档")
        if new_file is not None:
            if st.button('Upload'):
                file_name,file_type = collect_file(new_file)
                st.session_state.current_file = "<h2 style='text-align: center; color: black;'>"+"Chat with "+file_name+"</h2>"
                # 处理新文件
                st.session_state["dialogue_history"]=pdf_transofrm(new_file,file_type)
                # 改变标头
                header.write(st.session_state.current_file, unsafe_allow_html=True) 
                # 重置会话
                st.session_state["session"] = []    
                # 发送给GPT
                if st.session_state.mode == "Gpt4Free":
                    chatg4f(False,None,st.session_state["dialogue_history"],st.session_state["session"])
                else:
                    chatmd(False,None,st.session_state["dialogue_history"],st.session_state["session"])
            else:
                header.write(st.session_state.current_file, unsafe_allow_html=True)
    
    # 设置
    with st.container():
        with st.expander("Settings"):
            st.session_state.mode = st.selectbox("Mode",["Gpt4Free","SelfApi"])
            if st.session_state.mode == "Gpt4Free":
                g4fmodel = st.selectbox('models', ["gpt_35_long","gpt_35_turbo_16k_0613","gpt-4"])
                providers = st.selectbox('provider', ['OnlineGpt','GeekGpt','ChatBase','AiChatOnline','Bard','Liaobots','Phind','Koala','Hashnode'])
                memory = st.toggle('memory', st.session_state["memory"])
                temperature = st.slider('temperature', 0.0, 1.0, st.session_state["temperature"])
                max_tokens = st.text_input('max_tokens', st.session_state["max_tokens"])
                if st.button('Save'):
                    if g4fmodel == "gpt-4":
                        st.session_state.g4fmodel = g4f.models.gpt_4
                    elif g4fmodel == "gpt_35_turbo_16k_0613":
                        st.session_state.g4fmodel = g4f.models.gpt_35_turbo_16k_0613
                    else:
                        st.session_state.g4fmodel = g4f.models.gpt_35_long
                    st.session_state["provider"] =_providers[providers]
                    if providers == "Bard":
                        st.session_state["stream"] = False
                    else:
                        st.session_state["stream"] = True
                    st.session_state["temperature"] =temperature
                    st.session_state["memory"] =memory
                    st.session_state["max_tokens"] = max_tokens
                    st.balloons()
            else:
                base_url = st.text_input('base url', st.session_state["base_url"])
                api_key = st.text_input('api-key', st.session_state["api_key"])
                model = st.text_input('model', st.session_state["model"])
                memory = st.toggle('memory', st.session_state["memory"])
                temperature = st.slider('temperature', 0.0, 1.0, st.session_state["temperature"])
                max_tokens = st.text_input('max_tokens', st.session_state["max_tokens"])
                if st.button('Save'):
                    st.session_state["base_url"] =base_url
                    st.session_state["api_key"] = api_key
                    st.session_state["model"] =model
                    st.session_state["temperature"] =temperature
                    st.session_state["max_tokens"] = max_tokens
                    st.session_state["memory"] =memory
                    st.session_state.client = OpenAI(
                        api_key=st.session_state.api_key,
                        base_url = st.session_state.base_url,
                    )
                    st.balloons()
    with st.container():
        if st.button('Clear'):
            st.session_state["current_file"] = "<h2 style='text-align: center; color: grey;'>"+"当前无文件"+"</h2>"
            # 处理新文件
            st.session_state["dialogue_history"]=[]
            # 改变标头
            header.write(st.session_state.current_file, unsafe_allow_html=True) 
            # 重置会话
            st.session_state["session"] = []  


###########################聊天区域###########################

# 用户输入区域
with st.container(): 
    prompt = st.chat_input("Send a message")
    if prompt:
        message = {"role":"user","content":prompt}
        if st.session_state.mode == "Gpt4Free":
            chatg4f(True,message,st.session_state["dialogue_history"],st.session_state["session"])
        else:
            chatmd(True,message,st.session_state["dialogue_history"],st.session_state["session"])

