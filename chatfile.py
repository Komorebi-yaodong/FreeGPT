import PyPDF2
from docx import Document

sys_content = " You are a read-file master. You will receive a document and reply my requirements in Chinese. Instruction: Compose a comprehensive reply to the query using the search results given. Cite each reference using [ Page Number] notation (every result has this number at the beginning). Citation should be done at the end of each sentence. If the search results mention multiple subjects with the same name, create separate answers for each. Make sure the answer is correct and don't output false content. Only answer what is asked. The answer should be short and concise. Answer step-by-step and reply in markdown format."
end_file_message = "Document sent. Please reply in Chinese and format your response using markdown based on the content. My first requirement is'Summarize and main content of the article.'"

# 文件收集
def collect_file(file_upload):
    file_name = ".".join(file_upload.name.split('.')[0:-1])
    file_type = file_upload.name.split('.')[-1]

    return file_name,file_type


def extract_text_from_pdf(file):
    pdf = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        text += page.extract_text()
        
    return text


def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


# 直接读取pdf获得文本
def pdf_transofrm(file,type):

    def ContentSplit(string,length):
        return [string[i:i+length] for i in range(0, len(string), length)]
    

    # 将文件进行转换并存储
    if type == "pdf":
        content = extract_text_from_pdf(file)
    elif type == "docx":
        content = extract_text_from_docx(file)
    else:
        print("The file type is not supported.(only Pdf, Docx supported)")
        return None
    
    # 读取文件内容
    
    dialogue_history = []
    contents = ContentSplit(content,4000) # 分段内容
    pages = len(contents) # 分段数

    ## 分段输入
    # start
    start_message = f"我现在会将文章的内容分 {pages} 部分发送给你。请确保你已经准备好接收，接收到文章发送完毕的指令后，请准备回答我的问题。"
    dialogue_history.append({'role':'user','content':start_message})
    # 文章
    for i in range(pages):
        content_message = {'role':'user','content':contents[i]}
        dialogue_history.append(content_message)
    # end
    end_message = {'role':'user','content':end_file_message}
    dialogue_history.append(end_message)
    # print(dialogue_history)


    return dialogue_history