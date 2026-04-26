import streamlit as st

# --- ロジック部分 ---
def calculate_expressiveness(i_raw, t_raw):
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
        score_at_imin = calculate_expressiveness(i_min / 10.0, t_raw)
        score_at_imax = calculate_expressiveness(i_max / 10.0, t_raw)
        
        if not (score_at_imax < s_min or score_at_imin > s_max):
            bonus = total_t - base_t
            if bonus >= 0:
                possible_bonus.append(bonus)
            
    if not possible_bonus:
        return None
    return min(possible_bonus), max(possible_bonus)

# --- Streamlit UI部分 ---
st.set_page_config(page_title="Bonus Estimator", page_icon="🎯")

st.title("ジャストヒットボーナス推定")
st.write("みかけの数値から、あり得るボーナス値の範囲を逆算します。")

# サイドバーまたはメイン画面に入力欄を作成
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        disp_i = st.number_input("みかけの抑揚 (0-100)", min_value=0, max_value=100, value=99)
    with col2:
        disp_s = st.number_input("みかけの表現力 (0-100)", min_value=0, max_value=100, value=99)
    
    base_t = st.number_input("既知の基礎技法点 (0-1250)", min_value=0, max_value=1250, value=500)

st.divider()

if st.button("範囲を計算する", type="primary", use_container_width=True):
    result = solve_bonus_range(disp_i, disp_s, base_t)
    
    if result:
        b_min, b_max = result
        st.success("計算が完了しました！")
        
        # 大きな文字で表示
        if b_min == b_max:
            st.metric("推定ボーナス値", f"{b_min} 点", help="この値で確定です")
        else:
            st.subheader(f"推定範囲: {b_min} ～ {b_max} 点")
            st.info(f"ボーナス値は {b_min}点 から {b_max}点 の間のいずれかです。")
    else:
        st.error("条件を満たすボーナス値が見つかりませんでした。入力値を確認してください。")

st.caption("© 2026 Zawasow30 - Developed with Streamlit")