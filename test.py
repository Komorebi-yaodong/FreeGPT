from langchain.text_splitter import RecursiveCharacterTextSplitter
from g4f.models import ModelUtils,_all_models
from g4f.Provider import ProviderUtils
from bs4 import BeautifulSoup
from docx import Document
import streamlit as st
import requests
import asyncio
import PyPDF2
import g4f
import re


class GoogleSearchExtractor:
    def __init__(self,api_key,cse_id,num_link=3,timeout_seconds=10) -> None:
        self.api_key = api_key
        self.cse_id = cse_id
        self.num_links = num_link
        self.timeout_seconds = timeout_seconds

    def google_search(self,query):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q":query,
            "key":self.api_key,
            "cx":self.cse_id,
        }
        resopnse = requests.get(url,params=params)
        return resopnse.json()
    
    def clean_text(self,text):
        return re.sub(r'\s+', ' ', text).strip()
    
    def extract_contents(self,query):
        results = self.google_search(query)
        inner = []
        for item in results["items"][:self.num_links]:
            url = item['link']

            try:
                response = requests.get(url, timeout=self.timeout_seconds)
                if response.status_code == 200:
                    encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None

                    # 使用BeautifulSoup解析HTML
                    soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)

                    # 使用get_text()方法提取所有文本内容
                    text_content = soup.get_text()
                    # 清理文本
                    cleaned_text = self.clean_text(text_content)
                    inner.append(cleaned_text)
                    # 打印提取的文本内容
                else:
                    print(f"无法访问网页：{url}")
            except requests.Timeout:
                print(f"请求超时，超过了{self.timeout_seconds}秒的等待时间。链接：{url}")

        return inner
    

if "models_list" not in st.session_state:
    st.session_state._models_str = _all_models
    st.session_state.models_list = ModelUtils.convert
if "providers_list" not in st.session_state:
    st.session_state._providers_str = list(ProviderUtils.convert.keys())
    st.session_state.providers_list = ProviderUtils.convert
if "model" not in st.session_state:
    st.session_state["model"] = st.session_state._models_str[0]
    st.session_state["temperature"] = 0.8
    st.session_state["max_tokens"] = 2000
    st.session_state["memory"] = True
    st.session_state["g4fmodel"] = st.session_state.models_list[st.session_state["model"]]
    st.session_state["provider"] = st.session_state.providers_list[st.session_state._providers_str[0]]
    st.session_state["providers_available"] = st.session_state._providers_str
    st.session_state["stream"] = True
    st.session_state["mode"] = "**🚀introudce**"
if "session" not in st.session_state:
    st.session_state["session"] = []
if "sys_prompt" not in st.session_state:
    st.session_state["sys_prompt"] = ""
if "dialogue_history" not in st.session_state:
    st.session_state["dialogue_history"] = []
if "introduce" not in st.session_state:
    with open("./README.md","r",encoding="utf-8") as f:
        st.session_state.introduce = f.read()
if "web_catcher" not in st.session_state:
    st.session_state.web_catcher = GoogleSearchExtractor(st.secrets.google_key,st.secrets.cse_id)

########################### element ###########################


header =  st.empty()
header.write("<h2> 🤖 "+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
show_talk = st.container()
show_test = st.container()
show_introduce = st.container()

########################### function ###########################


def collect_file(file_upload):
    file_name = ".".join(file_upload.name.split('.')[0:-1])
    file_type = file_upload.name.split('.')[-1]

    return file_name,file_type


def get_text(file,type):
    
    def extract_text_from_docx(file):
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def extract_text_from_pdf(file):
        pdf = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text += page.extract_text()
            
        return text
    
    # 文件类型判断
    if type == 'pdf':
        text = extract_text_from_pdf(file)
    elif type == 'docx':
        text = extract_text_from_docx(file)
    elif type == 'txt' or type == 'md' or type == 'py' or type == 'c' or type == 'cpp' or type == 'js':
        text = file.getvalue().decode("utf-8")
    else:
        print("The file type is not supported.(only pdf, docx, txt, md supported)")
        return []
    
    return text


def get_splitted_text(text):
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=0
    )
    return r_splitter.split_text(text)


@st.cache_data
def get_file_reader(file,type):
    sys_content = "You are a file reading bot. Next, the user will send an file. After reading, you should fully understand the content of the file and be able to analyze, interpret, and respond to questions related to the file in both Chinese and Markdown formats. Answer step-by-step."
    end_file_message = "File sent. Next, please reply in Chinese and format your response using markdown based on the content.'"
    dialogue_history = [{'role':'system','content':sys_content},]
    
    # 文本提取并拆分
    text = get_text(file,type)
    text_list = get_splitted_text(text)
    pages = len(text_list)
    start_message = f"我现在会将文章的内容分 {len(text_list)} 部分发送给你。请确保你已经准备好接收，接收到文章发送完毕的指令后，请准备回答我的问题。"
    dialogue_history.append({'role':'user','content':start_message})

    # 分段输入
    for i in range(pages):
        text_message = {'role':'user','content':text_list[i]}
        dialogue_history.append(text_message)
    
    # 结束文本输入
    end_message = {'role':'user','content':end_file_message}
    dialogue_history.append(end_message)

    return dialogue_history


def gpt_resopnse(model,provider,dialogue_history,temperature,max_tokens,stream):
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
    return response

def chatg4f(message,dialogue_history,session,stream=st.session_state["stream"],model=st.session_state.g4fmodel,provider=st.session_state.provider,temperature=st.session_state.temperature,max_tokens=st.session_state.max_tokens):
    # 将当前消息添加到对话历史中
    session.append(message)
    dialogue_history.append(message)
    # 发送请求给 OpenAI GPT
    response = gpt_resopnse(model,provider,dialogue_history,temperature,max_tokens,stream)
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


def chatg4f_web(prompt,dialogue_history,session,stream=st.session_state["stream"],model=st.session_state.g4fmodel,provider=st.session_state.provider,temperature=st.session_state.temperature,max_tokens=st.session_state.max_tokens):
    # 整理联网消息
    tmp_history = [{'role':'system','content':"你现在是一个关键词提取机器人,接下来用户会给你一段文本,这段文本是用户输入给你的内容,这段内容可能会有一些混淆的信息,你要做的就是提取里面可能需要联网才能查询到的信息出来,并且返回搜索使用的关键词，你的回复必须是关键词,回复也只能有关键词，格式为'{key1} {key2} {key3} ...'"}]
    tmp_history.append({'role':'user','content':prompt})
    web_prompt = gpt_resopnse(model,provider,tmp_history,temperature,max_tokens,False)
    print(web_prompt)
    inner = st.session_state.web_catcher.extract_contents(web_prompt)[:3000]
    real_prompt = f"""user询问问题如下:\n{prompt}。\n\n网络搜索结果如下:\n{inner}\n\n请你结合网络搜索结果回答用户的问题"""
    print(real_prompt)
    # 将当前消息添加到对话历史中
    dialogue_history.append({"role":"user","content":real_prompt})
    session.append({"role":"system","content":prompt})
    # 发送请求给 OpenAI GPT
    response = gpt_resopnse(model,provider,dialogue_history,temperature,max_tokens,stream)
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

    # 新的开始
    with st.container():
        if st.button('New Chat',use_container_width=True):
            if st.session_state["sys_prompt"] == "":
                st.session_state["dialogue_history"] = []
            else:
                st.session_state.dialogue_history = [{'role':'system','content':st.session_state.sys_prompt},]
            st.session_state["session"] = []

    # 设置
    with st.container():
        with st.expander("**Settings**"):
            st.session_state["model"] = st.selectbox('models', st.session_state._models_str)
            provider = st.selectbox('provider', st.session_state.providers_available)
            max_tokens = st.text_input('max_tokens', st.session_state["max_tokens"])
            memory = st.toggle('memory', st.session_state["memory"])
            st.session_state["stream"] =  st.toggle('stream', ["True","False"])
            temperature = st.slider('temperature', 0.0, 2.0, st.session_state["temperature"])
            if st.button('Save',use_container_width=True):
                st.session_state.g4fmodel = st.session_state.models_list[st.session_state["model"]]
                st.session_state.provider = st.session_state.providers_list[provider]
                st.session_state["temperature"] =temperature
                st.session_state["memory"] =memory
                st.session_state["max_tokens"] = max_tokens
                st.balloons()
                show()

    # 系统提示词
    with st.container():
        sys_prompt = st.text_input('**System Prompt**', st.session_state["sys_prompt"])
        st.session_state["sys_prompt"] = sys_prompt.strip()
    
    with st.container():
        new_file = st.file_uploader("上传短文件")
        if st.button('Upload File📄',use_container_width=True) and new_file is not None:
                file_name,file_type = collect_file(new_file)
                st.session_state.dialogue_history = get_file_reader(new_file,file_type)

    # 模式
    with st.container():
        st.session_state["mode"] = st.radio("Choose the mode",["**🚀Introduce**","**🤖Chat**","**🌐Chat-web**","**🕵️‍♂️Test**"])


########################### 聊天展示区 ###########################

if st.session_state["mode"] == "**🤖Chat**":
    # 用户输入区域
    header.write("<h2> 🤖 "+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
    user_prompt = st.chat_input("Send a message")
    if user_prompt:
        message = {"role":"user","content":user_prompt}
        chatg4f(message,st.session_state["dialogue_history"],st.session_state["session"])
elif st.session_state["mode"] == "**🕵️‍♂️Test**":
    with show_test:
        async def run_provider(content,model,provider: g4f.Provider.BaseProvider):
            try:
                response = await g4f.ChatCompletion.create_async(
                    model=model,
                    messages=[{"role": "user", "content": content}],
                    provider=provider,
                )
                if response != "":
                    st.session_state.providers_available.append(provider.__name__)
                    show_test.write("***")
                    show_test.write(f"**{provider.__name__}:**")
                    show_test.write(response)
                # print(f"{provider.__name__}:", response)
            except Exception as e:
                # show_test.write("***")
                # show_test.write(f"*{provider.__name__}*: {e}")
                # print(f"{provider.__name__}:", e)
                pass
                
        async def run_all(content,model):
            calls = [
                run_provider(content,model,provider) for provider in st.session_state.providers_list.values()
            ]
            await asyncio.gather(*calls)

        def test_provider(content,model):
            asyncio.run(run_all(content,model))
            
    header.write("<h2> 🕵️‍♂️ "+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
    test_prompt = st.chat_input("Send a test message to search avalible providers")
    if test_prompt:
        with st.spinner('🕵️‍♂️Search available providers...'):
            st.session_state.providers_available = []
            test_provider(test_prompt,st.session_state.g4fmodel)
elif st.session_state.mode == "**🌐Chat-web**":
    # 用户输入区域
    header.write("<h2> 🌐 "+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
    user_prompt = st.chat_input("Send a message")
    if user_prompt:
        chatg4f_web(user_prompt,st.session_state["dialogue_history"],st.session_state["session"])
else:
    with show_introduce:
        header.write("<h2> 🚀 "+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
        st.write(st.session_state.introduce)
