import streamlit as st
import google.generativeai as genai
import os

# 1. 页面基础设置 (必须放在第一行)
# 我们用英文标题和标准图标，防止报错
st.set_page_config(page_title="AI_Rehab_Agent", page_icon=":hospital:")

# ==========================================
# 👇 请在这里填入你的新 Key！
# ==========================================
# 从 Streamlit 的云端保险箱里读取 Key
# 如果是在本地运行，它会报错，除非你建立了 .streamlit/secrets.toml
# 但为了部署，我们直接用这就行
try:
    my_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=my_key)
except Exception as e:
    st.error("这是在云端运行吗？没找到密钥。请在 Streamlit Cloud 的 Secrets 设置里填入 GEMINI_API_KEY")
    st.stop()
    # 建立模型 (使用官方原生的 flash 模型，速度快且免费)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"API Key 配置出错，请检查: {e}")
    st.stop()

# ==========================================

# 3. 定义“陆主任”的人设 (核心资产)
system_prompt = """
你现在是“陆主任”，一位顶尖的运动医学康复专家，同时非常熟悉保诚保险的《危疾加护保 III (CIE3)》条款。

你的任务是：
1. 【安抚与康复】：针对用户的手术（如ACL重建、骨折、中风），给出专业、温暖的康复建议。
2. 【保险植入】：在建议的最后，必须巧妙地通过“保险视角”提醒用户。
   - 如果是癌症/心脏病/中风，提到 CIE3 的“严重疾病延伸保障”需要 1 年等候期，鼓励他们利用这段时间好好康复。
   - 提到“安心医”服务可以帮他们找海外专家。

请用口语化、长辈关怀的语气回答。不要太生硬。
"""

# 4. 侧边栏：模拟用户画像
with st.sidebar:
    st.header("📋 客户档案模拟")
    surgery_type = st.selectbox("手术类型", ["前交叉韧带(ACL)重建", "髋关节置换", "中风后康复", "肺癌术后"])
    days_post_op = st.slider("术后天数", 1, 365, 7)
    insurance_status = st.checkbox("已购买保诚 CIE3", value=True)

# 5. 主界面
st.title("🏥 智能康复伴侣 (官方源)")
st.caption(f"当前模拟场景：{surgery_type} - 术后第 {days_post_op} 天")

# 初始化聊天记录
if "history" not in st.session_state:
    st.session_state.history = []

# 显示历史消息
for message in st.session_state.history:
    role = "user" if message["role"] == "user" else "assistant"
    st.chat_message(role).write(message["content"])

# 6. 处理用户输入
if prompt := st.chat_input("请描述您现在的身体感觉..."):
    # 显示用户的话
    st.chat_message("user").write(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})

    # 构造发给 AI 的上下文 (把人设和用户情况拼在一起)
    full_prompt = f"{system_prompt}\n\n【用户当前状态】：做完 {surgery_type} 手术第 {days_post_op} 天。\n【用户问题】：{prompt}"

    # 调用 AI
    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            with st.spinner("陆主任正在思考..."):
                # 官方库生成内容
                response = model.generate_content(full_prompt)
                ai_reply = response.text
            
            placeholder.write(ai_reply)
            # 保存回答
            st.session_state.history.append({"role": "model", "content": ai_reply})
            
        except Exception as e:
            st.error(f"连接出错: {e}")