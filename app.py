import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
from gtts import gTTS

# ==========================================
# 面向对象架构 (OOAD) - 严格遵循第三周规划报告类图
# ==========================================

class GeminiAPIClient:
    """ 云端认知模块：负责与 Google Gemini 1.5/2.5 进行安全通信 """
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
        # 使用最新的 flash 模型平衡速度与精度
        genai.configure(api_key=_self.api_key)
        return genai.GenerativeModel('gemini-1.5-flash')

    def fetch_description(self, image_obj, prompt) -> str:
        """ 发起 HTTPS 融合数据包请求并提取 AI 场景描述 """
        model = self._get_model()
        response = model.generate_content([prompt, image_obj])
        return response.text.strip()


class ImageProcessor:
    """ 业务逻辑模块：负责图像字节流的预处理与内存管理 """
    @staticmethod
    def load_image_from_memory(image_bytes):
        """ 遵守零本地环境约束，完全在内存中转化图像流 """
        return Image.open(io.BytesIO(image_bytes))


class AccessibilityRenderer:
    """ 前端交互模块：负责无障碍渲染、CSS 注入与隐形语音自动播报 """
    @staticmethod
    def inject_custom_css():
        """ 
        【关键】CSS 暴力破解：强行放大官方组件按钮
        解决视障用户对微小图标点击困难的痛点
        """
        css = """
        <style>
        /* 隐藏不必要的网页页眉页脚 */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 强行放大拍照区域的两个核心按钮（拍照与清除） */
        div[data-testid="stCameraInput"] button {
            transform: scale(2.2) !important;
            transform-origin: center center !important;
            margin: 40px auto !important;
            padding: 15px !important;
            background-color: #28B463 !important; /* 醒目的绿色 */
            color: white !important;
            border-radius: 12px !important;
            display: block !important;
        }
        
        /* 强行放大右上角的翻转摄像头图标 */
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
        """ 渲染高对比度大字号文本 """
        st.success(f"### **{text}**")

    @staticmethod
    def trigger_invisible_audio(text: str):
        """ 
        【核心突破】隐形自动语音播报
        解决用户必须手动点击播放按键的交互冗余
        """
        try:
            tts = gTTS(text=text, lang='zh-cn')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            # 将音频转换为 Base64 编码，嵌入隐形 HTML 标签中尝试自动触发
            audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
            audio_html = f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception:
            st.warning("语音合成尝试失败。")


class VisionAidApp:
    """ 系统主控类：负责全生命周期的调度逻辑 """
    def __init__(self):
        self.setup_page()
        self.api_client = GeminiAPIClient()
        self.renderer = AccessibilityRenderer()
        self.image_processor = ImageProcessor()

    def setup_page(self):
        st.set_page_config(page_title="VisionAid 视障助手", page_icon="👁️")
        self.renderer.inject_custom_css()

    def run_ui(self):
        # 恢复你要求的标题
        st.markdown("<h2 style='text-align: center;'>👁️ VisionAid 语音视觉助手</h2>", unsafe_allow_html=True)
        st.write("---")

        # 核心交互入口：调用摄像头
        camera_photo = st.camera_input("拍照探测环境", label_visibility="collapsed")

        if camera_photo is not None:
            image_bytes = camera_photo.getvalue()
            image = self.image_processor.load_image_from_memory(image_bytes)

            with st.spinner("AI 正在感知环境..."):
                try:
                    # 预置无障碍场景感知提示词
                    prompt = """
                    你现在是 VisionAid 智能视觉场景描述助手。
                    任务：精准分析用户拍摄的图像，将其转化为通顺的中文场景描述。
                    1. 优先描述正中央主体及其动作。
                    2. 指出明显的障碍物、台阶或安全危险。
                    3. 语言精炼顺口，长度在 50 字以内，方便语音播报。
                    """
                    description = self.api_client.fetch_description(image, prompt)
                    
                    # 结果呈现：大字号显示 + 隐形自动语音
                    self.renderer.render_markdown(description)
                    self.renderer.trigger_invisible_audio(description)

                except Exception as e:
                    st.error(f"分析失败，请检查网络或密钥: {e}")

# 执行程序
if __name__ == "__main__":
    app = VisionAidApp()
    app.run_ui()
