import requests

def update_documents():
    """
    Send request to update documents endpoint
    """
    try:
        response = requests.post('http://localhost:8000/update-documents')
        print(f"Update status: {response.status_code}")
        print(response.json())
    except Exception as e:
        print(f"Error updating documents: {e}")

if __name__ == "__main__":
    update_documents() 