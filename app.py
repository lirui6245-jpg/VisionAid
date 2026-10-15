import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageStat
import io
import base64
import time
from gtts import gTTS
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
        # Gemini 2.5 Flash
        return genai.GenerativeModel('gemini-2.5-flash')

    def fetch_description(self, image_obj, prompt) -> str:
        model = self._get_model()
        response = model.generate_content([prompt, image_obj])
        return response.text.strip()

class ImageProcessor:
    @staticmethod
    def load_image_from_memory(image_bytes):
        return Image.open(io.BytesIO(image_bytes))

    @staticmethod
    def is_image_valid(image) -> tuple[bool, str]:
        """
        Frame validity gate.

        Computes the mean brightness of the frame on-device and rejects
        frames that are essentially black or blocked by a finger, so that
        no model call is spent on obviously unusable input.
        """
        grayscale_image = image.convert("L")
        stat = ImageStat.Stat(grayscale_image)
        mean_brightness = stat.mean[0]
        
        # Below 15 is treated as too dark or obstructed
        if mean_brightness < 15: 
            return False, "镜头可能被手指遮挡，或环境光线极暗，请调整手机后重试。"
        return True, ""

class AccessibilityRenderer:
    @staticmethod
    def inject_custom_css():
        """
        Injects the high-contrast stylesheet tuned for low-vision users.
        """
        css = """
        <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        /* High-contrast result card */
        .a11y-card {
            background-color: #1A1A1A;
            border-left: 8px solid #FFD700;
            padding: 20px;
            border-radius: 12px;
            margin-top: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        }
        .a11y-text {
            color: #FFFFFF;
            font-size: 24px;
            line-height: 1.6;
            font-weight: bold;
        }
        /* Pulsing status indicator, shown while the model is working */
        .pulse-text {
            color: #28B463;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { opacity: 0.4; }
            50% { opacity: 1; }
            100% { opacity: 0.4; }
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    @staticmethod
    def render_markdown(text: str):
        # Large bold type on the custom high-contrast card
        html = f"""
        <div class="a11y-card">
            <div class="a11y-text">### **{text}**</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def render_system_status(status: str):
        st.markdown(f"<div class='pulse-text'>⏳ {status}</div>", unsafe_allow_html=True)

    @staticmethod
    def trigger_audio_with_fallback(text: str):
        try:
            tts = gTTS(text=text, lang='zh-cn')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
            
            audio_html = f"""
                <audio id="visionaid-audio" autoplay="autoplay" src="data:audio/mpeg;base64,{audio_base64}"></audio>
                <button onclick="document.getElementById('visionaid-audio').play()" 
                        style="width: 100%; padding: 40px 10px; margin-top: 20px; font-size: 26px; 
                               font-weight: bold; background-color: #E74C3C; color: white; 
                               border: none; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.3); 
                               cursor: pointer;">
                    🔊 若未自动播报，请盲按此处播放
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

        # Session state: short-term scene memory and the rate-limit timestamp
        if 'scene_history' not in st.session_state:
            st.session_state.scene_history = "这是首次扫描，尚无历史参照。"
        if 'last_request_time' not in st.session_state:
            st.session_state.last_request_time = 0.0

    def setup_page(self):
        st.set_page_config(page_title="VisionAid 视障助手", page_icon="👁️")
        self.renderer.inject_custom_css()

    def run_ui(self):
        st.markdown("<h2 style='text-align: center;'>👁️ VisionAid 语音视觉助手</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #28B463;'>👇 直接点击下方画面任意位置拍照 👇</h4>", unsafe_allow_html=True)
        
        camera_photo = back_camera_input()

        if camera_photo is not None:
            # Rate limiter: guards against double taps and repeated frames
            current_time = time.time()
            if current_time - st.session_state.last_request_time < 5.0:
                msg = "操作过于频繁，系统需要5秒冷却时间，请稍后再拍。"
                self.renderer.render_markdown(msg)
                self.renderer.trigger_audio_with_fallback(msg)
                return

            image_bytes = camera_photo.getvalue()
            image = self.image_processor.load_image_from_memory(image_bytes)

            # 1. Validate the frame
            is_valid, error_msg = self.image_processor.is_image_valid(image)
            if not is_valid:
                self.renderer.render_markdown(error_msg)
                self.renderer.trigger_audio_with_fallback(error_msg)
                return

            # Record the timestamp of this accepted request
            st.session_state.last_request_time = current_time

            # 2. Show the processing indicator
            self.renderer.render_system_status("AI 正在深度感知当前环境，请稍候...")

            try:
                current_history = st.session_state.scene_history
                prompt = f"""
                你现在是 VisionAid 智能视觉场景描述助手。
                【短时记忆】：用户上一秒看到的场景是：“{current_history}”。
                【当前任务】：精准分析新图像。如果与记忆相似，请指出“环境发生了什么变化”（如物体靠近、障碍物移动）。
                优先描述正中央主体。字数严格控制在50字以内，语言口语化。
                """
                description = self.api_client.fetch_description(image, prompt)
                
                st.session_state.scene_history = description
                
                self.renderer.render_markdown(description)
                self.renderer.trigger_audio_with_fallback(description)
            except Exception as e:
                st.error(f"分析失败，请检查网络: {e}")

if __name__ == "__main__":
    app = VisionAidApp()
    app.run_ui()
