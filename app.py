import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
from gtts import gTTS

class GeminiAPIClient:
    def __init__(self):
        self.api_key = self._load_credentials()

    def _load_credentials(self):
        try:
            return st.secrets["GEMINI_API_KEY"]
        except KeyError:
            st.error("系统严重异常：未读取到环境变量中的 API 密钥。")
            st.stop()

    @st.cache_resource(show_spinner=False)
    def _get_model(_self):
        genai.configure(api_key=_self.api_key)
        # ⚠️ 终于改对了！使用最新版 2.5 模型，彻底告别 404 报错
        return genai.GenerativeModel('gemini-2.5-flash')

    def fetch_description(self, image_obj, prompt) -> str:
        model = self._get_model()
        response = model.generate_content([prompt, image_obj])
        return response.text.strip()

class ImageProcessor:
    @staticmethod
    def load_image_from_memory(image_bytes):
        return Image.open(io.BytesIO(image_bytes))

class AccessibilityRenderer:
    @staticmethod
    def inject_custom_css():
        css = """
        <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        div[data-testid="stCameraInput"] button {
            transform: scale(2.2) !important;
            transform-origin: center center !important;
            margin: 40px auto !important;
            padding: 15px !important;
            background-color: #28B463 !important;
            color: white !important;
            border-radius: 12px !important;
            display: block !important;
        }
        div[data-testid="stCameraInput"] button[title="Switch camera"] {
            transform: scale(3.5) !important;
            transform-origin: top right !important;
            background-color: rgba(0,0,0,0.7) !important;
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    @staticmethod
    def render_markdown(text: str):
        st.success(f"### **{text}**")

    @staticmethod
    def trigger_invisible_audio(text: str):
        try:
            tts = gTTS(text=text, lang='zh-cn')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
            audio_html = f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception:
            st.warning("语音合成尝试失败。")

class VisionAidApp:
    def __init__(self):
        self.api_client = GeminiAPIClient()
        self.renderer = AccessibilityRenderer()
        self.image_processor = ImageProcessor()
        self.setup_page()

    def setup_page(self):
        st.set_page_config(page_title="VisionAid 视障助手", page_icon="👁️")
        self.renderer.inject_custom_css()

    def run_ui(self):
        st.markdown("<h2 style='text-align: center;'>👁️ VisionAid 语音视觉助手</h2>", unsafe_allow_html=True)
        st.write("---")
        camera_photo = st.camera_input("拍照探测环境", label_visibility="collapsed")

        if camera_photo is not None:
            image_bytes = camera_photo.getvalue()
            image = self.image_processor.load_image_from_memory(image_bytes)

            with st.spinner("AI 正在感知环境..."):
                try:
                    prompt = "你现在是 VisionAid 智能视觉场景描述助手。任务：精准分析用户拍摄的图像，将其转化为通顺的中文场景描述。1. 优先描述正中央主体及其动作。2. 指出明显的障碍物、台阶或安全危险。3. 语言精炼顺口，长度在 50 字以内，方便语音播报。"
                    description = self.api_client.fetch_description(image, prompt)
                    
                    self.renderer.render_markdown(description)
                    self.renderer.trigger_invisible_audio
