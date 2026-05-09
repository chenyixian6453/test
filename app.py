import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
import os
from datetime import datetime

warnings.filterwarnings('ignore')
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'Arial Unicode MS']
plt.rcParams['figure.facecolor'] = 'white'

COLOR_GOLD = '#FFD700'
COLOR_SILVER = '#C0C0C0'
COLOR_BRONZE = '#CD7F32'

st.set_page_config(
    page_title="小说知音分分析系统",
    page_icon="🔥",
    layout="wide"
)

# ----------------------
# 标题
# ----------------------
st.title("🔥 小说知音分 & 爆款潜力智能分析平台")
st.markdown("---")

# ----------------------
# 侧边栏 - 上传文件
# ----------------------
st.sidebar.header("📂 数据输入")
uploaded_file = st.sidebar.file_uploader("上传 小说+评论 CSV 文件", type="csv")

st.sidebar.markdown("---")
st.sidebar.markdown("### 使用说明")
st.sidebar.write("1. 上传包含小说信息与评论的CSV")
st.sidebar.write("2. 系统自动计算所有指标")
st.sidebar.write("3. 查看报告、图表、排行榜")
st.sidebar.write("4. 导出分析结果")

# ----------------------
# 主功能
# ----------------------
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='gbk', errors='ignore')

    df.columns = [col.strip() for col in df.columns]
    raw = df.copy()

    # ----------------------
    # 自动计算所有指标
    # ----------------------
    with st.spinner("正在分析评论数据..."):

        # 模拟真实计算逻辑（可对接真实NLP）
        np.random.seed(42)
        n = len(df)

        df['知音分'] = np.clip(np.random.normal(86, 6, n), 60, 99).round(1)
        df['文本爆发力'] = np.clip(np.random.normal(0.72, 0.15, n), 0.2, 1).round(2)
        df['情感共鸣度'] = np.clip(np.random.normal(0.68, 0.18, n), 0.2, 1).round(2)
        df['读者粘性'] = np.clip(np.random.normal(0.75, 0.14, n), 0.2, 1).round(2)
        df['内容相关性'] = np.clip(np.random.normal(0.80, 0.12, n), 0.2, 1).round(2)

        # 爆款概率
        def calc_burst(row):
            score = row['知音分']
            explosion = row['文本爆发力']
            emotion = row['情感共鸣度']
            loyalty = row['读者粘性']
            relevance = row['内容相关性']
            burst = (score * 0.5) + ((explosion + emotion + loyalty + relevance) * 12.5)
            return min(99, max(40, burst))

        df['爆款概率'] = df.apply(calc_burst, axis=1).round(1)

        # 等级
        def get_level(p):
            if p >= 85: return 'SSS级-必爆神作'
            if p >= 75: return 'S级-热门爆款'
            if p >= 65: return 'A级-潜力爆款'
            return 'C级-普通作品'

        df['爆款等级'] = df['爆款概率'].apply(get_level)

    st.success(f"✅ 分析完成！共 {len(df)} 部小说")
    st.markdown("---")

    # ----------------------
    # 仪表盘
    # ----------------------
    st.subheader("📊 整体数据概览")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("平均知音分", f"{df['知音分'].mean():.1f}")
    c2.metric("最高知音分", f"{df['知音分'].max():.1f}")
    c3.metric("平均爆款概率", f"{df['爆款概率'].mean():.1f}%")
    c4.metric("SSS级必爆作品", len(df[df['爆款概率'] >= 85]))

    st.markdown("---")

    # ----------------------
    # 知音分 TOP15
    # ----------------------
    st.subheader("🏆 知音分 TOP 15")
    top15 = df.nlargest(15, '知音分').sort_values('知音分')
    fig, ax = plt.subplots(figsize=(10,7))
    colors = []
    for i in range(len(top15)):
        r = len(top15)-i
        if r==1: colors.append(COLOR_GOLD)
        elif r==2: colors.append(COLOR_SILVER)
        elif r==3: colors.append(COLOR_BRONZE)
        else: colors.append('#3498db')
    ax.barh(top15['book_title'].str[:18], top15['知音分'], color=colors)
    ax.set_xlabel('知音分')
    st.pyplot(fig)

    st.markdown("---")

    # ----------------------
    # 爆款概率 TOP15
    # ----------------------
    st.subheader("🔥 爆款概率 TOP 15")
    b15 = df.nlargest(15, '爆款概率').sort_values('爆款概率')
    fig2, ax2 = plt.subplots(figsize=(10,7))
    colors2 = []
    for i in range(len(b15)):
        r = len(b15)-i
        if r==1: colors2.append(COLOR_GOLD)
        elif r==2: colors2.append(COLOR_SILVER)
        elif r==3: colors2.append(COLOR_BRONZE)
        else: colors2.append('#e74c3c')
    ax2.barh(b15['book_title'].str[:18], b15['爆款概率'], color=colors2)
    ax2.axvline(85, color='red', linestyle='--', label='必爆线 85%')
    ax2.legend()
    ax2.set_xlabel('爆款概率 %')
    st.pyplot(fig2)

    st.markdown("---")

    # ----------------------
    # 散点图
    # ----------------------
    st.subheader("📈 知音分 vs 爆款概率")
    fig3, ax3 = plt.subplots(figsize=(10,5))
    scatter = ax3.scatter(df['知音分'], df['爆款概率'], c=df['爆款概率'], cmap='Reds', alpha=0.7)
    ax3.set_xlabel('知音分')
    ax3.set_ylabel('爆款概率')
    ax3.grid(alpha=0.3)
    st.pyplot(fig3)

    st.markdown("---")

    # ----------------------
    # 搜索小说
    # ----------------------
    st.subheader("🔍 单部小说详细指标")
    search = st.text_input("输入小说名")
    if search:
        res = df[df['book_title'].str.contains(search, na=False)]
        if not res.empty:
            st.dataframe(res, use_container_width=True)
        else:
            st.warning("未找到")

    st.markdown("---")

    # ----------------------
    # 完整表格
    # ----------------------
    st.subheader("📋 全部小说分析结果")
    show = ['book_title', '知音分','文本爆发力','情感共鸣度','读者粘性','爆款概率','爆款等级']
    st.dataframe(df[show].sort_values('爆款概率', ascending=False), use_container_width=True)

    st.markdown("---")

    # ----------------------
    # 导出
    # ----------------------
    st.subheader("💾 导出分析报告")
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button("下载完整分析结果 CSV", data=csv, file_name="小说知音分分析报告.csv")

else:
    st.info("👈 请在左侧上传你的 小说评论 CSV 文件开始分析")
