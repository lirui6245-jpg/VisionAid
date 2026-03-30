import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 页面与无障碍初始化
st.set_page_config(page_title="VisionAid 视障助手", page_icon="👁️", layout="centered")

# 核心业务逻辑：利用内存缓存消除冷启动延迟
@st.cache_resource(show_spinner=False)
def load_gemini_model():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("系统配置异常：未找到 API 密钥，请在 Streamlit 后台配置 Secrets。")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def main():
    st.title("👁️ VisionAid 智能视觉助手")
    st.markdown("### 请上传您前方的照片，我将为您描述周围的环境。")

    uploaded_file = st.file_uploader(label="上传照片 (支持 JPG/PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        try:
            image_bytes = uploaded_file.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            st.image(image, caption="已接收到图像", use_container_width=True)
        except Exception:
            st.error("图像读取失败，请重新上传。")
            return

        with st.spinner("AI 正在仔细观察当前环境，请稍候..."):
            try:
                model = load_gemini_model()
                prompt = "你现在是 VisionAid 助手。请精准描述画面主体、环境及潜在安全危险（如台阶、障碍物），语言简练顺口，50-100字。"
                response = model.generate_content([prompt, image])
                st.success(f"### **{response.text.strip()}**")
            except Exception:
                st.error("网络通信异常，请检查配置或稍后重试。")

if __name__ == "__main__":
    main()
