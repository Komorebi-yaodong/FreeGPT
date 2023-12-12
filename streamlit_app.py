from langchain.text_splitter import RecursiveCharacterTextSplitter
from streamlit_mic_recorder import mic_recorder
from g4f.models import ModelUtils,_all_models
from streamlit.components.v1 import html
from g4f.Provider import ProviderUtils
import speech_recognition as sr
from docx import Document
from openai import OpenAI
import streamlit as st
from gtts import gTTS
import requests
import asyncio
import hashlib
import base64
import langid
import PyPDF2
import time
import g4f
import io



if "models_list" not in st.session_state:
    st.session_state._models_str = _all_models
    st.session_state.models_list = ModelUtils.convert
    st.session_state["black_list"] = ["GptTalkRu","Hashnode","Liaobots","Phind","Bing","You"]
    st.session_state._providers_str = list(ProviderUtils.convert.keys())
    st.session_state.providers_list = ProviderUtils.convert
    for black in st.session_state["black_list"]:
        if black in st.session_state._providers_str:
            del st.session_state.providers_list[black]
    st.session_state["model"] = st.session_state._models_str[0]
    st.session_state["temperature"] = 0.2
    st.session_state["g4fmodel"] = st.session_state.models_list[st.session_state["model"]]
    st.session_state["provider_name"] = st.session_state._providers_str[0]
    st.session_state["provider"] = st.session_state.providers_list[st.session_state.provider_name]
    st.session_state["providers_available"] = st.session_state._providers_str
    st.session_state["stream"] = True
    st.session_state["new_file"] = None
    st.session_state["sys_prompt"] = "";
    st.session_state["mode"] = "**🚀introudce**"
    st.session_state["speech"] = True
    st.session_state["talk_content"] = io.BytesIO()
    st.session_state["speech_language"] = "zh"
    st.session_state["audio_prompt"] = None
    st.session_state.sr = sr.Recognizer()
    st.session_state["session"] = []
    st.session_state["dialogue_history"] = []
    st.session_state["huggingfaceToken"] = ""
    st.session_state["draw_hisgory"] = []
    st.session_state["draw_model_list"] = {
        "现实-AbsoluteReality_v1.8.1":"https://api-inference.huggingface.co/models/digiplay/AbsoluteReality_v1.8.1",
        "现实-Absolute-Reality-1.81":"https://api-inference.huggingface.co/models/Lykon/absolute-reality-1.81",
        "动漫-AingDiffusion9.2":"https://api-inference.huggingface.co/models/digiplay/AingDiffusion9.2",
        "现实动漫-BluePencilRealistic_v01":"https://api-inference.huggingface.co/models/digiplay/bluePencilRealistic_v01",
        "动漫写实-Counterfeit-v2.5":"https://api-inference.huggingface.co/models/gsdf/Counterfeit-V2.5",
        "动漫写实-Counterfeit-v25-2.5d-tweak":"https://api-inference.huggingface.co/models/digiplay/counterfeitV2525d_tweak",
        "动漫可爱-Cuteyukimix":"https://api-inference.huggingface.co/models/stablediffusionapi/cuteyukimix",
        "动漫可爱-Cuteyukimixadorable":"https://api-inference.huggingface.co/models/stablediffusionapi/cuteyukimixadorable",
        "现实动漫-Dreamshaper-7":"https://api-inference.huggingface.co/models/Lykon/dreamshaper-7",
        "现实动漫-Dreamshaper_LCM_v7":"https://api-inference.huggingface.co/models/SimianLuo/LCM_Dreamshaper_v7",
        "动漫3D-DucHaitenDreamWorld":"https://api-inference.huggingface.co/models/DucHaiten/DucHaitenDreamWorld",
        "现实-EpiCRealism":"https://api-inference.huggingface.co/models/emilianJR/epiCRealism",
        "现实照片-EpiCPhotoGasm":"https://api-inference.huggingface.co/models/Yntec/epiCPhotoGasm",
        "动漫丰富-Ether-Blu-Mix-b5":"https://api-inference.huggingface.co/models/tensor-diffusion/Ether-Blu-Mix-V5",
        "动漫-Flat-2d-Animerge":"https://api-inference.huggingface.co/models/jinaai/flat-2d-animerge",
        "动漫风景-Genshin-Landscape-Diffusion":"https://api-inference.huggingface.co/models/Apocalypse-19/Genshin-Landscape-Diffusion",
        "现实照片-Juggernaut-XL-v7":"https://api-inference.huggingface.co/models/stablediffusionapi/juggernaut-xl-v7",
        "现实风景-Landscape_PhotoReal_v1":"https://api-inference.huggingface.co/models/digiplay/Landscape_PhotoReal_v1",
        "艺术水墨-MoXin":"https://api-inference.huggingface.co/models/zhyemmmm/MoXin",
        "现实写实-OnlyRealistic":"https://api-inference.huggingface.co/models/stablediffusionapi/onlyrealistic",
        "现实-Realistic-Vision-v51":"https://api-inference.huggingface.co/models/stablediffusionapi/realistic-vision-v51",
        "初始-StableDiffusion-2-1":"https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
        "初始-StableDiffusion-XL-0.9":"https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-0.9",
        "动漫-TMND-Mix":"https://api-inference.huggingface.co/models/stablediffusionapi/tmnd-mix",
        "艺术-Zavychromaxl-v3":"https://api-inference.huggingface.co/models/stablediffusionapi/zavychromaxlv3",
    }
    st.session_state.negative_prompt = "extra fingers, mutated hands, poorly drawn hands, poorly drawn face, deformed, ugly, bad anatomy, bad proportions, extra limbs, cloned face, double torso, extra arms, extra hands, mangled fingers, missing lips, ugly face, distorted face, extra legs"
    st.session_state["draw_model"] = "初始-StableDiffusion-2-1"
    st.session_state["StableDiffusion_URL"] = st.session_state["draw_model_list"][st.session_state["draw_model"]]
    with open("./README.md","r",encoding="utf-8") as f:
        st.session_state.introduce = f.read()
    st.session_state.gpt_choice = True
    st.session_state.openai_set = {
        "flag" : st.session_state.gpt_choice,
        "api_base" : "",
        "api_key" : "",
        "api_model" : "",
    }
    st.session_state.openai_model_list = [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-16k",
        "gpt-4",
        "text-davinci-001",
        "text-davinci-002",
        "text-davinci-003",
    ]
    st.session_state.author_key = ""

########################### element ###########################


header =  st.empty()
header.write("<h2> 🤖 "+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
# 文字聊天
show_talk = st.container()
# 项目介绍
show_introduce = st.container(border=True)
# 语音对话
show_mine_speech = st.empty()
show_ai_speech = st.empty()
# 文生图
show_draw = st.container()
# 其他网站
show_webs = st.container()


########################### function ###########################


@st.cache_data
def sha256_hash(string):
    # 创建SHA256哈希对象
    sha256_hasher = hashlib.sha256()
    # 将字符串编码为字节流并更新哈希对象
    sha256_hasher.update(string.encode('utf-8'))
    # 获取哈希结果
    hashed_string = sha256_hasher.hexdigest()

    return hashed_string


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
        st.error("The file type is not supported.(only pdf, docx, txt, md supported)")
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
    assistant_reply = {'role':'assistant','content':"收到"}
    start_content = "You are a file reading bot. Next, the user will send a file. After reading, you should fully understand the content of the file and be able to analyze, interpret, and respond to questions related to the file in both Chinese and Markdown formats. Answer step-by-step."
    end_file_message = "File sent. Next, please reply in Chinese and format your response using markdown based on the content.'"
    dialogue_history = [{'role':'system','content':start_content},assistant_reply]
    
    # 文本提取并拆分
    text = get_text(file,type)
    text_list = get_splitted_text(text)
    pages = len(text_list)
    start_message = f"我现在会将文章的内容分 {len(text_list)} 部分发送给你。请确保你已经准备好接收，接收到文章发送完毕的指令后，请准备回答我的问题。"
    dialogue_history.append({'role':'user','content':start_message})
    dialogue_history.append(assistant_reply)

    # 分段输入
    for i in range(pages):
        text_message = {'role':'user','content':text_list[i]}
        dialogue_history.append(text_message)
        dialogue_history.append(assistant_reply)
    
    # 结束文本输入
    end_message = {'role':'user','content':end_file_message}
    dialogue_history.append(end_message)
    dialogue_history.append({'role':'assistant','content':"我已阅读完文章"})

    return dialogue_history


def gpt_resopnse(model,provider,dialogue_history,stream,temperature,openai_set):
    if openai_set["flag"]:
        client = OpenAI(
            api_key=openai_set["api_key"],
            base_url=openai_set["api_base"],
        )
        response = client.chat.completions.create(
            model=openai_set["api_model"],
            messages=dialogue_history,
            temperature=temperature, # 控制模型输出的随机程度
            stream=stream,
        )
    else:
        if stream:
            response = g4f.ChatCompletion.create(
                model=model,
                provider = provider,
                messages=dialogue_history,
                temperature=temperature, # 控制模型输出的随机程度
                stream=stream
            )
        else:
            response = g4f.ChatCompletion.create(
                model=model,
                provider = provider,
                messages=dialogue_history,
                temperature=temperature, # 控制模型输出的随机程度
            )
    return response


def chatg4f(message,dialogue_history,session,openai_set=st.session_state.openai_set,stream=st.session_state["stream"],model=st.session_state.g4fmodel,provider=st.session_state.provider,temperature=st.session_state.temperature):
    if len(dialogue_history) != 0 and len(session) != 0:
        if dialogue_history[-1]["role"] == "user":
            dialogue_history.pop()
        if session[-1]["role"] == "user":
            session.pop()
    # 将当前消息添加到对话历史中
    session.append(message)
    dialogue_history.append(message)
    # 发送请求给 OpenAI GPT
    response = gpt_resopnse(model,provider,dialogue_history,stream,temperature,openai_set=openai_set)
    show()
    reply = {'role':'assistant','content':""}
    if openai_set["flag"]:
        if stream:
            with show_talk.chat_message(reply['role']):
                line = st.empty()
                for chunk in response:
                    message = chunk.choices[0].delta.content
                    if message is not None:
                        reply['content'] += message
                        line.empty()
                        line.write(reply['content'])
        else:
            with show_talk.chat_message(reply['role']):
                line = st.empty()
                reply['content'] = response.choices[0].message.content
                line.write(reply['content'])
    else:
        with show_talk.chat_message(reply['role']):
            line = st.empty()
            for message in response:
                reply['content'] += message
                line.empty()
                line.write(reply['content'])
    session.append(reply)
    dialogue_history.append(reply)
    if st.session_state["speech"] == True:
        st.session_state.talk_content = mytts(reply["content"])


def show():
    for section in st.session_state["session"]:
        with show_talk.chat_message(section['role']):
            st.write(section['content'])


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

def mytts(text):

    def autoplay_audio(audio_data:io.BytesIO):
        data = audio_data.getvalue()
        b64 = base64.b64encode(data).decode()
        md = f"""
                <audio controls autoplay="true" id="myAudio" style="width: 100%;">
                    <source src="data:audio/ogg;base64,{b64}" type="audio/ogg">
                </audio>
                <script>
                    var audio = document.getElementById("myAudio");
                    audio.playbackRate = 1.5; 
                </script>
                """
        html(md)
        
    text=text.replace("```"," ").replace("`"," ").replace("***"," ").replace("**"," ").replace("$$"," ").replace("###"," ").replace("##"," ").replace("#"," ").replace("---"," ")
    lang,conf = langid.classify(text)
    tts = gTTS(text=text,lang=lang)
    speach_BytesIO = io.BytesIO()
    tts.write_to_fp(speach_BytesIO)
    autoplay_audio(speach_BytesIO)
    st.write(lang,conf)


def talkg4f(message,dialogue_history,session,openai_set=st.session_state.openai_set,model=st.session_state.g4fmodel,provider=st.session_state.provider,temperature=st.session_state.temperature):
    if len(dialogue_history) != 0 and len(session) != 0:
        if dialogue_history[-1]["role"] == "user":
            dialogue_history.pop()
        if session[-1]["role"] == "user":
            session.pop()
    # 将当前消息添加到对话历史中
    session.append(message)
    dialogue_history.append(message)
    # 发送请求给 OpenAI GPT
    response = gpt_resopnse(model,provider,dialogue_history,False,temperature,openai_set=openai_set)
    if openai_set["flag"]:
        reply = {'role':'assistant','content':response.choices[0].message.content}
    else:
        reply = {'role':'assistant','content':response}
    session.append(reply)
    dialogue_history.append(reply)
    
    st.session_state.talk_content = mytts(reply["content"])


@st.cache_data
def audio2text(audio_prompt,language):
    audio_data = sr.AudioData(audio_prompt['bytes'],audio_prompt['sample_rate'],audio_prompt['sample_width'])
    output = st.session_state.sr.recognize_google(audio_data,language=language)
    return output


def text2img(prompt,token=st.session_state.huggingfaceToken,StableDiffusion_URL=st.session_state.StableDiffusion_URL):

    def query(payload):
        try:
            response = requests.post(StableDiffusion_URL, headers=StableDiffusion_headers, json=payload, timeout=60)
            if response.status_code == 200:
                return True, response.content
            else:
                return False,response.content
        except requests.exceptions.RequestException as e:
            return False,e
    
    StableDiffusion_headers = {"Authorization":"Bearer "+token}
    
    show_draw_img()
    flag,response = query({
        "inputs":prompt,
        "negative_prompt":st.session_state.negative_prompt,
    })
    
    image = response
    st.session_state.draw_hisgory.append({"prompt":prompt,"image":image,"flag":flag})
    with show_draw.chat_message("assistant"):
        if flag:
            st.image(image,prompt,use_column_width=True)
        else:
            st.write(prompt,"\n",image)


def show_draw_img():
    for section in st.session_state.draw_hisgory:
        with show_draw.chat_message("assistant"):
            if section["flag"]:
                st.image(section["image"],section["prompt"],use_column_width=True)
            else:
                st.write(section["prompt"],"\n",section["image"])

            
########################### 侧边栏：设置、测试 ###########################


# 侧边栏
with st.sidebar:

    def author_change():
        author_key_hash = sha256_hash(st.session_state.author_key.strip())
        if author_key_hash in st.secrets.pwsds:
            st.session_state.huggingfaceToken = st.secrets.huggingfaceTokens[st.secrets.pwsds[author_key_hash]]
            st.session_state.openai_set["api_key"] = st.secrets.openai_api_keys[st.secrets.pwsds[author_key_hash]]
            st.session_state.openai_set["api_base"] = st.secrets.openai_api_bases[st.secrets.pwsds[author_key_hash]]


    def get_file_chat():
        if st.session_state.new_file:
            file_name,file_type = collect_file(st.session_state.new_file)
            st.session_state.dialogue_history = get_file_reader(st.session_state.new_file,file_type)
            st.session_state.session = []


    def get_save():
        # 更新作者参数
        author_change()
        # 更新chat参数
        if st.session_state.gpt_choice:
            st.session_state.openai_set["api_model"] = st.session_state.openai_set["api_model"]
            st.session_state.openai_set["api_key"] = st.session_state.openai_set["api_key"]
            st.session_state.openai_set["api_base"] = st.session_state.openai_set["api_base"]
        else:
            st.session_state.model = st.session_state.model
            st.session_state.provider = st.session_state.providers_list[st.session_state.provider_name]
            st.session_state.g4fmodel = st.session_state.models_list[st.session_state.model]

        st.session_state.temperature =st.session_state.temperature
        st.session_state.speech =st.session_state.speech
        st.session_state.stream =st.session_state.stream
        st.session_state.sys_prompt = st.session_state.sys_prompt
        
        # 更新text2img参数
        st.session_state.draw_model = st.session_state.draw_model
        st.session_state.StableDiffusion_URL = st.session_state.draw_model_list[st.session_state.draw_model]
        st.session_state.huggingfaceToken = st.session_state.huggingfaceToken
        st.session_state.negative_prompt = st.session_state.negative_prompt

        # 更新会话
        if len(st.session_state.dialogue_history) == 0:
            if st.session_state.sys_prompt == "":
                st.session_state.dialogue_history = []
            else:
                st.session_state.dialogue_history = [{"role":"system","content":st.session_state.sys_prompt},]
            st.session_state.session = []

    # 新的开始
    with st.container():
        if st.session_state.get('🆕 New Chat'):
            if st.session_state.sys_prompt == "":
                st.session_state.dialogue_history = []
            else:
                st.session_state.dialogue_history = [{"role":"system","content":st.session_state.sys_prompt},]
            st.session_state.session = []
            st.session_state.draw_hisgory = []
        st.button('🆕 New Chat',use_container_width=True,type='primary',key="🆕 New Chat")
        
    with st.container():
        st.session_state.author_key =st.text_input('author channel',type='password',value=st.session_state.author_key,on_change=get_save())
    
        

    # 聊天设置
    with st.container():
        def gpt_choice_change():
            st.session_state.gpt_choice = not st.session_state.gpt_choice
            st.session_state.openai_set["flag"] = st.session_state.gpt_choice
        with st.expander("**Chat Settings**"):               
            st.session_state.gpt_choice = st.toggle("Free||API",value=st.session_state.gpt_choice,on_change=gpt_choice_change)
            if st.session_state.gpt_choice:
                st.session_state.openai_set["api_model"] = st.selectbox('Chat Models', sorted(st.session_state.openai_model_list),on_change=get_save())
                st.session_state.openai_set["api_key"] = st.text_input('api_key',type='password',value=st.session_state.openai_set["api_key"],on_change=get_save())
                st.session_state.openai_set["api_base"] = st.text_input('api_base',value=st.session_state.openai_set["api_base"],on_change=get_save())
            else:
                st.button("🕵️‍♂️Search Providers",use_container_width=True,key="🕵️‍♂️Search Providers")
                st.session_state.model = st.selectbox('Chat Models', sorted(st.session_state._models_str),on_change=get_save())
                st.session_state.provider_name = st.selectbox('Providers', sorted(st.session_state.providers_available),on_change=get_save())
            st.session_state.sys_prompt = st.text_input("System Prompt",value=st.session_state.sys_prompt,on_change=get_save())
            with st.container():
                col1,col2 = st.columns(2)
                with col1:
                    st.session_state.speech = st.toggle('speech', st.session_state.speech,on_change=get_save())
                with col2:
                    st.session_state.stream =  st.toggle('stream', ["True","False"],on_change=get_save())
            st.session_state.temperature = st.slider('temperature', 0.0, 2.0, st.session_state["temperature"],on_change=get_save())
            st.session_state.new_file = st.file_uploader("Chat short file",label_visibility="collapsed")
            st.button("ChatFile",use_container_width=True,key="ChatFile")
            if st.session_state.get("ChatFile"):
                get_file_chat()

    
    # 绘画设置
    with st.container():
        with st.expander("**Draw Settings**"):
            st.session_state.draw_model = st.selectbox('Draw Models', sorted(st.session_state.draw_model_list.keys(),key=lambda x:x.split("-")[0]),on_change=get_save())
            st.session_state.huggingfaceToken = st.text_input('Huggingface Token',type='password',value=st.session_state.huggingfaceToken,on_change=get_save())
            st.session_state.negative_prompt = st.text_input('Negative Prompt',value=st.session_state.negative_prompt,on_change=get_save())
    
    # st.button('Save',use_container_width=True,key="Save")

            
    st.button("Save",use_container_width=True,key="Save")

    # 模式
    with st.container(border=True):
        with st.container():
            st.session_state["mode"] = st.radio("Choose the mode",["**🤖Chat**","**💬Talk**","**🎨Text2Img**","**🔗Other Sites**","**🚀Introduce**"])


    if st.session_state.get("🕵️‍♂️Search Providers"):
        with show_talk:
            st.session_state.providers_available = []
            test_prompt = "请回复“收到”两字，不要有任何多余解释和字符。"
            test_provider(test_prompt,st.session_state.g4fmodel)
            get_save()


    if st.session_state.get("Save"):
        get_save()
        # 更新会话展示
        if st.session_state.mode == "**🤖Chat**":
            show()
        elif st.session_state.mode == "**🎨Text2Img**":
            show_draw_img()

########################### 聊天展示区 ###########################

if st.session_state["mode"] == "**🤖Chat**":
    # 用户输入区域
    if st.session_state.gpt_choice:
        header.write("<h2> 🤖 "+st.session_state.openai_set["api_model"]+"</h2>",unsafe_allow_html=True)
    else:
        header.write("<h2> 🤖 "+st.session_state["model"]+"</h2>",unsafe_allow_html=True)
    user_prompt = st.chat_input("Send a message")
    if user_prompt:
        message = {"role":"user","content":user_prompt}
        chatg4f(message,st.session_state["dialogue_history"],st.session_state["session"])
elif st.session_state["mode"] == "**💬Talk**":
    header.write("<h2> 💬 "+st.session_state["model"]+"</h2>",unsafe_allow_html=True)

    show_mine_speech = st.container()
    show_ai_speech = st.container()

    with show_mine_speech.container():
        st.session_state.speech_language = st.selectbox("🎙️language",["中文-zh","English-en","日本語-ja","Русский язык-ru","Deutsch-de","Français-fr","중국어-ko"],key="language")
        st.session_state.audio_prompt = mic_recorder(
            start_prompt="🎙️开始说话",
            stop_prompt="🛑结束说话", 
            just_once=True,
            use_container_width=True,
            callback=None,
            args=(),
            kwargs={},
            key=None
        )
    with show_ai_speech.container():
        if st.session_state.audio_prompt:
            speech_prompt = audio2text(st.session_state.audio_prompt,st.session_state.speech_language[-2:])
            message = {"role":"user","content":speech_prompt}
            talkg4f(message,st.session_state["dialogue_history"],st.session_state["session"])

elif st.session_state["mode"] == "**🎨Text2Img**":
    # 用户输入区域
    header.write("<h2> 🎨 "+st.session_state.draw_model+"</h2>",unsafe_allow_html=True)
    draw_prompt = st.chat_input("Send your prompt")
    if draw_prompt:
        text2img(draw_prompt)

elif st.session_state["mode"] == "**🔗Other Sites**":
    with show_webs:
        header.write("<h2> 🔗Other Sites"+"</h2>",unsafe_allow_html=True)
        tab1,tab2,tab3 = st.tabs(["**NovelAI Tags**","**Civitai Gallery**","Others"])
        with tab1:
            # html_source = get_html("https://novelai-tag.vercel.app/","1")
            # st.components.v1.html(html_source, height=1040, width=700)
            st.components.v1.iframe("https://novelai-tag.vercel.app/",height=700,scrolling=True,width=700)
            st.link_button(label="go to novelai-tag",url="https://novelai-tag.vercel.app/")
        with tab2:
            # html_source = get_html("https://civitai.com/images","1")
            # st.components.v1.html(html_source, height=1040, width=800)
            st.components.v1.iframe("https://civitai.com/images",height=700)
            st.link_button(label="go to Civitai Gallery",url="https://civitai.com/images")
        with tab3:
            st.write(st.session_state.introduce)
    st.write("网络数据仅供参考，非盈利，仅供学习参考")
else:
    with show_introduce:
        header.write("<h2> 🚀 Intorduce"+"</h2>",unsafe_allow_html=True)
        st.write(st.session_state.introduce)
