
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from collections import Counter
from datetime import datetime

st.set_page_config(page_title="Defense Analysis Console — Streamlit", layout="wide")

st.title("Defense Analysis Console — Streamlit (Prototype v0.1)")
st.caption("맥락 동시가시, 부분참조/스냅샷 개념, Run Profile 비교, 보고서 마법사(개념 스텁), 감사추적 뷰 등을 모사한 통합 대시보드")

# --------------- Data Loading ---------------
st.sidebar.header("데이터 로딩")
uploaded = st.sidebar.file_uploader("엑셀 파일 업로드(분석관인터뷰 형식)", type=["xlsx"])
use_sample = st.sidebar.checkbox("샘플 데이터 사용", value=True)

@st.cache_data
def parse_excel(xls_bytes) -> pd.DataFrame:
    try:
        xls = pd.ExcelFile(xls_bytes)
        if "interview 221013" in xls.sheet_names:
            df = xls.parse("interview 221013")
        else:
            df = xls.parse(xls.sheet_names[0])
        df.columns = [str(c).strip() for c in df.columns]
        for c in df.columns[:3]:
            df[c] = df[c].ffill()
        topic = df.columns[0]
        subtopic = df.columns[1]
        prompt = df.columns[2]
        text_cols = [c for c in df.columns if c not in (topic, subtopic, prompt)]
        long = df.melt(id_vars=[topic, subtopic, prompt], value_vars=text_cols,
                       var_name="speaker", value_name="utterance")
        long["topic"] = df[topic]
        long["subtopic"] = df[subtopic]
        long["prompt"] = df[prompt]
        long["utterance"] = long["utterance"].astype(str)
        long = long[long["utterance"].str.strip().ne("nan") & long["utterance"].str.strip().ne("")]
        long = long[["topic","subtopic","prompt","speaker","utterance"]].reset_index(drop=True)
        return long
    except Exception as e:
        st.error(f"엑셀 파싱 에러: {e}")
        return pd.DataFrame(columns=["topic","subtopic","prompt","speaker","utterance"])

@st.cache_data
def load_sample() -> pd.DataFrame:
    return pd.read_csv("data/sample_long.csv")

if uploaded is not None:
    df_long = parse_excel(uploaded)
elif use_sample:
    df_long = load_sample()
else:
    df_long = pd.DataFrame(columns=["topic","subtopic","prompt","speaker","utterance"])

st.sidebar.write(f"로우 수: {len(df_long)}")

# --------------- Filters ---------------
with st.sidebar.expander("필터", expanded=True):
    topics = sorted(df_long["topic"].dropna().astype(str).unique().tolist())
    speakers = sorted(df_long["speaker"].dropna().astype(str).unique().tolist())
    sel_topics = st.multiselect("주제(topic)", topics, default=topics[: min(5, len(topics))])
    sel_speakers = st.multiselect("발화자(speaker)", speakers, default=speakers)
    kw = st.text_input("키워드 포함(정규표현식 허용)", "")

    df_f = df_long.copy()
    if sel_topics:
        df_f = df_f[df_f["topic"].astype(str).isin(sel_topics)]
    if sel_speakers:
        df_f = df_f[df_f["speaker"].astype(str).isin(sel_speakers)]
    if kw.strip():
        try:
            df_f = df_f[df_f["utterance"].str.contains(kw, regex=True, na=False)]
        except Exception as e:
            st.warning(f"키워드 식 에러: {e}")

# --------------- Layout: 3 columns = 좌·중·우 ---------------
left, center, right = st.columns([2.2, 3.4, 2.4])

# Left: 과제개요/시나리오메타/보안 템플릿
with left:
    st.subheader("과제 개요 / 메타 / 보안")
    with st.container(border=True):
        st.markdown("**과제 개요**")
        st.write("- 과제명: 해상 다영역 시나리오 평가")
        st.write("- 요청부서: 전력분석")
        st.write("- 등급: 대내비 (자동 마스킹 ON)")
        st.write("- 상태: 내부 검토 중")
    with st.container(border=True):
        st.markdown("**시나리오 메타(싱글소스)**")
        st.write("- 작전구역: Sector‑A (EEZ 북서)")
        st.write("- 기상: 해상 풍속 12–15kt, 가시성 4km")
        st.write("- 통신: SATCOM 제한, Link‑X 간헐")
    with st.container(border=True):
        st.markdown("**권한·보안 템플릿**")
        st.write("- 초안 → 내부공유 → 승인 → 대외배포")
        st.write("- 공유 시 자동 워터마크/비식별화")
        st.write("- 역할 기반 접근제어 (RBAC)")

# Center: 시나리오 캔버스(개념), Run Profile, 사전검증
with center:
    st.subheader("시나리오 캔버스 & 실행 환경")
    with st.container(border=True):
        st.markdown("**시나리오 블록 (개념 모형)**")
        blk_cols = st.columns(5)
        blocks = [("접근/탐지",3),("분류/식별",5),("평가/결정",2),("분배/교전",4),("회복/동기화",1)]
        for i,(bn,refs) in enumerate(blocks):
            with blk_cols[i%5]:
                st.markdown(f"- **{bn}**  \n참조:{refs}회")
                c1,c2 = st.columns(2)
                if c1.button("부분참조", key=f"embed_{i}"):
                    st.toast(f"부분참조 생성: {bn}")
                if c2.button("스냅샷", key=f"snap_{i}"):
                    st.toast(f"스냅샷 복제: {bn}")
        st.caption("※ ‘부분참조(Embed)’는 원본 업데이트 자동 반영, ‘스냅샷’은 분기 복제")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("**변수 세트 (Run Profile)**")
            rp = pd.DataFrame([
                {"ID":"RP-01","Name":"Baseline / 해역 A","Vars":12,"Updated":"2025-10-10"},
                {"ID":"RP-02","Name":"악천후 + 통신제약","Vars":12,"Updated":"2025-10-11"},
                {"ID":"RP-03","Name":"전력손실 20%","Vars":14,"Updated":"2025-10-12"},
            ])
            st.dataframe(rp, use_container_width=True, hide_index=True)
            c3,c4,c5 = st.columns(3)
            if c3.button("저장"):
                st.toast("Run Profile 저장")
            if c4.button("불러오기"):
                st.toast("Run Profile 불러오기")
            if c5.button("Δ 비교"):
                st.session_state["_open_compare"] = True
    with c2:
        with st.container(border=True):
            st.markdown("**실행 전 검증 (오류값/체크리스트)**")
            st.write("- 입력 범위/단위 검증")
            st.write("- 결측·이상치 사전 필터")
            st.write("- 가정(Assumption) 명세 확인")

# Right: 결과 카드, 미니 상황도, 데이터 탐색
with right:
    st.subheader("결과 & 탐색")
    with st.container(border=True):
        st.markdown("**결과 카드**")
        results = [
            {"id":"RES-201","from":"RP-01","time":"+0.0%","loss":"0.8%","note":"기준선"},
            {"id":"RES-224","from":"RP-02","time":"+4.2%","loss":"1.7%","note":"통신제약 영향"},
            {"id":"RES-245","from":"RP-03","time":"+8.9%","loss":"2.4%","note":"전력손실 영향"},
        ]
        for r in results:
            with st.expander(f"{r['id']} · from {r['from']} — KPI(Time {r['time']}, Loss {r['loss']})", expanded=False):
                st.write(r["note"])
                c1,c2 = st.columns(2)
                if c1.button("↔ 원 시나리오", key=f"link_scn_{r['id']}"):
                    st.toast(f"{r['id']} ↔ 원 시나리오로 이동")
                if c2.button("보고 반영", key=f"link_rep_{r['id']}"):
                    st.toast(f"{r['id']} → 보고서에 반영")
    with st.container(border=True):
        st.markdown("**미니 상황도 (결과뷰 고정 미니맵)**")
        fig = plt.figure(figsize=(4,2))
        plt.plot([0,1,2,3,4],[1,2,1,3,2])
        plt.title("결과 연계 블록 하이라이트(개념)")
        st.pyplot(fig, clear_figure=True)

# --------------- Analysis Zone (원본 데이터 탐색) ---------------
st.divider()
st.subheader("원본 인터뷰 데이터 탐색")

st.write(f"필터 후 로우 수: **{len(df_f)}**")
st.dataframe(df_f, use_container_width=True)

# 문제/요구 키워드 빈도
pain_keywords = ['불편','오류','없음','필요','복사','권한','보안','요청','반복','시간']
pain_counts = {k: int(df_f['utterance'].str.contains(k, na=False).sum()) for k in pain_keywords}
st.markdown("**문제/요구 관련 키워드 빈도(필터 반영)**")
fig2 = plt.figure(figsize=(6,3))
plt.bar(list(pain_counts.keys()), list(pain_counts.values()))
plt.title("Pain Keyword Frequency")
plt.xticks(rotation=45)
st.pyplot(fig2, clear_figure=True)

# --------------- Compare Drawer (개념) ---------------
if st.session_state.get("_open_compare", False):
    st.subheader("Run Profile Δ 비교")
    colA, colB = st.columns(2)
    with colA:
        st.markdown("**RP-01 · Baseline / 해역 A**")
        st.write("- 변수 12개 / 단위·범위 규정 일치")
        st.write("- 환경: 기준")
        st.write("- 예상 KPI 민감도: Time +0.0%")
    with colB:
        st.markdown("**RP-02 · 악천후 + 통신제약**")
        st.write("- 변수 12개 / 단위·범위 규정 일치")
        st.write("- 환경: 통신 가용 저하, 가시성 저하")
        st.write("- 예상 KPI 민감도: Time +4.2%")
    st.markdown("**차이 하이라이트**")
    diff = pd.DataFrame([
        {"변수":"가시성(km)","RP‑01":8,"RP‑02":4,"Δ":-4},
        {"변수":"통신가용(%)","RP‑01":92,"RP‑02":61,"Δ":-31},
    ])
    st.dataframe(diff, use_container_width=True, hide_index=True)

# --------------- Report Wizard (개념) ---------------
with st.expander("보고서 마법사", expanded=False):
    grade = st.selectbox("보안 등급", ["대내비","대외제한","대외공개"])
    tmpl = st.multiselect("템플릿 섹션", ["대안별 KPI 비교 요약","가정/제약/출처 패널","민감도 래더 & 위험 포인트"], ["대안별 KPI 비교 요약"])
    st.caption("등급에 따라 변수명 비식별/수치 ±α 마스킹 자동 적용(개념)")
    if st.button("미리보기 생성"):
        st.success("자동 요약: RP‑02(통신제약) Time +4.2%, Loss +0.9% 증가. 통신가용/가시성이 주요 민감변수로 식별.")

# --------------- Audit Trail (개념) ---------------
st.divider()
st.subheader("감사 추적 (Who/When/Why — 개념)")
st.write("10:14 · B-2 변수범위 수정(홍OO) — 사유: 가시성 실측치 반영")
st.write("10:21 · RP-02 저장(김OO) — 통신가용 92→61")
st.write("10:33 · RES-224 생성 — from RP-02")
