import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from gtts import gTTS

# ==========================================
# 面向对象架构 (OOAD) - 契合第三周类图设计方案
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
        # 利用单例模式与内存缓存消除冷启动延迟
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        # 注意：此处已升级为最新版本的模型
        return genai.GenerativeModel('gemini-2.5-flash')

    def fetch_description(self, image_obj, prompt) -> str:
        """ 发起 HTTPS 融合数据包请求并提取中文响应 """
        response = self._initialize_model().generate_content([prompt, image_obj])
        return response.text.strip()


class ImageProcessor:
    """ 图像处理工具类：负责图像字节流的安全转换与内存管理 """
    @staticmethod
    def load_image_from_memory(image_bytes):
        """ 严格遵守零本地环境约束，完全在内存中转化图像流 """
        return Image.open(io.BytesIO(image_bytes))


class AccessibilityRenderer:
    """ 无障碍渲染类：负责大字号高对比度渲染与 TTS 语音合成 """
    @staticmethod
    def render_markdown(text: str):
        """ 强制使用 H3 级别粗体，适配 VoiceOver/TalkBack """
        st.success(f"### **{text}**")

    @staticmethod
    def trigger_tts_autoplay(text: str):
        """ 
        生成语音并在前端播放
        【修复】解决移动端/微信内置浏览器的音频解码报错与自动播放拦截问题
        """
        try:
            tts = gTTS(text=text, lang='zh-cn')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            # 关键修复 1：不要直接传对象，而是读取出真实的 bytes 字节流
            audio_bytes = audio_fp.read()
            
            # 关键修复 2：将 format 改为更兼容的 "audio/mpeg"
            # 关键修复 3：关闭 autoplay=False，绕过浏览器的静音拦截，改为让用户手动点击播放
            st.audio(audio_bytes, format="audio/mpeg", autoplay=False)
            
        except Exception as e:
            st.warning("语音播报引擎暂时不可用，请依赖系统屏幕朗读器。")

class VisionAidApp:
    """ 主控应用类：生命周期调度与 UI 渲染决策中枢 """
    def __init__(self):
        self.setup_page()
        self.api_client = GeminiAPIClient()
        self.renderer = AccessibilityRenderer()
        self.image_processor = ImageProcessor()

    def setup_page(self):
        st.set_page_config(page_title="VisionAid 视障助手", page_icon="👁️", layout="centered")

    def run_ui(self):
        st.title("👁️ VisionAid 语音视觉助手")
        st.markdown("#### 📱 请点击下方按钮拍摄前方环境")

        # 核心交互升级：直接唤醒移动端摄像头，摒弃繁琐的上传流程
        camera_photo = st.camera_input("拍摄环境照片", label_visibility="collapsed")

        if camera_photo is not None:
            try:
                # 内存级图像流注入
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
                    3. 安全预警：如果画面中存在明显的障碍物、台阶或潜在危险，请务必明确指出。
                    4. 语音友好：语言必须通俗易懂、简练顺口，总长度控制在 50 字左右，方便后续转化为语音播报。
                    """
                    # 数据交接与远端推理
                    description = self.api_client.fetch_description(image, prompt)
                    
                    # 视觉隔离渲染
                    self.renderer.render_markdown(description)
                    
                    # 触发 TTS 自动语音播报
                    self.renderer.trigger_tts_autoplay(description)

                except Exception as e:
                    st.error(f"网络通信异常，详情: {e}")


# ==========================================
# 程序的唯一执行入口
# ==========================================
if __name__ == "__main__":
    app = VisionAidApp()
    app.run_ui()
