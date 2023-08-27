from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField, validators
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

class BrightnessForm(FlaskForm):
    brightness_red = IntegerField("Red Brightness Value (-255 to 255)", validators=[validators.InputRequired()])
    brightness_green = IntegerField("Green Brightness Value (-255 to 255)", validators=[validators.InputRequired()])
    brightness_blue = IntegerField("Blue Brightness Value (-255 to 255)", validators=[validators.InputRequired()])
    captcha = StringField("What is 2 + 2?", validators=[validators.InputRequired()])
    submit = SubmitField("Apply")

def create_histogram(image_path, output_path):
    image = Image.open(image_path)
    pixels = np.array(image)
    
    r = pixels[:,:,0].ravel()
    g = pixels[:,:,1].ravel()
    b = pixels[:,:,2].ravel()
    
    plt.hist(r, bins=256, color='red', alpha=0.5, label='Red')
    plt.hist(g, bins=256, color='green', alpha=0.5, label='Green')
    plt.hist(b, bins=256, color='blue', alpha=0.5, label='Blue')
    
    plt.legend(loc='upper right')
    plt.xlabel('Color Value')
    plt.ylabel('Frequency')
    plt.title('Color Distribution')
    
    plt.savefig(output_path)
    plt.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = BrightnessForm()
    output_image_path = None
    input_image_path = None
    original_hist_path = None
    brightened_hist_path = None
    error = None
    
    if form.validate_on_submit() and 'image' in request.files:
        if form.captcha.data != "4":
            error = "Captcha answer is wrong!"
        else:
            original_image = Image.open(request.files['image'])
            image = original_image.copy() 
            
            r, g, b = image.split()
            
            brightness_value_red = (form.brightness_red.data / 255) + 1
            brightness_value_green = (form.brightness_green.data / 255) + 1
            brightness_value_blue = (form.brightness_blue.data / 255) + 1
            
            r = ImageEnhance.Brightness(r).enhance(brightness_value_red)
            g = ImageEnhance.Brightness(g).enhance(brightness_value_green)
            b = ImageEnhance.Brightness(b).enhance(brightness_value_blue)
            
            image = Image.merge("RGB", (r, g, b))
            
            input_image_path = "static/original.png"
            original_image.save(input_image_path)
            
            output_image_path = "static/brightened.png"
            image.save(output_image_path)

            create_histogram(input_image_path, "static/original_hist.png")
            create_histogram(output_image_path, "static/brightened_hist.png")

            original_hist_path = "original_hist.png"
            brightened_hist_path = "brightened_hist.png"

    return render_template('index.html', form=form, input_image=input_image_path, output_image=output_image_path, original_hist=original_hist_path, brightened_hist=brightened_hist_path, error=error)

if __name__ == '__main__':
    app.run(debug=True)