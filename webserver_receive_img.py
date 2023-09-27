from flask import Flask, request
import os
from scripts.calculator import CalcFPS

app = Flask(__name__)
upload_folder = "uploads/"
fps_calculator = CalcFPS()

if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        fps_calculator.start_time()
        image_data = request.data
        fps = fps_calculator.calculate()
        print(fps)
        with open(os.path.join(upload_folder, "uploaded_image.jpg"), "wb") as f:
            f.write(image_data)
            
        return "Image uploaded and processed successfully.", 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
