import streamlit as st
import pandas as pd
import random

# 初期化
if "board_size" not in st.session_state:
    st.session_state.board_size = 9
    st.session_state.player_positions = {1: {"x": 0, "y": 0}, 2: {"x": 8, "y": 8}}
    st.session_state.stones = []
    st.session_state.skill_tiles = []  # {"x": 3, "y": 4, "type": "heal"}
    st.session_state.current_player = 1
    st.session_state.dice_value = "-"
    st.session_state.next_dice_values = {1: 3, 2: 2}
    st.session_state.player_points = {1: 50, 2: 50}
    st.session_state.phase = "roll"

# タイトルとプレイヤー情報
st.title("2人対戦ストラテジーゲーム")
st.subheader(f"プレイヤー {st.session_state.current_player} のターン")
st.write(f"現在のサイコロの目: {st.session_state.dice_value}")
st.write(f"次のサイコロの目: {st.session_state.next_dice_values}")
st.write(f"プレイヤーのポイント: {st.session_state.player_points}")

# ボード描画
def render_board():
    # ── ❶ セルの一辺をサイドバーで可変に ──
    cell_size = st.sidebar.slider("セルの大きさ (px)", 40, 120, 70, 5)

    size = st.session_state.board_size

    html = f"""
    <style>
    .grid-container {{
        display: grid;
        grid-template-columns: repeat({size}, {cell_size}px);
        grid-template-rows: repeat({size}, {cell_size}px);
        gap: 1px;
    }}
    .grid-item {{
        width: {cell_size}px;
        height: {cell_size}px;
        text-align: center;
        line-height: {cell_size}px;
        border: 1px solid #ccc;
        font-size: {int(cell_size*0.45)}px;  /* フォントも拡大比率で */
        background-color: white;
        user-select: none;
    }}
    .stone  {{ background-color: #888; color: white; }}
    .skill  {{ background-color: #0af; color: white; }}
    .player1{{ background-color: #3af; color: white; }}
    .player2{{ background-color: #f33; color: white; }}
    </style>
    <div class="grid-container">
    """

    # 盤面ループ
    for y in range(size):
        for x in range(size):
            cls, content = "grid-item", ""
            if (x, y) == (st.session_state.player_positions[1]["x"],
                          st.session_state.player_positions[1]["y"]):
                cls += " player1"; content = "P1"
            elif (x, y) == (st.session_state.player_positions[2]["x"],
                            st.session_state.player_positions[2]["y"]):
                cls += " player2"; content = "P2"
            elif (x, y) in st.session_state.stones:
                cls += " stone";   content = "🪨"
            else:
                for tile in st.session_state.skill_tiles:
                    if tile["x"] == x and tile["y"] == y:
                        cls += " skill"; content = "🌀"
            html += f'<div class="{cls}">{content}</div>'

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)



render_board()

# サイコロフェーズ
if st.session_state.phase == "roll":
    if st.button("🎲 サイコロを振る"):
        dice = random.randint(1, 3)
        st.session_state.dice_value = dice
        st.session_state.phase = "move"
        st.rerun()

# 移動フェーズ
elif st.session_state.phase == "move":
    current = st.session_state.current_player
    pos = st.session_state.player_positions[current]
    x, y = pos["x"], pos["y"]
    dice = st.session_state.dice_value

    directions = {
        "↑ 上": (0, -1),
        "↓ 下": (0, 1),
        "← 左": (-1, 0),
        "→ 右": (1, 0)
    }

    st.write(f"{dice}マス移動可能。方向を選んでください：")

    for name, (dx, dy) in directions.items():
        blocked = False
        new_x, new_y = x, y
        for step in range(1, dice + 1):
            tx, ty = x + dx * step, y + dy * step
            if not (0 <= tx < st.session_state.board_size and 0 <= ty < st.session_state.board_size):
                blocked = True
                break
            if (tx, ty) in st.session_state.stones or (tx, ty) == (
                st.session_state.player_positions[3 - current]["x"],
                st.session_state.player_positions[3 - current]["y"]
            ):
                blocked = True
                new_x, new_y = x + dx * (step - 1), y + dy * (step - 1)
                break
            new_x, new_y = tx, ty

        if not blocked or (new_x != x or new_y != y):
            if st.button(f"{name} に移動"):
                if not (0 <= new_x < st.session_state.board_size and 0 <= new_y < st.session_state.board_size):
                    st.success(f"プレイヤー {current} は崖から落ちた！プレイヤー {3 - current} の勝利！")
                    st.stop()

                st.session_state.player_positions[current] = {"x": new_x, "y": new_y}
                st.session_state.phase = "place"
                st.session_state.dice_value = "-"
                st.rerun()

# 配置フェーズ（石 or スキル）
elif st.session_state.phase == "place":
    st.write("石またはスキルマスを配置してください：")
    current = st.session_state.current_player
    x = st.session_state.player_positions[current]["x"]
    y = st.session_state.player_positions[current]["y"]

    directions = {
        "↑": (x, y - 1),
        "↓": (x, y + 1),
        "←": (x - 1, y),
        "→": (x + 1, y)
    }

    for name, (tx, ty) in directions.items():
        if not (0 <= tx < st.session_state.board_size and 0 <= ty < st.session_state.board_size):
            continue

        cell_is_stone = (tx, ty) in st.session_state.stones
        cell_has_player = (tx, ty) == (st.session_state.player_positions[1]["x"], st.session_state.player_positions[1]["y"]) or (tx, ty) == (st.session_state.player_positions[2]["x"], st.session_state.player_positions[2]["y"])

        if not cell_has_player:
            # スキルマス設置（ポイント消費）
            if not cell_is_stone:
                if st.button(f"{name} にスキルマス設置（10pt）"):
                    if st.session_state.player_points[current] >= 10:
                        st.session_state.skill_tiles.append({"x": tx, "y": ty, "type": "heal"})  # 今は"heal"で固定
                        st.session_state.player_points[current] -= 10
                        st.session_state.phase = "roll"
                        st.session_state.current_player = 3 - current
                        st.rerun()
            # 石設置（スキルマスを上書き可能）
            if st.button(f"{name} に石を置く"):
                # スキルマスがあれば除去
                st.session_state.skill_tiles = [tile for tile in st.session_state.skill_tiles if not (tile["x"] == tx and tile["y"] == ty)]
                st.session_state.stones.append((tx, ty))
                st.session_state.phase = "roll"
                st.session_state.current_player = 3 - current
                st.rerun()
