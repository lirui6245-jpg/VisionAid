import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
from gtts import gTTS
# 引入第三方后置摄像头组件
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
        # ⚠️ 紧急替换：换成拥有极高免费额度、速度最快的 8b 模型，确保演示万无一失
        return genai.GenerativeModel('gemini-1.5-flash-8b')

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
        # 保持极简无边框界面
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
    def trigger_audio_with_fallback(text: str):
        """
        【终极语音方案】
        尝试自动播放。如果被手机安全机制拦截，则提供巨型盲触播放按钮作为安全网。
        """
        try:
            tts = gTTS(text=text, lang='zh-cn')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            # 使用 audio/mpeg 提高在 iOS 设备上的兼容性
            audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
            
            # 双重保险：自动播放属性 + 巨型盲触备用按钮
            audio_html = f"""
                <audio id="visionaid-audio" autoplay="autoplay" src="data:audio/mpeg;base64,{audio_base64}"></audio>
                <button onclick="document.getElementById('visionaid-audio').play()" 
                        style="width: 100%; padding: 60px 20px; margin-top: 15px; font-size: 32px; 
                               font-weight: bold; background-color: #E74C3C; color: white; 
                               border: none; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.3); 
                               cursor: pointer;">
                    🔊 若手机未自动播报<br><br>请盲按此处播放语音
                </button>
            """
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
        st.markdown("<h4 style='text-align: center; color: #28B463;'>👇 直接点击下方画面任意位置拍照 👇</h4>", unsafe_allow_html=True)
        
        # 使用黑客组件：无按钮、默认后置、全屏盲触拍照
        camera_photo = back_camera_input()

        if camera_photo is not None:
            image_bytes = camera_photo.getvalue()
            image = self.image_processor.load_image_from_memory(image_bytes)

            with st.spinner("AI 正在感知环境..."):
                try:
                    prompt = "你现在是 VisionAid 智能视觉场景描述助手。任务：精准分析用户拍摄的图像，将其转化为通顺的中文场景描述。1. 优先描述正中央主体及其动作。2. 指出明显的障碍物、台阶或安全危险。3. 语言精炼顺口，长度在 50 字以内，方便语音播报。"
                    description = self.api_client.fetch_description(image, prompt)
                    
                    # 渲染文字并执行语音双重保险方案
                    self.renderer.render_markdown(description)
                    self.renderer.trigger_audio_with_fallback(description)
                except Exception as e:
                    st.error(f"分析失败，请检查网络或密钥: {e}")

if __name__ == "__main__":
    app = VisionAidApp()
    app.run_ui()
