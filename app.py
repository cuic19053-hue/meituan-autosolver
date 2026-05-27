import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. 全局配置与黑金赛博风 CSS 注入
# ==========================================
st.set_page_config(
    page_title="MEITUAN AUTOSOLVER 1.0",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 严苛视觉要求：深煤灰背景，美团黄边框，发光效果，隐藏原生UI
st.markdown("""
    <style>
    /* 彻底重写基础变量，封杀默认蓝紫色 */
    :root {
        --dark-bg: #111111;
        --mt-yellow: #FFD000;
        --neon-green: #00FF41;
        --alert-orange: #FF4B2B;
        --card-bg: rgba(30, 30, 30, 0.8);
    }
    
    /* 隐藏 Streamlit 默认头部和底部 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 强制全局深色背景 */
    .stApp {
        background-color: var(--dark-bg);
        color: #FFFFFF;
    }

    /* 工业风卡片容器样式 */
    .cyber-card {
        background-color: var(--card-bg);
        border: 1px solid var(--mt-yellow);
        box-shadow: 0 0 15px rgba(255, 208, 0, 0.15);
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 20px;
        position: relative;
    }
    /* 卡片四角的机械装饰点 */
    .cyber-card::before { content: ''; position: absolute; top: 0; left: 0; width: 10px; height: 10px; border-top: 2px solid var(--mt-yellow); border-left: 2px solid var(--mt-yellow); }
    .cyber-card::after { content: ''; position: absolute; bottom: 0; right: 0; width: 10px; height: 10px; border-bottom: 2px solid var(--mt-yellow); border-right: 2px solid var(--mt-yellow); }

    /* 呼吸灯效果 */
    @keyframes breathe {
        0% { text-shadow: 0 0 5px var(--neon-green); opacity: 0.8; }
        50% { text-shadow: 0 0 20px var(--neon-green), 0 0 30px var(--neon-green); opacity: 1; }
        100% { text-shadow: 0 0 5px var(--neon-green); opacity: 0.8; }
    }
    .breathing-light {
        color: var(--neon-green);
        animation: breathe 2s infinite;
        font-weight: bold;
    }

    /* 黑客帝国终端流样式 */
    .matrix-terminal {
        background-color: #050505;
        border: 1px solid #333;
        color: var(--neon-green);
        font-family: 'Courier New', Courier, monospace;
        font-size: 13px;
        padding: 15px;
        height: 350px;
        overflow-y: hidden;
        text-shadow: 0 0 3px rgba(0, 255, 65, 0.5);
        line-height: 1.6;
        display: flex;
        flex-direction: column;
        justify-content: flex-end; /* 自动顶起旧日志 */
    }

    /* 发光巨型数字 */
    .glowing-score {
        font-size: 5rem;
        font-weight: 900;
        text-align: center;
        color: var(--mt-yellow);
        text-shadow: 0 0 20px var(--mt-yellow), 0 0 40px rgba(255,208,0,0.5);
        margin: 0;
        line-height: 1.1;
        font-family: 'Impact', sans-serif;
    }

    /* 巨型执行按钮深度定制 */
    .stButton>button {
        width: 100%;
        height: 60px;
        background-color: var(--mt-yellow) !important;
        color: #000000 !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        border-radius: 0px !important;
        border: none !important;
        box-shadow: 0 0 20px rgba(255, 208, 0, 0.4) !important;
        transition: all 0.1s ease-in-out;
    }
    .stButton>button:active {
        transform: scale(0.98);
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5) !important;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. Agent 核心逻辑预留接口 (Generator)
# ==========================================
def agent_logic(iterations=20):
    """
    预留接口：今晚获取真实数据后，在此处替换计算逻辑。
    目前通过 yield 模拟 Agent 在每一次反思迭代中的数据流输出。
    """
    score = 55.0
    history_scores = [score]
    logs = []
    
    for i in range(1, iterations + 1):
        time.sleep(0.3) # 模拟计算延迟
        
        # 1. 模拟分数攀升
        score += np.random.uniform(0.5, 3.5) if score < 95 else np.random.uniform(0.1, 0.5)
        history_scores.append(score)
        
        # 2. 模拟终端日志 (Thought Trace)
        status = "CRITICAL" if np.random.random() > 0.8 else "NOMINAL"
        log_line = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] ITER_{i:02d} | TRACE: Re-routing node {np.random.randint(100, 999)}... STATUS: {status}"
        if status == "CRITICAL":
            log_line = f"<span style='color: var(--alert-orange);'>[WARN] CONSTRAINT VIOLATION DETECTED. INITIATING REFLEXION...</span><br/>" + log_line
        logs.append(log_line)
        
        # 3. 模拟状态矩阵数据 (Status Matrix Heatmap) - 值越小表示缺口越大(越接近橘色)
        matrix_data = np.random.uniform(0, 100, (8, 8))
        
        # 4. 模拟雷达图齐套率
        radar_data = [min(100, 50 + (i * 2.5) + np.random.randint(-5, 5)) for _ in range(5)]
        
        yield {
            "iter": i,
            "progress": int((i / iterations) * 100),
            "score": score,
            "history_scores": history_scores,
            "logs": logs[-12:], # 仅保留最后12条避免溢出
            "matrix": matrix_data,
            "radar": radar_data
        }


# ==========================================
# 3. 页面布局：HUD Header
# ==========================================
hud_html = f"""
<div style="display: flex; justify-content: space-between; align-items: center; background: #000; border-bottom: 2px solid var(--mt-yellow); padding: 5px 20px; margin-bottom: 20px;">
    <div style="color: var(--mt-yellow); font-weight: 900; font-size: 18px; letter-spacing: 2px;">MEITUAN AI AUTOSOLVER 1.0 // LOGISTICS BRAIN</div>
    <div class="breathing-light">● AI CORE CONNECTED & ONLINE</div>
    <div style="color: #A3A3A3; font-family: monospace;">SYS_LOAD: 42% | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>
"""
st.markdown(hud_html, unsafe_allow_html=True)


# ==========================================
# 4. 页面布局：三栏 Dashboard 占位符
# ==========================================
col_left, col_mid, col_right = st.columns([1, 1.2, 1], gap="medium")

with col_left:
    st.markdown("<h4 style='color: #FFF; text-align: center; border-bottom: 1px solid #333; padding-bottom: 10px;'>:: 零件短缺矩阵 ::</h4>", unsafe_allow_html=True)
    matrix_placeholder = st.empty()
    
with col_mid:
    st.markdown("<h4 style='color: #FFF; text-align: center; border-bottom: 1px solid #333; padding-bottom: 10px;'>:: AGENT 核心演算中枢 ::</h4>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
    score_placeholder = st.empty()
    st.markdown("<div style='text-align: center; color: #777; margin-bottom: 10px;'>CURRENT OPTIMAL UTILITY SCORE</div>", unsafe_allow_html=True)
    terminal_placeholder = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<h4 style='color: #FFF; text-align: center; border-bottom: 1px solid #333; padding-bottom: 10px;'>:: 效能与齐套分析 ::</h4>", unsafe_allow_html=True)
    line_placeholder = st.empty()
    radar_placeholder = st.empty()

# 底部执行按钮区域
st.markdown("<br><br>", unsafe_allow_html=True)
start_btn = st.button("▶ EXECUTE AUTOMATED ALLOCATION STRATEGY (EXE_SOLVER)")
progress_bar = st.empty()


# ==========================================
# 5. 执行渲染循环与图表生成
# ==========================================
if start_btn:
    for state in agent_logic(iterations=30):
        
        # --- 渲染左侧：矩阵热力图 ---
        fig_matrix = go.Figure(data=go.Heatmap(
            z=state["matrix"],
            colorscale=[[0, '#FF4B2B'], [0.4, '#FFD000'], [1, '#111111']], # 警示橙 -> 美团黄 -> 深煤灰
            showscale=False,
            xgap=2, ygap=2
        ))
        fig_matrix.update_layout(
            margin=dict(l=0, r=0, t=0, b=0), height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False)
        )
        matrix_placeholder.plotly_chart(fig_matrix, width='stretch', config={'displayModeBar': False}, key=f"matrix_{state['iter']}")
        
        # --- 渲染中间：发光分数与终端流 ---
        score_placeholder.markdown(f"<div class='glowing-score'>{state['score']:.2f}</div>", unsafe_allow_html=True)
        
        logs_html = "<br/>".join(state["logs"])
        terminal_placeholder.markdown(f"<div class='matrix-terminal'>{logs_html}</div>", unsafe_allow_html=True)

        # --- 渲染右侧：动态线图与雷达图 ---
        # 1. 荧光绿分数攀升线
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            y=state["history_scores"], mode='lines',
            line=dict(color='#00FF41', width=3, shape='spline'),
            fill='tozeroy', fillcolor='rgba(0, 255, 65, 0.1)'
        ))
        fig_line.update_layout(
            margin=dict(l=0, r=0, t=20, b=20), height=180,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#333'), yaxis=dict(showgrid=True, gridcolor='#333', color='#777')
        )
        line_placeholder.plotly_chart(fig_line, width='stretch', config={'displayModeBar': False}, key=f"line_{state['iter']}")
        
        # 2. 美团黄雷达图
        categories = ['朝阳仓负载', '海淀仓负载', '冷链齐套率', '时效指标', '成本优化']
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=state["radar"],
            theta=categories,
            fill='toself',
            fillcolor='rgba(255, 208, 0, 0.3)',
            line=dict(color='#FFD000')
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor='#333', linecolor='#333', tickfont=dict(color='#777')),
                angularaxis=dict(gridcolor='#333', linecolor='#333', tickfont=dict(color='#FFF'))
            ),
            showlegend=False, margin=dict(l=30, r=30, t=30, b=30), height=240,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        radar_placeholder.plotly_chart(fig_radar, width='stretch', config={'displayModeBar': False}, key=f"radar_{state['iter']}")

        # --- 更新全局进度条 ---
        progress_bar.progress(state["progress"])

    progress_bar.empty()
    st.markdown("<div style='text-align:center; color: var(--neon-green); font-weight: bold; font-size: 20px;'>[ SUCCESS ] ALLOCATION STRATEGY COMPILED AND LOCKED.</div>", unsafe_allow_html=True)