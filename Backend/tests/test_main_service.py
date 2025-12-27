"""Test main service file"""
import os 


def test_converter(authorized_client , base_url, get_test_image):


    data = {
        "input_paths": [
            get_test_image
        ],
        "output_format": "tiff"
    }

    try:
        response = authorized_client.post(f"{base_url}/api/convert_to/image", json=data)
        assert response.status_code == 200, response.text

    except Exception as e:
        assert 1 == 2, f"Convert service failed: {str(e)}"

def test_compressor(authorized_client, base_url, get_test_image):

    data = {
        "input_paths": [
            get_test_image
        ],
        "quality": 30
    }

    try:
        response = authorized_client.post(f"{base_url}/api/compress/image", json=data)
        
        assert response.status_code == 200, response.text 
    except Exception as e:
        assert 1 == 2, f"Compress image failed: {str(e)}"

def test_removebg(authorized_client, base_url, get_test_image):

    data = {
        "input_paths": [
            get_test_image
        ]
    }

    try:
        response = authorized_client.post(f"{base_url}/api/remove_background", json=data)
        
        assert response.status_code == 200, response.text 
    except Exception as e:
        assert 1 == 2, f"Compress image failed: {str(e)}"
