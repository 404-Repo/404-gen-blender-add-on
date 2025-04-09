import bpy
import base64
import tempfile
import requests

def request_model(image_path:str, seed:int) ->  None|str:
    url = bpy.context.preferences.addons[__package__].preferences.url
    filepath = None

    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'seed': seed}

        response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        decoded_data = base64.b64decode(response.text)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ply") as temp_file:
            temp_file.write(decoded_data)
            filepath = temp_file.name

    return filepath