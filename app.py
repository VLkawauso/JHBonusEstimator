import streamlit as st

# --- ロジック部分 ---
def calculate_expressiveness(i_raw, t_raw):
    # 内部計算用（0-100スケール）
    i_axis = [0.0, 45.0, 70.0, 80.0, 90.0, 100.0]
    t_axis = [0.0, 40.0, 60.0, 80.0, 90.0, 100.0]
    grid = [
        [0, 30000, 40000, 50000, 53000, 55000],
        [30000, 50000, 65000, 78000, 82000, 83500],
        [50000, 63000, 75000, 86000, 88500, 92000],
        [56000, 66000, 80000, 89000, 92500, 95000],
        [60000, 68000, 82000, 93100, 95000, 97500],
        [63000, 70000, 84000, 95000, 98000, 100000]
    ]
    
    def get_index(val, axis):
        if val >= 100.0: return len(axis) - 2
        for i in range(len(axis) - 1):
            if axis[i] <= val < axis[i+1]: return i
        return len(axis) - 2

    idx_i = get_index(i_raw, i_axis)
    idx_t = get_index(t_raw, t_axis)

    it_ratio = (i_raw - i_axis[idx_i]) / (i_axis[idx_i+1] - i_axis[idx_i])
    te_ratio = (t_raw - t_axis[idx_t]) / (t_axis[idx_t+1] - t_axis[idx_t])

    q11, q12 = grid[idx_i][idx_t], grid[idx_i][idx_t+1]
    q21, q22 = grid[idx_i+1][idx_t], grid[idx_i+1][idx_t+1]

    res = (1-it_ratio)*(1-te_ratio)*q11 + it_ratio*(1-te_ratio)*q21 + \
          (1-it_ratio)*te_ratio*q12 + it_ratio*te_ratio*q22
    return res

def solve_bonus_range(disp_i, disp_s, base_t):
    # みかけの数値（整数）から範囲を定義
    i_min, i_max = disp_i * 10.0, (disp_i + 1) * 10.0 - 0.0001
    s_min, s_max = disp_s * 1000, (disp_s + 1) * 1000 - 1
    possible_bonus = []
    
    for total_t in range(0, 1251):
        t_raw = total_t / 12.5
        score_at_imin = calculate_expressiveness(i_min / 10.0, t_raw)
        score_at_imax = calculate_expressiveness(i_max / 10.0, t_raw)
        
        if not (score_at_imax < s_min or score_at_imin > s_max):
            bonus = total_t - base_t
            if bonus >= 0:
                possible_bonus.append(bonus)
    return possible_bonus

# --- Streamlit UI ---
st.set_page_config(page_title="Expressiveness Solver", page_icon="📊")

st.title("表現力解析ツール")

# モード切り替え
mode = st.radio(
    "計算モードを選択してください",
    ("ボーナス範囲の逆算（みかけの数値から）", "表現力の直接計算（正確な数値から）"),
    horizontal=True
)

st.divider()

if mode == "ボーナス範囲の逆算（みかけの数値から）":
    st.subheader("ジャストヒットボーナス推定")
    col1, col2 = st.columns(2)
    with col1:
        disp_i = st.number_input("みかけの抑揚 (0-100)", 0, 100, 99, key="di")
    with col2:
        disp_s = st.number_input("みかけの表現力 (0-100)", 0, 100, 99, key="ds")
    
    base_t = st.number_input("基礎技法点 (0-1250)", 0, 1250, 500, key="bt")

    if st.button("範囲を計算", type="primary", use_container_width=True):
        bonus_list = solve_bonus_range(disp_i, disp_s, base_t)
        if bonus_list:
            b_min, b_max = min(bonus_list), max(bonus_list)
            st.success(f"推定結果: {b_min} ～ {b_max} 点")
            if b_min == b_max:
                st.info(f"ボーナス値は {b_min}点で確定です。")
        else:
            st.error("矛盾検知: 条件に合うボーナス値が存在しません。")

else:
    st.subheader("表現力の直接計算")
    col1, col2 = st.columns(2)
    with col1:
        real_i = st.number_input("実際の抑揚 (0-1000)", 0.0, 1000.0, 800.0, step=1.0) / 10.0
    with col2:
        # 技法点(1250点満点)を入力してもらい、内部で0-100に変換
        real_t_val = st.number_input("実際の技法点 (0-1250)", 0.0, 1250.0, 625.0, step=1.0)
        real_t = real_t_val / 12.5

    if st.button("表現力を計算", type="primary", use_container_width=True):
        score = calculate_expressiveness(real_i, real_t)
        rounded_score = int(round(score))
        st.metric("算出された表現力 (100000点満点)", f"{rounded_score} 点")
        st.write(f"みかけの表現力表示: **{rounded_score // 1000}**")

st.divider()
st.caption("© 2026 Zawasow_lab")