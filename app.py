import streamlit as st
import re
import requests
import base64
from io import BytesIO
import time

def transform_gdrive_link(link):
    """Transform Google Drive preview link to direct download link."""
    pattern = r"/d/([a-zA-Z0-9_-]+)/preview"
    match = re.search(pattern, link)
    
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return None

def download_image(url):
    """Download image from Google Drive URL."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return BytesIO(response.content)
        return None
    except:
        return None

def upload_to_imgbb(api_key, image_data):
    """Upload image to ImgBB and return the URL."""
    try:
        base64_image = base64.b64encode(image_data.getvalue()).decode('utf-8')
        
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": api_key,
            "image": base64_image,
        }
        
        response = requests.post(url, payload)
        
        if response.status_code == 200:
            json_response = response.json()
            return json_response['data']['url']
        return None
    except:
        return None

def main():
    st.set_page_config(
        page_title="Link Transformer & Uploader",
        page_icon="🔄",
        layout="wide"
    )
    
    st.title("🔄 Link Transformer & Uploader")
    
    tab1, tab2 = st.tabs(["Drive Link Transformer", "ImgBB Bulk Uploader"])
    
    with tab1:
        st.header("Google Drive Link Transformer")
        st.write("Transform preview links to direct download links")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            input_links = st.text_area(
                "Enter Google Drive preview links (one per line)",
                height=300,
                help="Example: https://drive.google.com/file/d/YOUR_FILE_ID/preview"
            )
        
        with col2:
            if input_links.strip():
                links = input_links.strip().split('\n')
                transformed_links = []
                
                for link in links:
                    if link.strip():
                        transformed = transform_gdrive_link(link.strip())
                        if transformed:
                            transformed_links.append(transformed)
                        else:
                            transformed_links.append(f"Invalid link: {link}")
                
                st.subheader("Transformed Links:")
                result_text = "\n".join(transformed_links)
                st.code(result_text, language=None)
                
                st.button(
                    "Copy Transformed Links",
                    key="copy_transformed",
                    help="Click to copy all transformed links",
                    on_click=lambda: st.write('<script>navigator.clipboard.writeText(`{}`);</script>'.format(result_text), unsafe_allow_html=True)
                )
    
    with tab2:
        st.header("ImgBB Bulk Uploader")
        st.write("Upload images from Google Drive to ImgBB")
        
        api_key = st.text_input(
            "Enter your ImgBB API Key",
            type="password",
            help="Get your API key from https://api.imgbb.com/"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            download_links = st.text_area(
                "Enter Google Drive direct download links (one per line)",
                height=300,
                help="Use transformed links from the previous tab"
            )
        
        with col2:
            if st.button("Upload to ImgBB"):
                if not api_key:
                    st.error("Please enter your ImgBB API Key")
                    return
                    
                if not download_links.strip():
                    st.error("Please enter some download links")
                    return
                
                links = download_links.strip().split('\n')
                imgbb_links = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, link in enumerate(links):
                    if link.strip():
                        status_text.text(f"Processing link {i+1} of {len(links)}...")
                        
                        image_data = download_image(link.strip())
                        if image_data:
                            imgbb_url = upload_to_imgbb(api_key, image_data)
                            if imgbb_url:
                                imgbb_links.append(imgbb_url)
                            else:
                                imgbb_links.append(f"Failed to upload: {link}")
                        else:
                            imgbb_links.append(f"Failed to download: {link}")
                    
                    progress_bar.progress((i + 1) / len(links))
                    time.sleep(0.1)  # Prevent rate limiting
                
                status_text.text("Processing complete!")
                
                st.subheader("ImgBB Links:")
                result_text = "\n".join(imgbb_links)
                st.code(result_text, language=None)
                
                st.button(
                    "Copy ImgBB Links",
                    key="copy_imgbb",
                    help="Click to copy all ImgBB links",
                    on_click=lambda: st.write('<script>navigator.clipboard.writeText(`{}`);</script>'.format(result_text), unsafe_allow_html=True)
                )

if __name__ == "__main__":
    main()