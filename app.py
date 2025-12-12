import streamlit as st
import google.generativeai as genai
import os

# 1. 页面基础设置 (必须放在第一行)
st.set_page_config(page_title="AI_Rehab_Agent", page_icon=":hospital:")

# ==========================================
# 👇 核心修复区：智能密钥加载逻辑
# ==========================================
# 逻辑：先试着从云端(Secrets)拿，拿不到就用本地硬编码的。
# 这样你的代码既能在本地跑，也能在云端跑，不用改来改去。

my_key = None

# 尝试从 Streamlit Cloud 获取
if "GEMINI_API_KEY" in st.secrets:
    my_key = st.secrets["GEMINI_API_KEY"]
else:
    # 🔴 本地运行时的备用 Key (把你刚才申请的 Key 填在这里)
    my_key = "AIzaSyCXzMGmgJCPEUHantOiUJTDFDv4Ggik1fI"

# 初始化模型
model = None
try:
    if not my_key:
        st.error("❌ 未找到 API Key！请在本地填入代码第20行，或在云端配置 Secrets。")
        st.stop()
        
    genai.configure(api_key=my_key)
    
    # 使用最新的 Flash 模型
    model = genai.GenerativeModel('gemini-2.5-flash')

except Exception as e:
    st.error(f"❌ 模型初始化失败: {e}")
    st.info("如果 2.5-flash 报错，请尝试改回 'gemini-pro'")
    st.stop()

# ==========================================

# 3. 定义“陆主任”的人设 (已根据新战略更新为：高端医疗+运动医学)
system_prompt = """
你现在是“陆主任”，一位顶尖的运动医学康复专家（骨科/外科背景），同时非常熟悉保诚保险的《高端医疗计划 (VHIS/Global Medical)》条款。

你的任务是：
1. 【安抚与康复】：针对用户的运动损伤或骨科手术（如ACL重建、半月板修复、骨折），给出专业、温暖的康复建议（冰敷、抬高、早期活动等）。
2. 【保险植入】：在建议的最后，必须巧妙地通过“高端医疗险”视角提醒用户：
   - 强调“私家医院直付”优势：不用排队，可以使用最好的进口器材。
   - 强调“物理治疗(PT)报销”：提醒用户保单通常包含术后康复费用，鼓励他们去正规诊所做复健，不用省钱。
   - 提醒“预批核”：如果是建议手术，提醒用户先联系代理人做预批核(Pre-approval)。

请用口语化、长辈关怀的语气回答。不要太生硬。
"""

# 4. 侧边栏：模拟用户画像 (更新为骨科场景)
with st.sidebar:
    st.header("📋 客户档案模拟")
    surgery_type = st.selectbox("损伤/手术类型", ["前交叉韧带(ACL)重建", "半月板缝合", "滑雪骨折(胫腓骨)", "跟腱断裂"])
    days_post_op = st.slider("术后/伤后天数", 1, 180, 3)
    
    st.info("✅ 包含保诚高端医疗险逻辑")

# 5. 主界面
st.title("🏥 智能康复伴侣 (陆主任在线)")
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
    # 再次检查 model (双重保险)
    if not model:
        st.error("AI 模型未加载，请刷新。")
        st.stop()

    # 显示用户的话
    st.chat_message("user").write(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})

    # 构造发给 AI 的上下文
    full_prompt = f"{system_prompt}\n\n【用户当前状态】：做完 {surgery_type} 手术第 {days_post_op} 天。\n【用户问题】：{prompt}"

    # 调用 AI
    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            with st.spinner("陆主任正在思考..."):
                response = model.generate_content(full_prompt)
                ai_reply = response.text
            
            placeholder.write(ai_reply)
            # 保存回答
            st.session_state.history.append({"role": "model", "content": ai_reply})
            
        except Exception as e:
            st.error(f"连接出错: {e}")