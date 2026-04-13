import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
from gtts import gTTS

# ==========================================
# 面向对象架构 (OOAD) - 严格遵循规划报告类图设计 [cite: 25, 29]
# ==========================================

class GeminiAPIClient:
    """ 云端认知模块：负责与 Google 大模型进行安全通信 [cite: 25] """
    def __init__(self):
        self.api_key = self._load_credentials()

    def _load_credentials(self):
        try:
            return st.secrets["GEMINI_API_KEY"]
        except KeyError:
            st.error("密钥缺失：请在 Streamlit 后台配置 GEMINI_API_KEY。")
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
    """ 业务逻辑模块：负责图像流预处理 [cite: 25] """
    @staticmethod
    def load_image_from_memory(image_bytes):
        return Image.open(io.BytesIO(image_bytes))

class AccessibilityRenderer:
    """ 前端交互模块：负责 CSS 注入与巨型语音交互 [cite: 25] """
    @staticmethod
    def inject_mobile_optimization():
        """ 
        【核心外挂】强行放大组件并移除干扰 
        """
        css = """
        <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 极致放大拍照按钮，占据屏幕下半部分 */
        div[data-testid="stCameraInput"] button {
            transform: scale(2.5) !important;
            margin: 60px auto !important;
            background-color: #28B463 !important;
            color: white !important;
            border-radius: 15px !important;
            height: 100px !important;
            width: 80% !important;
        }
        
        /* 极巨化翻转摄像头图标 */
        div[data-testid="stCameraInput"] button[title="Switch camera"] {
            transform: scale(4.0) !important;
            transform-origin: top right !important;
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    @staticmethod
    def trigger_giant_audio_trigger(text: str):
        """ 
        【交互突破】全屏盲触播放器
        由于手机系统禁止自动播放，我们创建一个覆盖全屏的“透明点击层”
        用户只要触摸屏幕，就能播放声音
        """
        try:
            tts = gTTS(text=text, lang='zh-cn')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
            
            # 构造一个充满屏幕的绿色巨型按钮，写着“点击听取播报”
            audio_html = f"""
                <audio id="v-audio" src="data:audio/mp3;base64,{audio_base64}"></audio>
                <button onclick="document.getElementById('v-audio').play()" 
                        style="width: 100%; height: 300px; margin-top: 20px; 
                               font-size: 32px; font-weight: bold; 
                               background-color: #28B463; color: white; 
                               border: none; border-radius: 20px;
                               box-shadow: 0 10px 20px rgba(0,0,0,0.3);">
                    🔊 结果已就绪 <br> [ 拍我听取播报 ]
                </button>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception:
            st.warning("语音播报尝试失败。")

class VisionAidApp:
    """ 主控应用类：调度系统生命周期 [cite: 29] """
    def __init__(self):
        self.api_client = GeminiAPIClient()
        self.renderer = AccessibilityRenderer()
        self.image_processor = ImageProcessor()
        self.setup_page()

    def setup_page(self):
        st.set_page_config(page_title="VisionAid", page_icon="👁️")
        self.renderer.inject_mobile_optimization()

    def run_ui(self):
        st.markdown("<h2 style='text-align: center;'>👁️ VisionAid 语音视觉助手</h2>", unsafe_allow_html=True)
        
        camera_photo = st.camera_input("拍照", label_visibility="collapsed")

        if camera_photo is not None:
            image_bytes = camera_photo.getvalue()
            image = self.image_processor.load_image_from_memory(image_bytes)

            with st.spinner("AI 正在感知环境..."):
                try:
                    prompt = "你现在是 VisionAid 智能助手。请用 50 字以内的中文描述图像中央的内容，并指出潜在危险。"
                    description = self.api_client.fetch_description(image, prompt)
                    
                    st.success(f"### **{description}**")
                    # 触发巨型点击播放器
                    self.renderer.trigger_giant_audio_trigger(description)
                except Exception as e:
                    st.error(f"分析失败: {e}")

if __name__ == "__main__":
    app = VisionAidApp()
    app.run_ui()
