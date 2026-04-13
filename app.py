import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
from gtts import gTTS
# ⚠️ 引入新的第三方后置摄像头专属组件
from streamlit_back_camera_input import back_camera_input

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
        # 清理掉了之前那些导致界面变形的“暴力放大”代码
        # 只保留隐藏页眉页脚，还原最清爽的界面
        css = """
        <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
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
        st.markdown("<h4 style='text-align: center; color: #28B463;'>👇 盲触模式：直接点击下方画面任意位置拍照 👇</h4>", unsafe_allow_html=True)
        
        # ⚠️ 核心替换：使用不需要按钮、默认后置的黑客组件
        camera_photo = back_camera_input()

        if camera_photo is not None:
            image_bytes = camera_photo.getvalue()
            image = self.image_processor.load_image_from_memory(image_bytes)

            with st.spinner("AI 正在感知环境..."):
                try:
                    prompt = "你现在是 VisionAid 智能视觉场景描述助手。任务：精准分析用户拍摄的图像，将其转化为通顺的中文场景描述。1. 优先描述正中央主体及其动作。2. 指出明显的障碍物、台阶或安全危险。3. 语言精炼顺口，长度在 50 字以内，方便语音播报。"
                    description = self.api_client.fetch_description(image, prompt)
                    
                    self.renderer.render_markdown(description)
                    self.renderer.trigger_invisible_audio(description)
                except Exception as e:
                    st.error(f"分析失败，请检查网络或密钥: {e}")

if __name__ == "__main__":
    app = VisionAidApp()
    app.run_ui()
