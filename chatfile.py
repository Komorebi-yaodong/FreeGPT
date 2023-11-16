import aspose.words as aw
import os
from shutil import copyfile
from PyPDF2 import PdfReader, PdfWriter
import json
import shutil


# 文件收集
def collect_file(file_upload):
    file_name = ".".join(file_upload.name.split('.')[0:-1])
    file_type = file_upload.name.split('.')[-1]

    return file_name,file_type


def change_config(config_path,base_url,api_key,model,temperature,memory):
    with open(config_path,'r',encoding="utf-8") as f:
        config = json.load(f)
        config['base_url'] = base_url
        config['api_key'] = api_key
        config['model'] = model
        config['temperature'] = temperature
        config['memory'] = memory
    with open(config_path,'w',encoding="utf-8") as f:
        json.dump(config,f,ensure_ascii = False)
    return True


# 获得配置
def get_config(config_path):
    with open(config_path,'r',encoding="utf-8") as f:
        config = json.load(f)
        base_url = config['base_url']
        api_key = config['api_key']
        model = config['model']
        temperature = config['temperature']
        data_path = config['data_path']
        sys_content = config['sys_content']
        max_tokens = config['max_tokens']
        memory = config['memory']
    return base_url,api_key,model,temperature,data_path,sys_content,max_tokens,memory


def get_file(file_name,data_path):
    dialogue_path = data_path+"/"+file_name+"/dialogue.json"
    if os.path.exists(dialogue_path):
        with open(dialogue_path, "r", encoding="utf-8") as f:
            dialogue_history = json.load(f)
        return dialogue_history
    else:
        print(f"No dialogue.json, delete {data_path+'/'+file_name} and try again")


def get_history(data_path):
    floders = os.listdir(data_path)
    return floders


def delete_file(file_name,data_path):
    file_path = data_path+"/"+file_name
    if os.path.exists(file_path):
        shutil.rmtree(file_path)
        return True
    else:
        print(f"No such file path: {file_path}.")


# 分割pdf
def pdf_splitter(file,output_path):
    pdf = PdfReader(file)
    for page in range(len(pdf.pages)):
        pdf_writer = PdfWriter()
        pdf_writer.add_page(pdf.pages[page]) 
        output_filename = output_path+'{}.pdf'.format(page+1) 
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)


def md_merger(fdir,output_path):
    if os.path.exists(fdir):
        files = os.listdir(fdir)
        md = aw.Document(fdir+files[0])
        for f in range(1,len(files)):
            doc = aw.Document(fdir+files[f])
            md.append_document(doc, aw.ImportFormatMode.USE_DESTINATION_STYLES)
        md.save(output_path)
    else:
        print(f"{fdir}不存在")


# 将文件转为MD，并存储
def file_transform(file,file_name,type,data_path,sys_content):

    def ContentSplit(string,length):
        return [string[i:i+length] for i in range(0, len(string), length)]
    
    if os.path.exists(data_path):
        # 新文件夹存储路径
        new_folder = data_path+"/"+file_name
        # 转换后MD文件名称
        new_file = file_name+".md"
        # 文件类型
        
        # 创建存储路径
        if os.path.exists(new_folder) == False:
            os.mkdir(new_folder)
        elif os.path.exists(new_folder+"/"+new_file):
            # 读取文件内容
            if os.path.exists(new_folder+"/dialogue.json"):
                with open(new_folder+"/dialogue.json", "r", encoding="utf-8") as f:
                    dialogue_history = json.load(f)
                return dialogue_history
            else:
                print(f"No dialogue.json, delete {new_folder} and try again")
        else:
            print("Folder already exists but no file.")
            return None

        # 将文件进行转换并存储
        if type == "pdf":
            # pdf分割
            new_ini = new_folder+"/init/"
            os.mkdir(new_ini)
            pdf_splitter(file,new_ini)
            # md 生成 合并 保存
            md_merger(new_ini, new_folder+"/"+new_file)
        elif type == "md":
            # md保存
            copyfile(file, new_folder+"/"+new_file)
        else:
            print("File type is not supported.")
            os.remove(new_folder)
            return None
        
        # 读取文件内容
        with open(new_folder+"/"+new_file, "r", encoding="utf-8") as f:
            content = f.read()
        with open(new_folder+"/dialogue.json", "w", encoding="utf-8") as f:
            dialogue_history = [{'role':'system','content':sys_content},]
            contents = ContentSplit(content,1000) # 分段内容
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
            end_message = "文章已发送完毕，接下来我将提出一些与文章相关的问题，请你使用中文，根据内容以markdown格式进行回答，我的第一个问题是'Summarize the main content of the article.'"
            end_message = {'role':'user','content':end_message}
            dialogue_history.append(end_message)

            json.dump(dialogue_history,f)

        return dialogue_history
    else:
        print("No data path to save file cache.")
        return None