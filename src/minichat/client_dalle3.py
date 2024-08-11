import os
from openai import OpenAI
from minichat.config_schema import Config
where_ami = os.path.dirname(__file__)
cfig = Config.load(os.path.join(where_ami, "minichat.json"))
client = OpenAI(api_key=cfig.cfig_openai.openai_key)

response = client.images.generate(
  model="dall-e-3",
  prompt="a white siamese cat",
  size="1024x1024",
  quality="standard",
  n=1,
)

image_url = response.data[0].url
print(image_url)

import requests

# 图片的URL
url = 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-YTOte5T8GURbsS3PHh8eTgvk/user-Fiwv2pM4918bRP79aFAnAZFE/img-wPlRMvQqO3iN56vA2sHjtdv8.png?st=2024-08-02T07%3A41%3A26Z&se=2024-08-02T09%3A41%3A26Z&sp=r&sv=2023-11-03&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-08-02T04%3A40%3A15Z&ske=2024-08-03T04%3A40%3A15Z&sks=b&skv=2023-11-03&sig=w0nEsbLPP1H3gI41pE6wLp4Lc7JAdxweOrX9pVv9mPM%3D'

# 发送HTTP GET请求
response = requests.get(url)

# 检查请求是否成功
if response.status_code == 200:
    # 打开一个文件，准备写入二进制数据
    with open('downloaded_image.png', 'wb') as file:
        file.write(response.content)
    print("图片下载成功并保存为 'downloaded_image.png'")
else:
    print(f"下载失败，状态码: {response.status_code}")

