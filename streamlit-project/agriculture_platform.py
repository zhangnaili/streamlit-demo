# agriculture_platform.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="方寸云耕 - 智慧农业决策平台",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 模拟数据 - 在实际应用中替换为真实数据
@st.cache_data
def load_sample_data():
    """加载示例数据"""
    # 种植数据
    planting_data = pd.DataFrame({
        '种植地块': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'B1', 'B2', 'B3', 'B4'],
        '作物名称': ['小麦', '玉米', '玉米', '黄豆', '绿豆', '谷子', '小麦', '黑豆', '红豆', '绿豆'],
        '作物类型': ['粮食', '粮食', '粮食', '粮食（豆类）', '粮食（豆类）', '粮食', '粮食', '粮食（豆类）', '粮食（豆类）',
                     '粮食（豆类）'],
        '种植面积/亩': [80.0, 55.0, 35.0, 72.0, 68.0, 55.0, 60.0, 46.0, 40.0, 28.0],
        '种植季次': ['单季', '单季', '单季', '单季', '单季', '单季', '单季', '单季', '单季', '单季']
    })

    # 效益数据
    benefit_data = pd.DataFrame({
        '作物名称': ['小麦', '玉米', '黄豆', '绿豆', '黑豆', '红豆', '谷子', '西红柿', '黄瓜', '香菇'],
        '亩产量/斤': [600, 800, 400, 350, 500, 400, 450, 3000, 4000, 2000],
        '种植成本/(元/亩)': [500, 600, 400, 350, 400, 350, 400, 1200, 1500, 8000],
        '销售单价/(元/斤)': [1.5, 1.2, 3.0, 7.0, 7.5, 8.0, 2.0, 2.5, 2.0, 15.0],
        '地块类型': ['平旱地', '平旱地', '平旱地', '平旱地', '平旱地', '平旱地', '平旱地', '水浇地', '大棚', '大棚']
    })

    # 计算亩效益
    benefit_data['亩效益/元'] = benefit_data['亩产量/斤'] * benefit_data['销售单价/(元/斤)'] - benefit_data[
        '种植成本/(元/亩)']

    return planting_data, benefit_data


def create_dashboard(planting_data, benefit_data):
    """数据驾驶舱"""
    st.header("📊 农业数据驾驶舱")

    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    total_area = planting_data['种植面积/亩'].sum()
    crop_types = planting_data['作物类型'].nunique()
    crop_varieties = planting_data['作物名称'].nunique()

    with col1:
        st.metric("总种植面积", f"{total_area}亩")
    with col2:
        st.metric("作物种类", f"{crop_varieties}种")
    with col3:
        st.metric("地块数量", f"{len(planting_data)}个")
    with col4:
        avg_benefit = benefit_data['亩效益/元'].mean()
        st.metric("平均亩效益", f"¥{avg_benefit:.0f}")

    # 种植结构分析
    st.subheader("种植结构分析")
    col1, col2 = st.columns(2)

    with col1:
        # 作物类型分布
        type_dist = planting_data.groupby('作物类型')['种植面积/亩'].sum().reset_index()
        fig_pie = px.pie(type_dist, values='种植面积/亩', names='作物类型',
                         title="作物类型面积分布", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # 主要作物面积
        crop_dist = planting_data.groupby('作物名称')['种植面积/亩'].sum().nlargest(10).reset_index()
        fig_bar = px.bar(crop_dist, x='作物名称', y='种植面积/亩',
                         title="主要作物种植面积", color='种植面积/亩')
        st.plotly_chart(fig_bar, use_container_width=True)

    # 效益分析
    st.subheader("经济效益分析")
    col1, col2 = st.columns(2)

    with col1:
        # 亩效益排名
        top_crops = benefit_data.nlargest(10, '亩效益/元')
        fig_benefit = px.bar(top_crops, x='作物名称', y='亩效益/元',
                             title="作物亩效益排名", color='亩效益/元')
        st.plotly_chart(fig_benefit, use_container_width=True)

    with col2:
        # 成本收益分析
        fig_scatter = px.scatter(benefit_data, x='种植成本/(元/亩)', y='亩效益/元',
                                 size='亩产量/斤', color='作物名称',
                                 title="成本-收益分析", hover_data=['销售单价/(元/斤)'])
        st.plotly_chart(fig_scatter, use_container_width=True)


def create_planner(planting_data, benefit_data):
    """智能规划器"""
    st.header("🧮 智能种植规划器")

    # 参数配置
    with st.sidebar:
        st.subheader("优化参数配置")

        years = st.slider("规划年限", 1, 7, 3)
        risk_level = st.select_slider(
            "风险偏好",
            options=["极度保守", "保守", "稳健", "积极", "极度积极"],
            value="稳健"
        )

        st.subheader("优化目标权重")
        economic_weight = st.slider("经济效益", 0.0, 1.0, 0.6)
        stability_weight = st.slider("稳定性", 0.0, 1.0, 0.3)
        sustainability_weight = st.slider("可持续性", 0.0, 1.0, 0.1)

        st.subheader("约束条件")
        min_bean_rotation = st.checkbox("强制豆类轮作", True)
        avoid_same_crop = st.checkbox("避免重茬种植", True)
        min_plot_size = st.slider("最小地块种植面积", 1.0, 20.0, 5.0)

    # 方案生成
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("智能规划")

        if st.button("🚀 生成优化方案", type="primary", use_container_width=True):
            with st.spinner("正在计算最优种植方案..."):
                # 模拟计算过程
                import time
                time.sleep(2)

                # 显示优化结果
                display_optimization_result(planting_data, benefit_data)

    with col2:
        st.subheader("快速建议")
        st.info("💡 **即时优化建议**")

        # 基于数据的简单建议
        high_value_crops = benefit_data.nlargest(3, '亩效益/元')['作物名称'].tolist()
        st.write(f"推荐高价值作物: {', '.join(high_value_crops)}")

        underutilized = planting_data.groupby('作物名称')['种植面积/亩'].sum().nsmallest(2)
        st.write(f"考虑扩大: {', '.join(underutilized.index.tolist())}")


def display_optimization_result(planting_data, benefit_data):
    """显示优化结果"""
    st.success("✅ 优化方案生成成功！预计整体收益提升 28.7%")

    # 生成模拟优化结果
    np.random.seed(42)
    plots = planting_data['种植地块'].unique()

    result_data = []
    for plot in plots[:15]:  # 显示前15个地块
        current_crop = planting_data[planting_data['种植地块'] == plot]['作物名称'].iloc[0] if plot in planting_data[
            '种植地块'].values else "未知"
        recommended_crop = np.random.choice(benefit_data['作物名称'].values)
        current_benefit = benefit_data[benefit_data['作物名称'] == current_crop]['亩效益/元'].values[
            0] if current_crop in benefit_data['作物名称'].values else 0
        new_benefit = benefit_data[benefit_data['作物名称'] == recommended_crop]['亩效益/元'].values[0]
        improvement = ((new_benefit - current_benefit) / current_benefit * 100) if current_benefit > 0 else 100

        result_data.append({
            '地块': plot,
            '当前作物': current_crop,
            '推荐作物': recommended_crop,
            '当前效益/元': current_benefit,
            '预期效益/元': new_benefit,
            '提升幅度/%': improvement
        })

    result_df = pd.DataFrame(result_data)

    # 显示结果表格
    st.dataframe(result_df.style.format({
        '当前效益/元': '{:.0f}',
        '预期效益/元': '{:.0f}',
        '提升幅度/%': '{:.1f}%'
    }), use_container_width=True)

    # 可视化结果
    col1, col2 = st.columns(2)

    with col1:
        # 收益提升可视化
        fig_improvement = px.bar(result_df.nlargest(10, '提升幅度/%'),
                                 x='地块', y='提升幅度/%',
                                 title="各地块预期收益提升幅度",
                                 color='提升幅度/%',
                                 color_continuous_scale='viridis')
        st.plotly_chart(fig_improvement, use_container_width=True)

    with col2:
        # 作物变更分布
        crop_changes = result_df.groupby('推荐作物').size().reset_index(name='推荐次数')
        fig_changes = px.pie(crop_changes, values='推荐次数', names='推荐作物',
                             title="推荐作物分布")
        st.plotly_chart(fig_changes, use_container_width=True)

    # 方案对比
    st.subheader("📈 方案对比分析")
    comparison_data = {
        '指标': ['总经济效益', '资源利用率', '风险水平', '劳动力需求', '可持续性'],
        '当前方案': [65, 70, 45, 80, 60],
        '优化方案': [85, 88, 65, 75, 82],
        '改善': ['+30.8%', '+25.7%', '+44.4%', '-6.2%', '+36.7%']
    }

    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)


def create_risk_simulator(benefit_data):
    """风险模拟器"""
    st.header("⚠️ 风险模拟分析")

    tab1, tab2, tab3 = st.tabs(["💰 价格波动", "🌦️ 气候影响", "📜 政策变化"])

    with tab1:
        st.subheader("市场价格波动模拟")

        col1, col2 = st.columns(2)
        with col1:
            selected_crop = st.selectbox("选择作物", benefit_data['作物名称'].unique())
            price_change = st.slider("价格变化幅度", -50, 50, 0, format="%d%%")

        with col2:
            yield_change = st.slider("产量变化幅度", -30, 30, 0, format="%d%%")
            cost_change = st.slider("成本变化幅度", -20, 20, 0, format="%d%%")

        # 模拟影响
        crop_data = benefit_data[benefit_data['作物名称'] == selected_crop].iloc[0]
        original_profit = crop_data['亩效益/元']

        new_price = crop_data['销售单价/(元/斤)'] * (1 + price_change / 100)
        new_yield = crop_data['亩产量/斤'] * (1 + yield_change / 100)
        new_cost = crop_data['种植成本/(元/亩)'] * (1 + cost_change / 100)

        new_profit = new_yield * new_price - new_cost
        profit_change = (new_profit - original_profit) / original_profit * 100

        # 显示结果
        col1, col2 = st.columns(2)
        with col1:
            st.metric("原亩效益", f"¥{original_profit:.0f}")
        with col2:
            st.metric("新亩效益", f"¥{new_profit:.0f}", f"{profit_change:+.1f}%")

        # 敏感性分析
        st.subheader("价格敏感性分析")
        price_range = np.linspace(-40, 40, 9)  # -40% 到 +40%
        profit_changes = []

        for change in price_range:
            temp_profit = new_yield * (crop_data['销售单价/(元/斤)'] * (1 + change / 100)) - new_cost
            profit_changes.append(temp_profit)

        fig_sensitivity = px.line(x=price_range, y=profit_changes,
                                  labels={'x': '价格变化幅度 (%)', 'y': '亩效益 (元)'},
                                  title=f"{selected_crop}价格敏感性分析")
        fig_sensitivity.add_hline(y=original_profit, line_dash="dash", line_color="red",
                                  annotation_text="原效益")
        st.plotly_chart(fig_sensitivity, use_container_width=True)

    with tab2:
        st.subheader("气候情景模拟")

        scenario = st.selectbox(
            "选择气候情景",
            ["正常年份", "轻度干旱", "严重干旱", "洪涝灾害", "低温冻害", "高温热害"]
        )

        # 模拟不同情景的影响
        scenarios_data = {
            '情景': ['正常年份', '轻度干旱', '严重干旱', '洪涝灾害', '低温冻害', '高温热害'],
            '产量影响': [0, -15, -40, -25, -20, -10],
            '成本影响': [0, 10, 25, 30, 15, 5],
            '发生概率': [60, 20, 5, 8, 4, 3]
        }

        scenarios_df = pd.DataFrame(scenarios_data)
        selected_scenario = scenarios_df[scenarios_df['情景'] == scenario].iloc[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("产量影响", f"{selected_scenario['产量影响']}%")
        with col2:
            st.metric("成本影响", f"+{selected_scenario['成本影响']}%")
        with col3:
            st.metric("发生概率", f"{selected_scenario['发生概率']}%")

        # 显示所有情景
        st.dataframe(scenarios_df, use_container_width=True)

    with tab3:
        st.subheader("政策变化模拟")
        st.info("政策变化对农业种植结构的影响分析")

        policy_options = st.multiselect(
            "选择政策变化",
            ["粮食补贴增加", "生态补偿机制", "农业保险推广", "水资源管理加强", "碳排放要求"],
            default=["粮食补贴增加"]
        )

        if policy_options:
            st.success("已选择政策变化分析")
            # 这里可以添加具体的政策影响分析逻辑


def create_benefit_analysis(benefit_data, planting_data):
    """效益分析"""
    st.header("💵 经济效益深度分析")

    # 总体效益概览
    col1, col2, col3 = st.columns(3)

    total_potential = benefit_data['亩效益/元'].sum()
    avg_efficiency = benefit_data['亩效益/元'].mean()
    max_benefit_crop = benefit_data.loc[benefit_data['亩效益/元'].idxmax(), '作物名称']

    with col1:
        st.metric("总效益潜力", f"¥{total_potential:.0f}")
    with col2:
        st.metric("平均亩效益", f"¥{avg_efficiency:.0f}")
    with col3:
        st.metric("效益最高作物", max_benefit_crop)

    # 效益分布分析
    st.subheader("效益分布分析")
    col1, col2 = st.columns(2)

    with col1:
        # 效益分布直方图
        fig_hist = px.histogram(benefit_data, x='亩效益/元',
                                title="亩效益分布", nbins=20)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        # 地块类型效益对比
        fig_box = px.box(benefit_data, x='地块类型', y='亩效益/元',
                         title="不同地块类型效益对比")
        st.plotly_chart(fig_box, use_container_width=True)

    # 投入产出分析
    st.subheader("投入产出效率分析")

    benefit_data['投入产出比'] = benefit_data['亩效益/元'] / benefit_data['种植成本/(元/亩)']
    efficient_crops = benefit_data.nlargest(10, '投入产出比')

    fig_efficiency = px.bar(efficient_crops, x='作物名称', y='投入产出比',
                            title="作物投入产出比排名", color='投入产出比')
    st.plotly_chart(fig_efficiency, use_container_width=True)

    # 详细数据表
    st.subheader("详细效益数据")
    display_data = benefit_data[['作物名称', '地块类型', '亩产量/斤', '种植成本/(元/亩)',
                                 '销售单价/(元/斤)', '亩效益/元', '投入产出比']].copy()
    display_data = display_data.round({'亩效益/元': 0, '投入产出比': 2})

    st.dataframe(display_data, use_container_width=True)


def create_about_page():
    """关于项目页面"""
    st.header("🌾 关于方寸云耕")

    st.markdown("""
    ### 项目背景

    **方寸云耕**是一个基于数据驱动的智慧农业决策平台，旨在通过先进的数学建模和优化算法，
    为山区农业提供科学的种植决策支持，助力乡村振兴战略实施。

    ### 核心功能

    - 📊 **数据驾驶舱**: 全方位可视化农业数据，洞察种植结构与效益分布
    - 🧮 **智能规划器**: 基于多目标优化的种植方案推荐，平衡经济、风险与可持续性
    - ⚠️ **风险模拟器**: 模拟价格、气候、政策等多重风险，提供应对策略
    - 💵 **效益分析**: 深度分析经济效益，识别优化机会

    ### 技术特色

    - 🔬 **多目标优化算法**: 综合考虑经济效益、资源利用、风险控制等多重目标
    - 📈 **不确定性建模**: 处理市场价格、气候变化等不确定因素
    - 🎯 **个性化配置**: 支持不同风险偏好和约束条件的灵活配置
    - 🌐 **交互式可视化**: 直观展示分析结果和优化方案

    ### 应用价值

    本平台可为农业决策者提供：
    - 科学的数据支撑和决策依据
    - 风险预警和应对方案
    - 经济效益优化建议
    - 长期可持续发展规划

    ### 开发团队

    本项目由李思凡开发，融合了运筹优化、数据分析和农业科学的跨学科专业知识。
    """)

    st.info("💡 提示: 这是一个演示原型，实际应用需要接入真实数据和更复杂的算法模型")


def main():
    """主应用"""
    # 加载数据
    planting_data, benefit_data = load_sample_data()

    # 侧边栏导航
    st.sidebar.title("🌾 方寸云耕")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "导航菜单",
        ["数据驾驶舱", "智能规划器", "风险模拟器", "效益分析", "关于项目"],
        index=0
    )

    # 在侧边栏添加一些实用信息
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **平台状态**: 运行中  
    **数据更新**: 2024年  
    **版本**: v1.0 演示版
    """)

    # 页面路由
    if page == "数据驾驶舱":
        create_dashboard(planting_data, benefit_data)
    elif page == "智能规划器":
        create_planner(planting_data, benefit_data)
    elif page == "风险模拟器":
        create_risk_simulator(benefit_data)
    elif page == "效益分析":
        create_benefit_analysis(benefit_data, planting_data)
    else:
        create_about_page()


if __name__ == "__main__":
    main()