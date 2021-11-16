import subprocess

parameters_list = ["editly",
                   "title:'Darwin'",
                   "1.jpg",
                   "2.jpg",
                   "3.jpg",
                   "--width",
                   "1920",
                   "height",
                   "1080",
                   "--fps",
                   "60"]

subprocess.run(["editly", "title:'Darwin'", "1.jpg", "2.jpg", "3.jpg"], check=True)
# ["editly", "title:'Darwin'", "1.jpg", "2.jpg", "3.jpg"]

# subprocess.run(["editly"], check=True)
