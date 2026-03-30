import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
from gtts import gTTS

# ==========================================
# 面向对象架构 (OOAD) - 核心功能矩阵区块
# ==========================================

class GeminiAPIClient:
    """ AI 通信客户端类：负责与 Google大模型进行安全交互 """
    def __init__(self):
        self.api_key = self._load_credentials()
        self.model = self._initialize_model()

    def _load_credentials(self):
        try:
            return st.secrets["GEMINI_API_KEY"]
        except KeyError:
            st.error("系统严重异常：未读取到环境变量中的 API 密钥。")
            st.stop()

    @staticmethod
    @st.cache_resource(show_spinner=False)
    def _initialize_model():
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')

    def fetch_description(self, image_obj, prompt) -> str:
        response = self._initialize_model().generate_content([prompt, image_obj])
        return response.text.strip()


class ImageProcessor:
    """ 图像处理工具类 """
    @staticmethod
    def load_image_from_memory(image_bytes):
        return Image.open(io.BytesIO(image_bytes))


class AccessibilityRenderer:
    """ 无障碍渲染类：大字号渲染与巨型 TTS 语音按钮 """
    @staticmethod
    def render_markdown(text: str):
        st.success(f"### **{text}**")

    @staticmethod
    def trigger_tts_autoplay(text: str):
        try:
            tts = gTTS(text=text, lang='zh-cn')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
            
            # 巨型语音播放按钮
            audio_html = f"""
                <audio id="visionaid-audio" src="data:audio/mp3;base64,{audio_base64}"></audio>
                <button onclick="document.getElementById('visionaid-audio').play()" 
                        style="width: 100%; padding: 35px; margin-top: 20px; font-size: 30px; 
                               font-weight: bold; background-color: #28B463; color: white; 
                               border: none; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.2); 
                               cursor: pointer;">
                    🔊 点击播放语音播报
                </button>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.warning("语音播报引擎暂时不可用，请依赖系统屏幕朗读器。")


class VisionAidApp:
    """ 主控应用类 """
    def __init__(self):
        self.setup_page()
        self.api_client = GeminiAPIClient()
        self.renderer = AccessibilityRenderer()
        self.image_processor = ImageProcessor()

    def setup_page(self):
        st.set_page_config(page_title="VisionAid 视障助手", page_icon="👁️", layout="centered")
        
        # ==========================================
        # ⚠️ 核心外挂：CSS 暴力破解官方摄像头组件 UI
        # ==========================================
        custom_css = """
        <style>
        /* 强行放大整个摄像头组件区域内的主要按键（拍照/清除） */
        div[data-testid="stCameraInput"] button {
            transform: scale(1.8) !important;
            transform-origin: center center !important;
            margin-top: 25px !important;
            margin-bottom: 25px !important;
        }
        
        /* 强行超级放大右上角的“翻转摄像头”图标按钮，方便盲触 */
        div[data-testid="stCameraInput"] button[title="Switch camera"],
        div[data-testid="stCameraInput"] button[kind="icon"] {
            transform: scale(2.5) !important;
            transform-origin: top right !important;
            background-color: rgba(0,0,0,0.5) !important; /* 加深底色提高对比度 */
            border-radius: 10px !important;
        }
        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)

    def run_ui(self):
        st.title("👁️ VisionAid 语音视觉助手")
        st.markdown("#### 📱 请盲按下方巨大区域拍摄环境")

        camera_photo = st.camera_input("拍摄环境照片", label_visibility="collapsed")

        if camera_photo is not None:
            try:
                image_bytes = camera_photo.getvalue()
                image = self.image_processor.load_image_from_memory(image_bytes)
            except Exception:
                st.error("摄像头数据读取失败，请重试。")
                return

            with st.spinner("AI 正在解析环境，正在生成语音..."):
                try:
                    prompt = """
                    你现在是 VisionAid——一款专为视障人士设计的智能视觉场景描述助手。
                    你的任务是精准、客观地分析用户拍摄的图像，并将其转化为通顺的中文自然语言描述。
                    请严格遵循以下原则：
                    1. 核心优先：优先描述画面正中央、最突出的主体及其动作。
                    2. 环境感知：简要说明主体所处的环境。
                    3. 安全预警：如果存在明显障碍物或潜在危险，请务必明确指出。
                    4. 语音友好：语言必须通俗易懂、简练顺口，50字左右。
                    """
                    description = self.api_client.fetch_description(image, prompt)
                    self.renderer.render_markdown(description)
                    self.renderer.trigger_tts_autoplay(description)

                except Exception as e:
                    st.error(f"网络通信异常，详情: {e}")

if __name__ == "__main__":
    app = VisionAidApp()
    app.run_ui()
