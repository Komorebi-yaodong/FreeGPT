import streamlit as st
from chatfile import collect_file,change_config,get_config,file_transform,get_file,delete_file,get_history
from openai import OpenAI


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
if "config_path" not in st.session_state:
    st.session_state["config_path"] = "./config.json"
if "base_url" not in st.session_state:
    st.session_state["base_url"],st.session_state["api_key"],st.session_state["model"],st.session_state["temperature"],st.session_state["data_path"],st.session_state["sys_content"],st.session_state["max_tokens"],st.session_state["memory"] = get_config(st.session_state["config_path"])
if "session" not in st.session_state:
    st.session_state["session"] = []
if "dialogue_history" not in st.session_state:
    st.session_state["dialogue_history"] = []
if "history" not in st.session_state:
    st.session_state["history"] = get_history(st.session_state["data_path"])

########################### function ###########################
if "client" not in st.session_state:
    st.session_state["client"] = OpenAI(
        api_key=st.session_state.api_key,
        base_url = st.session_state.base_url,
    )


def chatmd(flag,message,dialogue_history,session,model=st.session_state.model,temperature=st.session_state.temperature,max_tokens=st.session_state.max_tokens):
    # 将当前消息添加到对话历史中
    if flag:
        session.append(message)
        dialogue_history.append(message)
    # 发送请求给 OpenAI GPT
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


def show():
    print(len(st.session_state["session"]))
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
                st.session_state["dialogue_history"]=file_transform(new_file,file_name,file_type,st.session_state["data_path"],st.session_state["sys_content"])
                # 历史文件改变
                st.session_state["history"] = get_history(st.session_state["data_path"])
                # 改变标头
                header.write(st.session_state.current_file, unsafe_allow_html=True) 
                # 重置会话
                st.session_state["session"] = []             
                # 发送给GPT
                end_message = "文章已发送完毕，接下来我将提出一些与文章相关的问题，请你使用中文，根据内容以markdown格式进行回答，我的第一个问题是'Summarize the main content of the article.'"
                end_message = {'role':'user','content':end_message}
                chatmd(False,end_message,st.session_state["dialogue_history"],st.session_state["session"])
            else:
                header.write(st.session_state.current_file, unsafe_allow_html=True)
    
    # 历史文件
    with st.container():
        with st.expander("History"):
            if st.button("Update"):
                st.session_state["history"] = get_history(st.session_state["data_path"])
                with st.container():
                    choose_file = st.selectbox(
                        '你可以选择以下历史文件',
                        st.session_state["history"])
                    if choose_file:
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("√"):
                                st.session_state.current_file = "<h2 style='text-align: center; color: black;'>"+"Chat with "+choose_file+"</h2>"
                                # 处理新文件
                                st.session_state["dialogue_history"]=get_file(choose_file,st.session_state["data_path"])
                                # 历史文件改变
                                st.session_state["history"] = get_history(st.session_state["data_path"])
                                # 改变标头
                                header.write(st.session_state.current_file, unsafe_allow_html=True) 
                                # 重置会话
                                st.session_state["session"] = []             
                                # 发送给GPT
                                end_message = "文章已发送完毕，接下来我将提出一些与文章相关的问题，请你使用中文，根据内容以markdown格式进行回答，我的第一个问题是'Summarize the main content of the article.'"
                                end_message = {'role':'user','content':end_message}
                                chatmd(False,end_message,st.session_state["dialogue_history"],st.session_state["session"])
                        with col2:
                            if st.button("X"):
                                if choose_file == st.session_state.current_file:
                                    st.session_state.current_file = "<h2 style='text-align: center; color: grey;'>"+"当前无文件"+"</h2>"
                                    st.session_state["history"] = []
                                    header.write(st.session_state.current_file, unsafe_allow_html=True) 
                                    st.session_state["session"] = []
                                st.session_state["history"] = get_history(st.session_state["data_path"])
                                delete_file(choose_file,st.session_state["data_path"])
            else:
                with st.container():
                    choose_file = st.selectbox(
                        '你可以选择以下历史文件',
                        st.session_state["history"])
                    if choose_file:
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("√"):
                                st.session_state.current_file = "<h2 style='text-align: center; color: black;'>"+"Chat with "+choose_file+"</h2>"
                                # 处理新文件
                                st.session_state["dialogue_history"]=get_file(choose_file,st.session_state["data_path"])
                                # 历史文件改变
                                st.session_state["history"] = get_history(st.session_state["data_path"])
                                # 改变标头
                                header.write(st.session_state.current_file, unsafe_allow_html=True) 
                                # 重置会话
                                st.session_state["session"] = []             
                                # 发送给GPT
                                end_message = "文章已发送完毕，接下来我将提出一些与文章相关的问题，请你使用中文，根据内容以markdown格式进行回答，我的第一个问题是'Summarize the main content of the article.'"
                                end_message = {'role':'user','content':end_message}
                                chatmd(False,end_message,st.session_state["dialogue_history"],st.session_state["session"])
                        with col2:
                            if st.button("X"):
                                if choose_file == st.session_state.current_file:
                                    st.session_state.current_file = "<h2 style='text-align: center; color: grey;'>"+"当前无文件"+"</h2>"
                                    st.session_state["history"] = []
                                    header.write(st.session_state.current_file, unsafe_allow_html=True) 
                                    st.session_state["session"] = []
                                st.session_state["history"] = get_history(st.session_state["data_path"])
                                delete_file(choose_file,st.session_state["data_path"])
    
    # 设置
    with st.container():
        with st.expander("Settings"):

            base_url = st.text_input('base url', st.session_state["base_url"])
            api_key = st.text_input('api-key', st.session_state["api_key"])
            model = st.text_input('model', st.session_state["model"])
            temperature = st.slider('temperature', 0.0, 1.0, st.session_state["temperature"])
            memory = st.toggle('memory', st.session_state["memory"])
            if st.button('Save'):
                st.session_state["base_url"] =base_url
                st.session_state["api_key"] = api_key
                st.session_state["model"] =model
                st.session_state["temperature"] =temperature
                st.session_state["memory"] =memory
                st.session_state["client"] = OpenAI(
                    api_key=st.session_state.api_key,
                    base_url = st.session_state.base_url,
                )
                flag = change_config(st.session_state["config_path"],st.session_state["base_url"],st.session_state["api_key"],st.session_state["model"],st.session_state["temperature"],st.session_state["memory"])
                if flag:
                    st.balloons()


###########################聊天区域###########################

# 用户输入区域
with st.container(): 
    prompt = st.chat_input("Send a message")
    if prompt:
        message = {"role":"user","content":prompt}
        chatmd(True,message,st.session_state["dialogue_history"],st.session_state["session"])
        # show()

