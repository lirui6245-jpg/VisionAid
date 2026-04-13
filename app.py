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
    """ AI 通信客户端类 """
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
    """ 无障碍渲染类：大字号渲染与隐形自动语音 """
    @staticmethod
    def render_markdown(text: str):
        st.success(f"### **{text}**")

    @staticmethod
    def trigger_tts_autoplay(text: str):
        """ 
        【核心突破】抛弃可视播放器，强行注入隐形自动播放标签 
        """
        try:
            tts = gTTS(text=text, lang='zh-cn')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
            
            # 删除了按钮，只保留隐形的 audio 标签，并强制加入 autoplay 属性
            audio_html = f"""
                <audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}"></audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.warning("语音播报引擎异常。")


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
        # ⚠️ 终极外挂：CSS 暴力魔改，打造全屏盲触体验
        # ==========================================
        custom_css = """
        <style>
        /* 隐藏顶部烦人的各种多余提示和边框 */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 将拍照按钮和清除照片(重拍)按钮放大到极其夸张的地步 */
        div[data-testid="stCameraInput"] button {
            transform: scale(2.0) !important;
            transform-origin: center center !important;
            margin-top: 50px !important;
            margin-bottom: 50px !important;
            padding: 20px !important;
            background-color: #28B463 !important; /* 强制绿色背景 */
            color: white !important;
            border-radius: 10px !important;
        }
        
        /* 翻转摄像头图标放大 */
        div[data-testid="stCameraInput"] button[title="Switch camera"] {
            transform: scale(3.0) !important;
            transform-origin: top right !important;
            background-color: rgba(0,0,0,0.6) !important;
        }
        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)

    def run_ui(self):
        # 极简标题
        st.markdown("<h2 style='text-align: center;'>👁️ 盲触极简版</h2>", unsafe_allow_html=True)

        camera_photo = st.camera_input("拍摄", label_visibility="collapsed")

        if camera_photo is not None:
            try:
                image_bytes = camera_photo.getvalue()
                image = self.image_processor.load_image_from_memory(image_bytes)
            except Exception:
                st.error("读取失败，请重拍。")
                return

            with st.spinner("解析中..."):
                try:
                    prompt = """
                    你现在是 VisionAid 智能视觉场景描述助手。
                    精准分析图像，转换为中文自然语言。
                    优先描述正中央主体。指出明显障碍物或危险。
                    通俗易懂，50字左右。
                    """
                    description = self.api_client.fetch_description(image, prompt)
                    
                    self.renderer.render_markdown(description)
                    self.renderer.trigger_tts_autoplay(description)

                except Exception as e:
                    st.error(f"网络异常: {e}")

if __name__ == "__main__":
    app = VisionAidApp()
    app.run_ui()
