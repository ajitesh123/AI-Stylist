# Import the necessary libraries
import gradio as gr
import openai
import base64
from PIL import Image
import io
import requests
import os

# Consider using environment variables or a configuration file for API keys.
# WARNING: Do not hardcode API keys in your code, especially if sharing or using version control.
openai.api_key = os.getenv('OPENAI_API_KEY')
if openai.api_key is None:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# Function to encode the image to base64
def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

# Function to send the image to the OpenAI API and get a response
def ask_openai_with_image(image):
    # Encode the uploaded image to base64
    base64_image = encode_image_to_base64(image)
    
    # Create the new prompt for the fashion stylist and mother scenario
    prompt = f"You are a fashion stylist and a mother. I've uploaded an image of a dress. Please analyze the dress based on factors like color theory, texture, and other relevant criteria, and provide a verdict on whether I should keep or return the dress. Justify your verdict with a detailed explanation."

    # Create the payload with the base64 encoded image and the new prompt
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}"
                    }
                ]
            }
        ],
        "max_tokens": 4095
    }
    
    # Send the request to the OpenAI API
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {openai.api_key}"},
        json=payload
    )
    
    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()
        print("Response JSON:", response_json)  # Print the raw response JSON
        try:
            # Attempt to extract the content text
            return response_json["choices"][0]["message"]["content"]
        except Exception as e:
            # If there is an error in the JSON structure, print it
            print("Error in JSON structure:", e)
            print("Full JSON response:", response_json)
            return "Error processing the image response."
    else:
        # If an error occurred, return the error message
        return f"Error: {response.text}"

# Create a Gradio interface
iface = gr.Interface(
    fn=ask_openai_with_image,
    inputs=gr.Image(type="pil"),
    outputs="text",
    title="GPT-4 with Vision",
    description="Upload an image and get a description from GPT-4 with Vision."
)

# Launch the app
iface.launch()def handle_image_upload(request):
    # Get the uploaded image from the request
    uploaded_image = request.files['image']

    # Call the ask_openai_with_image function with the uploaded image
    response = ask_openai_with_image(uploaded_image)

    # Return the response as JSON
    return jsonify({'response': response})

@app.route('/upload-image', methods=['POST'])
def upload_image():
    return handle_image_upload(request)
