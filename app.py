import streamlit as st
import json
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# ページ設定
st.set_page_config(page_title="性格診断エンジン", page_icon="🔮", layout="centered")

HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(profile, scores):
    history = load_history()
    new_entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "profile": profile,
        "scores": scores
    }
    history.append(new_entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# カスタムCSSの読み込み
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# セッション状態の初期化
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'scores' not in st.session_state:
    st.session_state.scores = {"Logic": 0, "Empathy": 0, "Daring": 0, "Prudence": 0}
if 'result_saved' not in st.session_state:
    st.session_state.result_saved = False
if 'questions' not in st.session_state:
    with open('questions.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
        random.shuffle(questions)
        st.session_state.questions = questions

def reset_quiz():
    st.session_state.current_index = 0
    st.session_state.scores = {"Logic": 0, "Empathy": 0, "Daring": 0, "Prudence": 0}
    st.session_state.result_saved = False
    random.shuffle(st.session_state.questions)
    st.session_state.quiz_started = True

# --- サイドバー (履歴表示) ---
with st.sidebar:
    st.title("📜 診断履歴")
    history = load_history()
    
    if history:
        if st.button("履歴をすべて削除"):
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            st.rerun()

    if not history:
        st.write("履歴はまだありません。")
    else:
        for entry in reversed(history):
            with st.expander(f"{entry['date']} - {entry['profile']}"):
                st.write(f"**タイプ:** {entry['profile']}")
                for attr, score in entry['scores'].items():
                    st.write(f"{attr}: {score}")

# --- UI レイアウト ---

st.title("PERSONALITY ENGINE")

if not st.session_state.quiz_started:
    st.markdown("""
    <div class='question-card'>
        <p class='question-text' style='text-align: center;'>
            あなたの深層心理を分析し、4つの属性から真の姿を導き出します。<br>
            直感に従って10の質問に答えてください。
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("診断を開始する"):
        st.session_state.quiz_started = True
        st.rerun()

elif st.session_state.current_index < 10:
    # 進行状況
    progress = (st.session_state.current_index) / 10
    st.progress(progress)
    st.write(f"Question {st.session_state.current_index + 1} / 10")

    # 質問表示
    q = st.session_state.questions[st.session_state.current_index]
    
    st.markdown(f"""
    <div class='question-card'>
        <p class='question-text'>{q['text']}</p>
    </div>
    """, unsafe_allow_html=True)

    # 選択肢ボタン
    for i, choice in enumerate(q['choices']):
        if st.button(choice['text'], key=f"btn_{st.session_state.current_index}_{i}"):
            # スコア加算
            for attr, points in choice['points'].items():
                st.session_state.scores[attr] += points
            # 次の質問へ
            st.session_state.current_index += 1
            st.rerun()

else:
    # 結果表示
    st.markdown("<h3>分析完了</h3>", unsafe_allow_html=True)
    
    # 最多得点属性の判定
    top_attr = max(st.session_state.scores, key=st.session_state.scores.get)
    profiles = {
        "Logic": ("賢者", "論理的で冷静な判断ができる。真理を追求する知の探求者。"),
        "Empathy": ("交渉人", "他者の心に寄り添い、和を重んじる。絆を紡ぐ調停者。"),
        "Daring": ("勇者", "リスクを恐れず、直感で道を切り拓く。未来を掴む冒険者。"),
        "Prudence": ("守護者", "慎重に準備を整え、確実性を重視する。基盤を支える防衛者。")
    }
    profile_name, description = profiles[top_attr]

    # 履歴に保存 (一度だけ)
    if not st.session_state.result_saved:
        save_history(profile_name, st.session_state.scores)
        st.session_state.result_saved = True
        st.rerun() # 履歴を即座にサイドバーに反映させるため

    st.markdown(f"<div class='result-profile'>【 {profile_name} 】</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-description'>{description}</div>", unsafe_allow_html=True)

    # レーダーチャート作成
    df = pd.DataFrame(dict(
        r=list(st.session_state.scores.values()),
        theta=list(st.session_state.scores.keys())
    ))
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=df['r'],
        theta=df['theta'],
        fill='toself',
        line_color='#00ffcc',
        fillcolor='rgba(0, 255, 204, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(st.session_state.scores.values()) + 5], showticklabels=False, gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)", linecolor="rgba(255,255,255,0.1)")
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ffffff", size=14),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 詳細スコア
    cols = st.columns(4)
    for i, (attr, score) in enumerate(st.session_state.scores.items()):
        cols[i].metric(attr, score)

    st.write("---")
    if st.button("最初からやり直す"):
        reset_quiz()
        st.rerun()
