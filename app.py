import streamlit as st

# --- ロジック部分 ---
def calculate_expressiveness(i_raw, t_raw):
    # 内部計算（0-100スケール）
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
    i_min, i_max = disp_i * 10.0, (disp_i + 1) * 10.0 - 0.0001
    s_min, s_max = disp_s * 1000, (disp_s + 1) * 1000 - 1
    possible_bonus = []
    
    for total_t in range(0, 1251):
        t_raw = total_t / 12.5
        score_imin = calculate_expressiveness(i_min / 10.0, t_raw)
        score_imax = calculate_expressiveness(i_max / 10.0, t_raw)
        
        if not (score_imax < s_min or score_imin > s_max):
            bonus = total_t - base_t
            if bonus >= 0:
                possible_bonus.append(bonus)
    return possible_bonus

# --- Streamlit UI ---
st.set_page_config(page_title="JH Bonus Analyzer", page_icon="🎯")

st.title("💥 ジャストヒットボーナス解析")

# モード選択（みかけ推定をデフォルトに）
mode = st.radio(
    "解析に使用するデータの精度を選択してください",
    ("【予測】みかけの数値から推定する", "【正確】実数値から特定する"),
    horizontal=True
)

st.divider()

# 各モード共通の入力順序: 抑揚 -> 表現力 -> 技法点
if mode == "【予測】みかけの数値から推定する":
    st.subheader("🔍 みかけ数値推定モード")
    st.write("リザルト画面の整数値（0-100）を入力してください。")
    
    col1, col2 = st.columns(2)
    with col1:
        disp_i = st.number_input("みかけの抑揚 (0-100)", 0, 100, 99)
    with col2:
        disp_s = st.number_input("みかけの表現力 (0-100)", 0, 100, 99)
    
    base_t_est = st.number_input("基礎技法点 (0-1250)", 0, 1250, 800)

    if st.button("あり得る範囲を計算", type="primary", use_container_width=True):
        bonus_list = solve_bonus_range(disp_i, disp_s, base_t_est)
        if bonus_list:
            b_min, b_max = min(bonus_list), max(bonus_list)
            st.success("計算完了")
            if b_min == b_max:
                st.metric("確定ボーナス値", f"{b_min} 点")
            else:
                st.subheader(f"推定範囲: {b_min} ～ {b_max} 点")
        else:
            st.error("条件に合うボーナス値が見つかりませんでした。入力値を確認してください。")

else:
    st.subheader("📋 詳細リザルト解析モード")
    st.write("内部ログ等の正確な数値を入力してください。")
    
    col1, col2 = st.columns(2)
    with col1:
        real_i = st.number_input("実際の抑揚 (0-1000)", 0, 1000, 990)
    with col2:
        real_s = st.number_input("実際の表現力 (0-100000)", 0, 100000, 99750)
    
    base_t = st.number_input("基礎技法点 (0-1250)", 0, 1250, 800)

    if st.button("ボーナスを特定する", type="primary", use_container_width=True):
        best_t, min_diff = 0, float('inf')
        for t_int in range(0, 1251):
            score = calculate_expressiveness(real_i / 10.0, t_int / 12.5)
            diff = abs(score - real_s)
            if diff < min_diff:
                min_diff, best_t = diff, t_int
        
        bonus = best_t - base_t
        if bonus < 0:
            st.error(f"矛盾を検知しました。基礎点({base_t})が算出合計値({best_t})を上回っています。")
        else:
            st.success("解析完了")
            st.metric("ジャストヒットボーナス", f"{bonus} 点")
            st.caption(f"（内部合計技法点: {best_t}）")

st.divider()
st.caption("© 2026 Zawasow_lab")