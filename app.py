import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ==========================================
# 一、 页面与无障碍 (A11y) 初始化配置
# ==========================================
st.set_page_config(
    page_title="VisionAid 视障助手", 
    page_icon="👁️", 
    layout="centered"
)

# ==========================================
# 二、 核心业务逻辑与性能调优
# ==========================================
@st.cache_resource(show_spinner=False)
def load_gemini_model():
    """
    初始化 Gemini 模型实例。
    """
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("系统配置异常：未找到 API 密钥，请在 Streamlit 后台配置 Secrets。")
        st.stop()
        
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

# ==========================================
# 三、 前端 UI 与主程序逻辑
# ==========================================
def main():
    st.title("👁️ VisionAid 智能视觉助手")
    st.markdown("### 请上传您前方的照片，我将为您描述周围的环境。")

    uploaded_file = st.file_uploader(
        label="上传照片 (支持 JPG/PNG)", 
        type=["jpg", "jpeg", "png"], 
        help="点击此处选择或拍摄照片"
    )

    if uploaded_file is not None:
        try:
            image_bytes = uploaded_file.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            st.image(image, caption="已接收到图像", use_container_width=True)
        except Exception:
            st.error("抱歉，图像读取失败，请尝试重新上传。")
            return

        with st.spinner("AI 正在仔细观察当前环境，请稍候..."):
            try:
                model = load_gemini_model()
                
                prompt = """
                你现在是 VisionAid——一款专为视障人士设计的智能视觉场景描述助手。
                你的任务是精准、客观地分析用户上传的图像，并将其转化为通顺的中文自然语言描述。
                请严格遵循以下原则：
                1. 核心优先：优先描述画面正中央、最突出的主体及其动作。
                2. 环境感知：简要说明主体所处的环境和当前光线/天气状态。
                3. 安全预警：如果画面中存在明显的障碍物、台阶、红绿灯或潜在危险，请务必在描述中明确指出。
                4. 语音友好：语言必须通俗易懂、简练顺口，总长度控制在 50-100 字以内。
                """
                
                response = model.generate_content([prompt, image])
                description = response.text.strip()
                
                st.success(f"### **{description}**")
                
            except Exception as e:
                # 关键修改：直接把底层真实的英文错误日志抛到前端页面上
                st.error(f"侦测到真实错误，详情如下：{e}")

if __name__ == "__main__":
    main()
