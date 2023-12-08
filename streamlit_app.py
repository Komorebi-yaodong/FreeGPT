from langchain.text_splitter import RecursiveCharacterTextSplitter
from g4f.models import ModelUtils,_all_models
from g4f.Provider import ProviderUtils
from docx import Document
import streamlit as st
import asyncio
import PyPDF2
import g4f



if "models_list" not in st.session_state:
    st.session_state._models_str = _all_models
    st.session_state.models_list = ModelUtils.convert
if "providers_list" not in st.session_state:
    st.session_state["black_list"] = ["GptTalkRu","Hashnode","Liaobots","Phind","Bing","You"]
    st.session_state._providers_str = list(ProviderUtils.convert.keys())
    st.session_state.providers_list = ProviderUtils.convert
    for black in st.session_state["black_list"]:
        if black in st.session_state._providers_str:
            del st.session_state.providers_list[black]
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
if "dialogue_history" not in st.session_state:
    st.session_state["dialogue_history"] = []
if "introduce" not in st.session_state:
    with open("./README.md","r",encoding="utf-8") as f:
        st.session_state.introduce = f.read()

########################### element ###########################


header =  st.empty()
header.write("<h2> 🤖 "+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
show_talk = st.container()
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
    start_content = "You are a file reading bot. Next, the user will send a file. After reading, you should fully understand the content of the file and be able to analyze, interpret, and respond to questions related to the file in both Chinese and Markdown formats. Answer step-by-step."
    end_file_message = "File sent. Next, please reply in Chinese and format your response using markdown based on the content.'"
    dialogue_history = [{'role':'user','content':start_content},]
    
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


async def run_provider(content,model,provider: g4f.Provider.BaseProvider):
    try:
        response = await g4f.ChatCompletion.create_async(
            model=model,
            messages=[{"role": "user", "content": content}],
            provider=provider,
            timeout=10,
        )
        if response != "" and provider.__name__ not in st.session_state.black_list:
            st.session_state.providers_available.append(provider.__name__)
            st.info(provider.__name__, icon="✅")
            print(provider.__name__,":",response)
        # print(f"{provider.__name__}:", response)
    except Exception as e:
        # print(f"{provider.__name__}:", e)
        pass
        

async def run_all(content,model):
    calls = [
        run_provider(content,model,provider) for provider in st.session_state.providers_list.values()
    ]
    await asyncio.gather(*calls)

def test_provider(content,model):
    asyncio.run(run_all(content,model))


########################### 侧边栏：设置、测试 ###########################


# 侧边栏
with st.sidebar:

    # 新的开始
    with st.container():
        if st.session_state.get('🗨️ New Chat'):
            st.session_state.dialogue_history = []
            st.session_state["session"] = []
        st.button('🗨️ New Chat',use_container_width=True,type='primary',key="🗨️ New Chat")


    with st.container():
        if st.button("🕵️‍♂️Search Providers",use_container_width=True,key="🕵️‍♂️Search Providers"):
            with show_talk:
                st.session_state.providers_available = []
                test_prompt = "请回复“收到”两字，不要有任何多余解释和字符。"
                test_provider(test_prompt,st.session_state.g4fmodel)
        


    # 设置
    with st.container():
        with st.expander("**Settings**"):
            st.session_state["model"] = st.selectbox('models', sorted(st.session_state._models_str))
            provider = st.selectbox('provider', sorted(st.session_state.providers_available))
            max_tokens = st.text_input('max_tokens', st.session_state["max_tokens"])
            memory = st.toggle('memory', st.session_state["memory"])
            st.session_state["stream"] =  st.toggle('stream', ["True","False"])
            temperature = st.slider('temperature', 0.0, 2.0, st.session_state["temperature"])
            if st.session_state.get('Save'):
                st.session_state.g4fmodel = st.session_state.models_list[st.session_state["model"]]
                st.session_state.provider = st.session_state.providers_list[provider]
                st.session_state["temperature"] =temperature
                st.session_state["memory"] =memory
                st.session_state["max_tokens"] = max_tokens
                st.balloons()
                show()
            st.button('Save',use_container_width=True,key="Save")

    
    with st.container():
        new_file = st.file_uploader("上传短文件")
        if st.session_state.get('Upload File📄') and new_file is not None:
                file_name,file_type = collect_file(new_file)
                st.session_state.dialogue_history = get_file_reader(new_file,file_type)
        st.button('Upload File📄',use_container_width=True,key='Upload File📄')

    # 模式
    with st.container():
        st.session_state["mode"] = st.radio("Choose the mode",["**🤖Chat**","**🚀Introduce**"])




########################### 聊天展示区 ###########################

if st.session_state["mode"] == "**🤖Chat**":
    # 用户输入区域
    header.write("<h2> 🤖 "+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
    user_prompt = st.chat_input("Send a message")
    if user_prompt:
        message = {"role":"user","content":user_prompt}
        chatg4f(message,st.session_state["dialogue_history"],st.session_state["session"])
else:
    with show_introduce:
        header.write("<h2> 🚀 "+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
        st.write(st.session_state.introduce)
