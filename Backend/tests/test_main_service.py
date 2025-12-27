"""Test main service file"""

def test_converter(authorized_client , base_url):

    data = {
        "input_paths": [
            "D:\\Downloads\\ready.webp"
        ],
        "output_format": "tiff"
    }

    try:
        response = authorized_client.post(f"{base_url}/api/convert_to/image", json=data)
        assert response.status_code == 200, response.text

    except Exception as e:
        assert 1 == 2, f"Convert service failed: {str(e)}"

def test_compressor(authorized_client, base_url):

    data = {
        "input_paths": [
            "D:\\Ryan\\Saved Pictures\\z6193229319145_0422e4545890575de9bf68717f63b732.jpg"
        ],
        "quality": 30
    }

    try:
        response = authorized_client.post(f"{base_url}/api/compress/image", json=data)
        
        assert response.status_code == 200, response.text 
    except Exception as e:
        assert 1 == 2, f"Compress image failed: {str(e)}"

def test_removebg(authorized_client, base_url):

    data = {
        "input_paths": [
            "D:\\Ryan\\Saved Pictures\\z6193229319145_0422e4545890575de9bf68717f63b732.jpg"
        ]
    }

    try:
        response = authorized_client.post(f"{base_url}/api/remove_background", json=data)
        
        assert response.status_code == 200, response.text 
    except Exception as e:
        assert 1 == 2, f"Compress image failed: {str(e)}"
