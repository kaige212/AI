from PIL import Image


image = Image.open('/home/aiservice/workspace/AI/instance/uploads/1/origin_image.jpg')
print(image.mode)  # 这会打印出 'RGB', 'RGBA', 或其他模式