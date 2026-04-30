import streamlit as st

# --- ロジック部分 ---
def calculate_expressiveness_score(intonation_raw, technique_raw):
    """
    抑揚と技法点の実数値から表現力スコアを算出する。
    """
    # 内部計算用の軸定義（0-100スケール）
    intonation_axis = [0.0, 45.0, 70.0, 80.0, 90.0, 100.0]
    technique_axis = [0.0, 40.0, 60.0, 80.0, 90.0, 100.0]
    
    # 表現力スコアの格子データ
    score_grid = [
        [0, 30000, 40000, 50000, 53000, 55000],
        [30000, 50000, 65000, 78000, 82000, 83500],
        [50000, 63000, 75000, 86000, 88500, 92000],
        [56000, 66000, 80000, 89000, 92500, 95000],
        [60000, 68000, 82000, 93100, 95000, 97500],
        [63000, 70000, 84000, 95000, 98000, 100000]
    ]
    
    def find_axis_index(value, axis):
        if value >= 100.0: 
            return len(axis) - 2
        for i in range(len(axis) - 1):
            if axis[i] <= value < axis[i+1]: 
                return i
        return len(axis) - 2

    # 各軸のインデックスを取得
    idx_i = find_axis_index(intonation_raw, intonation_axis)
    idx_t = find_axis_index(technique_raw, technique_axis)

    # 境界値の間における位置割合を計算
    intonation_ratio = (intonation_raw - intonation_axis[idx_i]) / (intonation_axis[idx_i+1] - intonation_axis[idx_i])
    technique_ratio = (technique_raw - technique_axis[idx_t]) / (technique_axis[idx_t+1] - technique_axis[idx_t])

    # 周囲4点のスコアを取得
    score_q11 = score_grid[idx_i][idx_t]
    score_q12 = score_grid[idx_i][idx_t+1]
    score_q21 = score_grid[idx_i+1][idx_t]
    score_q22 = score_grid[idx_i+1][idx_t+1]

    # 二線形補間による最終スコアの算出
    final_score = (
        (1 - intonation_ratio) * (1 - technique_ratio) * score_q11 +
        intonation_ratio * (1 - technique_ratio) * score_q21 +
        (1 - intonation_ratio) * technique_ratio * score_q12 +
        intonation_ratio * technique_ratio * score_q22
    )
    return final_score

def solve_possible_bonus_range(display_intonation, display_expressiveness, base_technique_points):
    """
    画面表示値からあり得るジャストヒットボーナスの範囲を特定する。
    """
    # 画面上の整数値から内部的な実数値の範囲（最小・最大）を定義[cite: 2]
    # 抑揚は0-1000、表現力は0-100000スケールを想定
    intonation_min = display_intonation * 10
    intonation_max = min(display_intonation * 10 + 9, 1000)
    
    expressiveness_min = display_expressiveness * 1000
    expressiveness_max = min(display_expressiveness * 1000 + 999, 100000)
    
    possible_bonuses = []
    
    # 合計技法点(total_technique)を全探索して条件に合うものを探す[cite: 2]
    for total_technique in range(0, 1251):
        technique_raw_scale = total_technique / 12.5
        
        # 指摘に基づいた境界条件チェック:
        # 同じ技法点なら、抑揚が大きいほど表現力は低くなり、抑揚が小さいほど表現力は高くなる傾向を利用[cite: 2]
        
        # 1. 最も表現力が出にくい条件（抑揚が最大）でのスコア
        potential_score_min = calculate_expressiveness_score(intonation_max / 10.0, technique_raw_scale)
        
        # 2. 最も表現力が出やすい条件（抑揚が最小）でのスコア
        potential_score_max = calculate_expressiveness_score(intonation_min / 10.0, technique_raw_scale)
        
        # 判定: 技法点由来のスコア範囲が、表示値の範囲と重なっているか[cite: 2]
        is_score_within_range = not (potential_score_max < expressiveness_min or potential_score_min > expressiveness_max)
        
        if is_score_within_range:
            current_bonus = total_technique - base_technique_points
            if current_bonus >= 0:
                possible_bonuses.append(current_bonus)
                
    return possible_bonuses

# --- Streamlit UI ---
st.set_page_config(page_title="JH Bonus Analyzer", page_icon="🎯")

st.title("💥 ジャストヒットボーナス解析")

analysis_mode = st.radio(
    "解析に使用するデータの精度を選択してください",
    ("【予測】みかけの数値から推定する", "【正確】実数値から特定する"),
    horizontal=True
)

st.divider()

if analysis_mode == "【予測】みかけの数値から推定する":
    st.subheader("🔍 みかけ数値推定モード")
    st.write("リザルト画面の整数値（0-100）を入力してください。")
    
    col_intonation, col_expressiveness = st.columns(2)
    with col_intonation:
        input_disp_i = st.number_input("みかけの抑揚 (0-100)", 0, 100, 99)
    with col_expressiveness:
        input_disp_s = st.number_input("みかけの表現力 (0-100)", 0, 100, 99)
    
    input_base_t = st.number_input("基礎技法点 (0-1250)", 0, 1250, 800)

    if st.button("あり得る範囲を計算", type="primary", use_container_width=True):
        bonus_results = solve_possible_bonus_range(input_disp_i, input_disp_s, input_base_t)
        
        if bonus_results:
            min_bonus, max_bonus = min(bonus_results), max(bonus_results)
            st.success("計算完了")
            if min_bonus == max_bonus:
                st.metric("確定ボーナス値", f"{min_bonus} 点")
            else:
                st.subheader(f"推定範囲: {min_bonus} ～ {max_bonus} 点")
        else:
            st.error("条件に合うボーナス値が見つかりませんでした。入力値を確認してください。")

else:
    st.subheader("📋 詳細リザルト解析モード")
    st.write("内部ログ等の正確な数値を入力してください。")
    
    col_real_i, col_real_s = st.columns(2)
    with col_real_i:
        input_real_i = st.number_input("実際の抑揚 (0-1000)", 0, 1000, 990)
    with col_real_s:
        input_real_s = st.number_input("実際の表現力 (0-100000)", 0, 100000, 99750)
    
    input_base_t_precise = st.number_input("基礎技法点 (0-1250)", 0, 1250, 800)

    if st.button("ボーナスを特定する", type="primary", use_container_width=True):
        best_technique_total, minimum_difference = 0, float('inf')
        
        for trial_technique in range(0, 1251):
            calculated_score = calculate_expressiveness_score(input_real_i / 10.0, trial_technique / 12.5)
            difference = abs(calculated_score - input_real_s)
            
            if difference < minimum_difference:
                minimum_difference = difference
                best_technique_total = trial_technique
        
        calculated_bonus = best_technique_total - input_base_t_precise
        if calculated_bonus < 0:
            st.error(f"矛盾を検知しました。基礎点({input_base_t_precise})が算出合計値({best_technique_total})を上回っています。")
        else:
            st.success("解析完了")
            st.metric("ジャストヒットボーナス", f"{calculated_bonus} 点")
            st.caption(f"（内部合計技法点: {best_technique_total}）")

st.divider()
st.caption("© 2026 Zawasow_lab")