import subprocess
import os


current_path = os.getcwd()

program = os.path.join(current_path, "Real-ESRGAN/Real-ESRGAN.bat")
# image = "Real-ESRGAN/image.webp"
image = os.path.join(current_path, "_127830610_img_1087.jpg.jpg")

print(program)

subprocess_list = [program,
                   image]

subprocess.run(subprocess_list)