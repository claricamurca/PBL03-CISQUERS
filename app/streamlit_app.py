from __future__ import annotations

import html
from typing import Any

import streamlit as st

try:
    from app.local_inference import predict_student_risk
except ModuleNotFoundError:
    from local_inference import predict_student_risk


st.set_page_config(
    page_title="Previsão de Desempenho Escolar",
    layout="wide",
    initial_sidebar_state="collapsed",
)


YES_NO_OPTIONS = {
    "yes": "Sim",
    "no": "Não",
}

SCHOOL_OPTIONS = {
    "GP": "Escola Gabriel Pereira (GP)",
    "MS": "Escola Mousinho da Silveira (MS)",
}

SUBJECT_OPTIONS = {
    "mathematics": "Matemática",
    "portuguese": "Português",
}

SEX_OPTIONS = {
    "F": "Feminino",
    "M": "Masculino",
}

ADDRESS_OPTIONS = {
    "U": "Zona urbana",
    "R": "Zona rural",
}

FAMILY_SIZE_OPTIONS = {
    "GT3": "Família com mais de 3 pessoas",
    "LE3": "Família com até 3 pessoas",
}

PARENT_STATUS_OPTIONS = {
    "T": "Pais vivem juntos",
    "A": "Pais separados",
}

JOB_OPTIONS = {
    "teacher": "Professor(a)",
    "health": "Área da saúde",
    "services": "Serviços",
    "at_home": "Trabalha em casa",
    "other": "Outra ocupação",
}

REASON_OPTIONS = {
    "home": "Proximidade de casa",
    "reputation": "Reputação da escola",
    "course": "Preferência pelo curso",
    "other": "Outro motivo",
}

GUARDIAN_OPTIONS = {
    "mother": "Mãe",
    "father": "Pai",
    "other": "Outro responsável",
}

SECTION_TEXT = {
    "section_1": (
        "Seção 1",
        "Identificação do estudante",
        "Informações de identificação, origem escolar e contexto familiar do registro analisado.",
    ),
    "section_2": (
        "Seção 2",
        "Histórico escolar",
        "Indicadores de trajetória acadêmica recente, frequência, notas e rotina de estudo.",
    ),
    "section_3": (
        "Seção 3",
        "Contexto familiar e social",
        "Variáveis de apoio, rotina pessoal, sociabilidade, bem-estar e hábitos associados ao estudante.",
    ),
    "section_4": (
        "Seção 4",
        "Resultado da predição",
        "Após o envio do formulário, esta área consolida a probabilidade estimada, o resumo executivo, os fatores analíticos e a recomendação de acompanhamento.",
    ),
}

RISK_PROFILES = {
    "low": {
        "badge_label": "Baixo risco",
        "badge_class": "status-low",
        "summary": "O perfil informado apresenta menor probabilidade de baixo desempenho acadêmico no cenário analisado.",
        "management_reading": "O conjunto de sinais informado sugere estabilidade relativa no momento, com espaço para acompanhamento preventivo de rotina e manutenção das condições favoráveis.",
        "follow_up": "Manter acompanhamento pedagógico regular, observando evolução de notas, frequência e engajamento ao longo dos próximos períodos.",
    },
    "moderate": {
        "badge_label": "Risco moderado",
        "badge_class": "status-medium",
        "summary": "O perfil informado reúne sinais de atenção acadêmica e merece monitoramento preventivo mais próximo.",
        "management_reading": "Há indícios de vulnerabilidade que justificam observação mais frequente do desempenho, da rotina escolar e das condições de apoio ao estudante.",
        "follow_up": "Priorizar contato pedagógico, revisar frequência, alinhar apoio com a família e avaliar medidas de reforço ou suporte adicional.",
    },
    "high": {
        "badge_label": "Risco elevado",
        "badge_class": "status-high",
        "summary": "O conjunto de informações informado se aproxima de perfis historicamente associados a maior probabilidade de baixo desempenho.",
        "management_reading": "O caso pede leitura mais cuidadosa e articulada entre sinais acadêmicos, frequência e contexto do estudante para orientar resposta mais rápida.",
        "follow_up": "Acionar acompanhamento mais intensivo, revisar fatores acadêmicos e sociais e definir um plano de apoio individualizado com monitoramento contínuo.",
    },
}

RISK_LEVEL_THRESHOLDS = {
    "low_max": 0.35,
    "moderate_max": 0.65,
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-main: #070B17;
            --bg-secondary: #0D1324;
            --bg-card: #11182B;
            --bg-card-elevated: #151D34;
            --accent-purple: #8B5CF6;
            --accent-magenta: #D946EF;
            --accent-cyan: #38BDF8;
            --accent-indigo: #6366F1;
            --success: #22C55E;
            --warning: #F59E0B;
            --error: #EF4444;
            --text-main: #F8FAFC;
            --text-secondary: #CBD5E1;
            --text-muted: #94A3B8;
            --border-soft: rgba(148, 163, 184, 0.15);
            --shadow-card: 0 24px 80px rgba(2, 6, 23, 0.45);
            --shadow-glow: 0 0 0 1px rgba(139, 92, 246, 0.16), 0 0 32px rgba(56, 189, 248, 0.10);
            --radius-lg: 24px;
            --radius-md: 18px;
            --radius-sm: 14px;
            --font-stack: Inter, Manrope, "Segoe UI", Roboto, sans-serif;
        }

        html, body, [class*="css"] {
            font-family: var(--font-stack);
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 10%, rgba(139, 92, 246, 0.20), transparent 28%),
                radial-gradient(circle at 88% 12%, rgba(217, 70, 239, 0.16), transparent 24%),
                radial-gradient(circle at 78% 78%, rgba(56, 189, 248, 0.14), transparent 24%),
                linear-gradient(180deg, #070B17 0%, #09101D 45%, #070B17 100%);
            color: var(--text-main);
        }

        [data-testid="stAppViewContainer"] > .main {
            background: transparent;
        }

        [data-testid="stHeader"],
        #MainMenu,
        footer {
            visibility: hidden;
            height: 0;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(13, 19, 36, 0.96) 0%, rgba(9, 16, 30, 0.96) 100%);
            border-right: 1px solid var(--border-soft);
        }

        [data-testid="stSidebar"] * {
            color: var(--text-secondary);
        }

        [data-testid="stSidebar"] [data-testid="stTextInput"] input {
            background: rgba(17, 24, 43, 0.88);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.2rem;
            padding-bottom: 4rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background:
                linear-gradient(180deg, rgba(21, 29, 52, 0.92) 0%, rgba(17, 24, 43, 0.98) 100%);
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-card), var(--shadow-glow);
            padding: 1.2rem 1.25rem 1.4rem 1.25rem;
            margin-bottom: 1.15rem;
            position: relative;
            overflow: hidden;
        }

        [data-testid="stVerticalBlockBorderWrapper"]::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 2px;
            background: linear-gradient(90deg, rgba(139, 92, 246, 0), rgba(139, 92, 246, 0.95), rgba(56, 189, 248, 0.85), rgba(217, 70, 239, 0));
        }

        .hero-shell {
            position: relative;
            overflow: hidden;
            padding: 2rem 2rem 1.85rem 2rem;
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(21, 29, 52, 0.96) 0%, rgba(17, 24, 43, 0.98) 45%, rgba(13, 19, 36, 1) 100%);
            border: 1px solid var(--border-soft);
            box-shadow: var(--shadow-card), var(--shadow-glow);
            margin-bottom: 1.15rem;
        }

        .hero-shell::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 12% 18%, rgba(139, 92, 246, 0.26), transparent 34%),
                radial-gradient(circle at 82% 10%, rgba(56, 189, 248, 0.18), transparent 26%),
                radial-gradient(circle at 90% 80%, rgba(217, 70, 239, 0.14), transparent 22%);
            pointer-events: none;
        }

        .hero-topline {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.45rem 0.9rem;
            border-radius: 999px;
            color: var(--text-main);
            background: rgba(99, 102, 241, 0.14);
            border: 1px solid rgba(99, 102, 241, 0.35);
            font-size: 0.82rem;
            letter-spacing: 0.02em;
            font-weight: 600;
            margin-bottom: 1rem;
        }

        .hero-title {
            font-size: clamp(2rem, 3.8vw, 3.35rem);
            line-height: 1.04;
            font-weight: 800;
            color: var(--text-main);
            margin: 0 0 0.75rem 0;
            max-width: 880px;
        }

        .hero-subtitle {
            color: var(--text-secondary);
            font-size: 1.04rem;
            line-height: 1.7;
            max-width: 820px;
            margin: 0 0 1.2rem 0;
        }

        .hero-meta-row {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin-top: 1.3rem;
        }

        .hero-meta-card {
            padding: 0.95rem 1rem;
            border-radius: var(--radius-md);
            background: rgba(13, 19, 36, 0.78);
            border: 1px solid rgba(148, 163, 184, 0.12);
            backdrop-filter: blur(8px);
        }

        .hero-meta-label {
            color: var(--text-muted);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
        }

        .hero-meta-value {
            color: var(--text-main);
            font-size: 0.98rem;
            font-weight: 600;
            line-height: 1.45;
        }

        .section-kicker {
            color: var(--accent-cyan);
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 700;
            margin-bottom: 0.45rem;
        }

        .section-title {
            color: var(--text-main);
            font-size: 1.3rem;
            line-height: 1.25;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .section-subtitle {
            color: var(--text-muted);
            font-size: 0.96rem;
            line-height: 1.6;
            margin-bottom: 1.1rem;
            max-width: 760px;
        }

        .field-caption {
            color: var(--text-muted);
            font-size: 0.82rem;
            line-height: 1.5;
            margin: -0.12rem 0 0.95rem 0;
        }

        .result-card,
        .factor-card,
        .management-box,
        .responsible-box,
        .notice-box,
        .metric-card {
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.12);
            padding: 1.2rem 1.2rem 1.15rem 1.2rem;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.02),
                0 14px 34px rgba(2, 6, 23, 0.20);
            min-height: 100%;
        }

        .metric-card {
            background:
                linear-gradient(180deg, rgba(19, 28, 52, 0.92) 0%, rgba(13, 19, 36, 0.96) 100%);
        }

        .result-card,
        .factor-card,
        .management-box,
        .responsible-box,
        .notice-box {
            background: rgba(13, 19, 36, 0.78);
        }

        .metric-card::before,
        .result-card::before,
        .factor-card::before,
        .management-box::before,
        .responsible-box::before,
        .notice-box::before {
            content: "";
            display: block;
            height: 1px;
            margin: -1.2rem -1.2rem 1rem -1.2rem;
            background: linear-gradient(90deg, rgba(139, 92, 246, 0), rgba(139, 92, 246, 0.48), rgba(56, 189, 248, 0.42), rgba(139, 92, 246, 0));
        }

        .result-card {
            background:
                linear-gradient(180deg, rgba(17, 24, 43, 0.92) 0%, rgba(13, 19, 36, 0.95) 100%);
        }

        .result-label {
            color: var(--text-muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
        }

        .result-value {
            color: var(--text-main);
            font-size: 2.35rem;
            line-height: 1;
            font-weight: 800;
            margin-bottom: 0.4rem;
        }

        .result-note,
        .notice-box p,
        .management-box p,
        .responsible-box p {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.62;
            margin: 0;
        }

        .card-title {
            color: var(--text-main);
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .card-subtitle {
            color: var(--text-muted);
            font-size: 0.88rem;
            line-height: 1.55;
            margin-bottom: 0.85rem;
        }

        .result-summary-text {
            color: var(--text-secondary);
            font-size: 0.96rem;
            line-height: 1.68;
            margin-top: 0.2rem;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.42rem 0.8rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.82rem;
            margin-bottom: 0.85rem;
        }

        .status-low {
            color: #C4F7D4;
            background: rgba(34, 197, 94, 0.14);
            border: 1px solid rgba(34, 197, 94, 0.28);
        }

        .status-medium {
            color: #FDE7B2;
            background: rgba(245, 158, 11, 0.14);
            border: 1px solid rgba(245, 158, 11, 0.28);
        }

        .status-high {
            color: #FFD2D2;
            background: rgba(239, 68, 68, 0.14);
            border: 1px solid rgba(239, 68, 68, 0.28);
        }

        .summary-meta-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.8rem;
            margin-top: 1rem;
        }

        .summary-meta-card {
            border-radius: 16px;
            border: 1px solid rgba(148, 163, 184, 0.10);
            background: rgba(21, 29, 52, 0.68);
            padding: 0.9rem 0.95rem;
        }

        .summary-meta-label {
            color: var(--text-muted);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.3rem;
        }

        .summary-meta-value {
            color: var(--text-main);
            font-size: 0.9rem;
            line-height: 1.55;
            font-weight: 600;
        }

        .factor-risk {
            border-color: rgba(239, 68, 68, 0.16);
            background:
                linear-gradient(180deg, rgba(34, 13, 22, 0.24) 0%, rgba(13, 19, 36, 0.82) 100%);
        }

        .factor-protective {
            border-color: rgba(34, 197, 94, 0.16);
            background:
                linear-gradient(180deg, rgba(11, 32, 24, 0.20) 0%, rgba(13, 19, 36, 0.82) 100%);
        }

        .factor-list {
            display: grid;
            gap: 0.7rem;
            margin-top: 0.8rem;
        }

        .factor-item {
            padding: 0.85rem 0.9rem;
            border-radius: 16px;
            background: rgba(21, 29, 52, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.10);
        }

        .factor-item-title {
            color: var(--text-main);
            font-size: 0.93rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .factor-item-text {
            color: var(--text-muted);
            font-size: 0.86rem;
            line-height: 1.55;
        }

        .responsible-box {
            background: rgba(56, 189, 248, 0.08);
            border-color: rgba(56, 189, 248, 0.18);
        }

        .recommendation-box {
            background:
                linear-gradient(180deg, rgba(19, 28, 52, 0.88) 0%, rgba(13, 19, 36, 0.92) 100%);
            border-color: rgba(99, 102, 241, 0.18);
        }

        .result-block-spacer {
            height: 0.95rem;
        }

        .method-note {
            color: var(--text-muted);
            font-size: 0.82rem;
            line-height: 1.55;
            margin-top: 0.7rem;
        }

        .progress-shell {
            margin: 0.95rem 0 0.85rem 0;
        }

        .progress-track {
            width: 100%;
            height: 0.58rem;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.14);
            overflow: hidden;
            box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.06);
        }

        .progress-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 52%, #38BDF8 100%);
            box-shadow: 0 0 18px rgba(99, 102, 241, 0.24);
        }

        .notice-error {
            background: rgba(239, 68, 68, 0.10);
            border-color: rgba(239, 68, 68, 0.28);
        }

        .notice-info {
            background: rgba(56, 189, 248, 0.10);
            border-color: rgba(56, 189, 248, 0.24);
        }

        .stTextInput label p,
        .stSelectbox label p,
        .stNumberInput label p,
        .stSlider label p {
            color: var(--text-main) !important;
            font-weight: 600;
            letter-spacing: 0;
        }

        [data-testid="stCaptionContainer"] p {
            color: var(--text-muted) !important;
            font-size: 0.82rem !important;
            line-height: 1.5 !important;
        }

        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        .stNumberInput > div > div {
            background: rgba(13, 19, 36, 0.84) !important;
            border: 1px solid rgba(148, 163, 184, 0.15) !important;
            border-radius: 16px !important;
            min-height: 3rem;
            box-shadow: none !important;
        }

        [data-baseweb="select"] > div:hover,
        [data-baseweb="input"] > div:hover,
        .stNumberInput > div > div:hover {
            border-color: rgba(99, 102, 241, 0.42) !important;
        }

        [data-baseweb="select"] input,
        [data-baseweb="input"] input,
        .stNumberInput input {
            color: var(--text-main) !important;
        }

        .stSelectbox div[data-baseweb="select"] span {
            color: var(--text-main);
        }

        .stSlider {
            margin-top: 0.1rem;
        }

        .stSlider [data-baseweb="slider"] {
            padding-top: 0.35rem !important;
            padding-bottom: 0.2rem !important;
        }

        .stSlider [data-baseweb="slider"] > div > div > div > div:nth-child(1),
        .stSlider [data-baseweb="slider"] > div > div > div > div:nth-child(2) {
            height: 0.34rem !important;
            border-radius: 999px !important;
        }

        .stSlider [data-baseweb="slider"] > div > div > div > div:nth-child(1) {
            background: rgba(172, 177, 195, 0.22) !important;
            background-image: none !important;
            background-color: rgba(172, 177, 195, 0.22) !important;
            box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.05) !important;
        }

        .stSlider [data-baseweb="slider"] > div > div > div > div:nth-child(2),
        .stSlider [data-baseweb="slider"] > div > div > div > div:nth-child(2)[class] {
            background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 48%, #38BDF8 100%) !important;
            background-image: linear-gradient(90deg, #6366F1 0%, #8B5CF6 48%, #38BDF8 100%) !important;
            background-color: transparent !important;
            box-shadow: 0 0 16px rgba(99, 102, 241, 0.18) !important;
        }

        .stSlider [data-baseweb="slider"] [role="slider"] {
            width: 18px !important;
            height: 18px !important;
            border-radius: 50% !important;
            border: 2px solid rgba(248, 250, 252, 0.96) !important;
            background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 55%, #38BDF8 100%) !important;
            background-image: linear-gradient(135deg, #8B5CF6 0%, #6366F1 55%, #38BDF8 100%) !important;
            box-shadow:
                0 0 0 6px rgba(99, 102, 241, 0.14),
                0 10px 26px rgba(56, 189, 248, 0.20) !important;
        }

        .stSlider [data-baseweb="slider"] [role="slider"]:hover,
        .stSlider [data-baseweb="slider"] [role="slider"]:focus {
            outline: none !important;
            box-shadow:
                0 0 0 7px rgba(56, 189, 248, 0.16),
                0 12px 30px rgba(99, 102, 241, 0.30) !important;
        }

        .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
            background: rgba(17, 24, 43, 0.98) !important;
            color: var(--text-main) !important;
            border: 1px solid rgba(99, 102, 241, 0.35) !important;
            border-radius: 999px !important;
            box-shadow: 0 10px 24px rgba(2, 6, 23, 0.35) !important;
        }

        .stSlider input[type="range"] {
            accent-color: #8B5CF6 !important;
        }

        .stSlider [aria-valuenow] {
            accent-color: #8B5CF6 !important;
        }

        .stSlider p,
        .stSlider span {
            color: var(--text-secondary) !important;
        }

        .stSlider *::selection {
            background: transparent !important;
        }

        .stSlider [data-testid="stSliderTickBar"] {
            color: rgba(203, 213, 225, 0.72) !important;
        }

        .stSlider [data-testid*="tick"],
        .stSlider [class*="tick"],
        .stSlider [class*="mark"],
        .stSlider [data-testid*="mark"] {
            color: var(--text-muted) !important;
            background: transparent !important;
        }

        .stButton > button,
        .stFormSubmitButton > button {
            width: 100%;
            min-height: 3.3rem;
            border-radius: 18px;
            border: 1px solid rgba(139, 92, 246, 0.38);
            background: linear-gradient(90deg, #7C3AED 0%, #8B5CF6 38%, #6366F1 72%, #38BDF8 100%);
            color: white;
            font-weight: 700;
            font-size: 1rem;
            box-shadow: 0 18px 34px rgba(99, 102, 241, 0.26);
            transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 22px 42px rgba(99, 102, 241, 0.34);
            filter: brightness(1.04);
        }

        .stButton > button:focus,
        .stFormSubmitButton > button:focus {
            outline: none;
            box-shadow: 0 0 0 1px rgba(255,255,255,0.12), 0 0 0 4px rgba(56, 189, 248, 0.18);
        }

        @media (max-width: 980px) {
            .hero-meta-row,
            .summary-meta-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        f"""
        <section class="hero-shell">
            <div class="hero-topline">IA aplicada à gestão educacional</div>
            <h1 class="hero-title">Sistema Inteligente de Previsão de Desempenho Escolar</h1>
            <p class="hero-subtitle">
                Plataforma de apoio à gestão educacional com análise preditiva de risco acadêmico,
                construída para transformar dados escolares em sinais práticos de acompanhamento.
            </p>
            <div class="hero-meta-row">
                <div class="hero-meta-card">
                    <div class="hero-meta-label">Objetivo</div>
                    <div class="hero-meta-value">Apoiar gestores na identificação antecipada de estudantes com maior probabilidade de baixo desempenho.</div>
                </div>
                <div class="hero-meta-card">
                    <div class="hero-meta-label">Modelo</div>
                    <div class="hero-meta-value">Rede neural MLP com inferência local em Streamlit, sem dependência de backend externo em tempo de execução.</div>
                </div>
                <div class="hero-meta-card">
                    <div class="hero-meta-label">Execução</div>
                    <div class="hero-meta-value">Modelo, pré-processador e esquema de atributos carregados diretamente dos artefatos do projeto.</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="section-kicker">{html.escape(kicker)}</div>
        <div class="section-title">{html.escape(title)}</div>
        <div class="section-subtitle">{html.escape(subtitle)}</div>
        """,
        unsafe_allow_html=True,
    )


def render_notice(title: str, message: str, kind: str = "error") -> None:
    st.markdown(
        f"""
        <div class="notice-box notice-{kind}">
            <div class="card-title">{html.escape(title)}</div>
            <p>{html.escape(message)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def select_mapped_option(
    label: str,
    options: dict[str, str],
    default: str,
    help_text: str | None = None,
) -> str:
    values = list(options.keys())
    return st.selectbox(
        label,
        values,
        index=values.index(default),
        format_func=lambda value: options[value],
        help=help_text,
    )


def yes_no(label: str, default: str = "no", help_text: str | None = None) -> str:
    return select_mapped_option(label, YES_NO_OPTIONS, default, help_text)


def slider_with_caption(
    label: str,
    min_value: int,
    max_value: int,
    value: int,
    caption: str,
    help_text: str | None = None,
) -> int:
    selected = st.slider(label, min_value, max_value, value, help=help_text)
    st.markdown(
        f'<div class="field-caption">{html.escape(caption)}</div>',
        unsafe_allow_html=True,
    )
    return int(selected)


def number_input_with_caption(
    label: str,
    min_value: int,
    max_value: int,
    value: int,
    caption: str,
    help_text: str | None = None,
) -> int:
    selected = st.number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        help=help_text,
    )
    st.markdown(
        f'<div class="field-caption">{html.escape(caption)}</div>',
        unsafe_allow_html=True,
    )
    return int(selected)


def format_percentage_ptbr(probability: float) -> str:
    return f"{probability * 100:.1f}%".replace(".", ",")


def localize_api_risk_label(risk_label: str) -> str:
    normalized = (risk_label or "").strip().lower()
    mapping = {
        "risk of low performance": "Risco de baixo desempenho",
        "at risk of low performance": "Risco de baixo desempenho",
        "no elevated risk": "Sem risco elevado",
        "low risk": "Baixo risco",
        "moderate risk": "Risco moderado",
        "high risk": "Risco elevado",
    }
    return mapping.get(normalized, risk_label)


def get_risk_level(
    probability: float,
    predicted_class: int,
    risk_label: str | None = None,
) -> str:
    normalized_label = (risk_label or "").strip().lower()
    probability = max(0.0, min(1.0, float(probability)))

    # O endpoint retorna `risk_probability` para a classe positiva de risco.
    # Portanto a hierarquia visual da Seção 4 deve seguir a própria probabilidade,
    # e não palavras soltas do rótulo textual.
    if probability < RISK_LEVEL_THRESHOLDS["low_max"]:
        return "low"
    if probability < RISK_LEVEL_THRESHOLDS["moderate_max"]:
        return "moderate"
    return "high"


def get_risk_profile(risk_level: str) -> dict[str, str]:
    return RISK_PROFILES.get(risk_level, RISK_PROFILES["moderate"])


def get_risk_titles(risk_level: str) -> tuple[str, str]:
    if risk_level == "low":
        return (
            "Principais fatores que poderiam elevar o risco",
            "Fatores que podem reduzir ainda mais o risco",
        )
    return (
        "Principais fatores que aumentaram o risco",
        "Fatores que ajudam a reduzir o risco",
    )


def classify_risk(probability: float, predicted_class: int) -> tuple[str, str, str, str]:
    risk_profile = get_risk_profile(get_risk_level(probability, predicted_class))
    return (
        risk_profile["badge_label"],
        risk_profile["badge_class"],
        risk_profile["summary"],
        risk_profile["follow_up"],
    )


def _make_factor(weight: int, title: str, detail: str) -> dict[str, Any]:
    return {"weight": weight, "title": title, "detail": detail}


def build_hybrid_explanation(
    features: dict[str, Any],
    probability: float,
    predicted_class: int,
) -> dict[str, Any]:
    risk_factors: list[dict[str, Any]] = []
    protective_factors: list[dict[str, Any]] = []

    def add_risk(weight: int, title: str, detail: str) -> None:
        risk_factors.append(_make_factor(weight, title, detail))

    def add_protective(weight: int, title: str, detail: str) -> None:
        protective_factors.append(_make_factor(weight, title, detail))

    g1 = int(features["G1"])
    g2 = int(features["G2"])
    failures = int(features["failures"])
    absences = int(features["absences"])
    studytime = int(features["studytime"])
    traveltime = int(features["traveltime"])
    famrel = int(features["famrel"])
    freetime = int(features["freetime"])
    goout = int(features["goout"])
    dalc = int(features["Dalc"])
    walc = int(features["Walc"])
    health = int(features["health"])

    if g2 <= 9:
        add_risk(10, "Desempenho recente mais baixo em G2", "A nota do segundo período está abaixo do patamar de referência e sinaliza dificuldade acadêmica mais próxima da nota final.")
    elif g2 >= 12:
        add_protective(9, "Desempenho recente satisfatório em G2", "A nota do segundo período sugere base acadêmica mais consistente no momento.")

    if g1 <= 9:
        add_risk(9, "Desempenho inicial mais baixo em G1", "A nota do primeiro período indica que as dificuldades podem ter começado antes e não apenas no momento atual.")
    elif g1 >= 12:
        add_protective(7, "Bom desempenho em G1", "A nota do primeiro período indica histórico recente de aprendizagem mais favorável.")

    if failures >= 2:
        add_risk(8, "Histórico de reprovações anteriores", "O registro informa duas ou mais reprovações anteriores, o que costuma aumentar a necessidade de acompanhamento pedagógico.")
    elif failures == 1:
        add_risk(6, "Presença de reprovação anterior", "Há ao menos uma reprovação anterior registrada, fator que pode indicar trajetória escolar mais vulnerável.")
    else:
        add_protective(6, "Ausência de reprovações anteriores", "Não há reprovações anteriores registradas, o que tende a indicar trajetória escolar mais estável.")

    if absences >= 10:
        add_risk(7, "Frequência fragilizada por faltas elevadas", "O volume de faltas é alto e pode impactar continuidade de aprendizagem, vínculo com a rotina escolar e desempenho.")
    elif absences >= 5:
        add_risk(4, "Faltas acima do ideal", "A quantidade de faltas já merece observação, pois pode afetar acompanhamento de conteúdos.")
    elif absences <= 2:
        add_protective(3, "Boa regularidade de frequência", "O número reduzido de faltas favorece continuidade pedagógica e acompanhamento das atividades.")

    if studytime == 1:
        add_risk(5, "Tempo de estudo semanal reduzido", "A dedicação extraclasse informada é baixa, o que pode limitar consolidação de conteúdos.")
    elif studytime >= 3:
        add_protective(4, "Maior dedicação aos estudos", "O tempo de estudo semanal informado está acima do nível básico e tende a apoiar melhor desempenho.")

    if traveltime >= 3:
        add_risk(3, "Deslocamento mais longo até a escola", "Um tempo de deslocamento maior pode aumentar desgaste diário e reduzir disponibilidade para estudo e descanso.")

    if features["famsup"] == "yes":
        add_protective(4, "Apoio educacional da família", "O registro informa apoio familiar aos estudos, fator que pode contribuir para organização e acompanhamento.")
    else:
        add_risk(2, "Ausência de apoio educacional da família", "A ausência de suporte educacional familiar pode reduzir a rede de apoio ao processo de aprendizagem.")

    if features["schoolsup"] == "yes":
        add_protective(3, "Apoio escolar adicional", "Há suporte pedagógico complementar registrado, o que pode ajudar a mitigar dificuldades.")

    if features["higher"] == "yes":
        add_protective(3, "Expectativa de continuidade dos estudos", "A intenção de cursar ensino superior costuma aparecer associada a metas educacionais mais claras.")
    else:
        add_risk(2, "Baixa sinalização de continuidade educacional", "A ausência de intenção de seguir para o ensino superior pode refletir menor conexão com objetivos acadêmicos de longo prazo.")

    if features["activities"] == "yes":
        add_protective(2, "Participação em atividades extracurriculares", "A participação em atividades extracurriculares pode fortalecer vínculo escolar e engajamento.")

    if features["internet"] == "yes":
        add_protective(2, "Acesso à internet em casa", "O acesso à internet amplia possibilidades de estudo, pesquisa e acompanhamento de atividades.")
    else:
        add_risk(2, "Restrição de acesso à internet em casa", "A ausência de internet pode limitar apoio aos estudos fora do ambiente escolar.")

    if famrel <= 2:
        add_risk(3, "Relação familiar mais frágil", "A percepção de relação familiar menos positiva pode afetar estabilidade emocional e apoio cotidiano.")
    elif famrel >= 4:
        add_protective(2, "Relação familiar mais positiva", "Uma relação familiar melhor percebida pode contribuir para suporte emocional e rotina mais organizada.")

    if dalc >= 4 or walc >= 4:
        add_risk(3, "Consumo de álcool mais elevado", "O padrão informado de consumo de álcool é alto e pode estar associado a maior vulnerabilidade acadêmica.")

    if goout >= 4:
        add_risk(2, "Rotina social mais intensa", "Saídas frequentes com amigos podem reduzir tempo disponível para estudo ou descanso em alguns perfis.")

    if freetime >= 4 and studytime == 1:
        add_risk(2, "Mais tempo livre com menor dedicação aos estudos", "A combinação sugere espaço para reorganização da rotina acadêmica.")

    if health <= 2:
        add_risk(2, "Saúde percebida como mais fragilizada", "Condições de saúde menos favoráveis podem interferir em frequência, energia e desempenho.")
    elif health >= 4:
        add_protective(1, "Boa saúde percebida", "Melhor condição de saúde pode favorecer presença, disposição e continuidade das atividades.")

    risk_factors = sorted(risk_factors, key=lambda item: item["weight"], reverse=True)[:5]
    protective_factors = sorted(protective_factors, key=lambda item: item["weight"], reverse=True)[:5]
    risk_profile = get_risk_profile(get_risk_level(probability, predicted_class))

    return {
        "summary": risk_profile["summary"],
        "management_reading": risk_profile["management_reading"],
        "follow_up": risk_profile["follow_up"],
        "risk_factors": risk_factors or [
            _make_factor(
                0,
                "Sem sinais críticos dominantes",
                "Os fatores informados não exibem, isoladamente, um conjunto forte de alertas adicionais além do padrão geral capturado pela estimativa.",
            )
        ],
        "protective_factors": protective_factors or [
            _make_factor(
                0,
                "Poucos fatores protetivos explícitos",
                "O formulário não destacou muitos elementos de proteção claros, o que sugere olhar mais atento para apoio pedagógico e contexto do estudante.",
            )
        ],
        "responsible_use": "Esta camada explicativa combina o resultado do modelo com regras interpretativas baseadas nas informações preenchidas. Ela apoia a análise, mas não representa causalidade nem substitui a avaliação pedagógica individual.",
        "method_note": "Estrutura preparada para futura evolução com técnicas de explicabilidade baseadas em modelo, como SHAP, sem alterar o fluxo principal de predição.",
    }


def build_status_badge(label: str, css_class: str) -> str:
    return f'<div class="status-badge {css_class}">{html.escape(label)}</div>'


def render_metric_card(probability: float) -> None:
    progress_width = min(max(probability * 100, 0), 100)
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="result-label">Probabilidade estimada de risco</div>
            <div class="result-value">{format_percentage_ptbr(probability)}</div>
            <div class="progress-shell" aria-hidden="true">
                <div class="progress-track">
                    <div class="progress-fill" style="width: {progress_width:.1f}%;"></div>
                </div>
            </div>
            <div class="result-note">
                Percentual calculado localmente pelo modelo para a classe de risco de baixo desempenho acadêmico.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_card(
    risk_profile: dict[str, str],
    summary: str,
    risk_label: str,
    recommendation: str,
) -> None:
    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-label">Resumo executivo da análise</div>
            {build_status_badge(risk_profile["badge_label"], risk_profile["badge_class"])}
            <div class="result-summary-text">{html.escape(summary)}</div>
            <div class="summary-meta-grid">
                <div class="summary-meta-card">
                    <div class="summary-meta-label">Classificação calculada pelo modelo</div>
                    <div class="summary-meta-value">{html.escape(risk_label)}</div>
                </div>
                <div class="summary-meta-card">
                    <div class="summary-meta-label">Primeira recomendação</div>
                    <div class="summary-meta-value">{html.escape(recommendation)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_factor_card(title: str, subtitle: str, items: list[dict[str, Any]], tone: str) -> None:
    st.markdown(
        f"""
        <div class="factor-card factor-{tone}">
            <div class="card-title">{html.escape(title)}</div>
            <div class="card-subtitle">{html.escape(subtitle)}</div>
            <div class="factor-list">
        """,
        unsafe_allow_html=True,
    )
    for item in items:
        st.markdown(
            f"""
            <div class="factor-item">
                <div class="factor-item-title">{html.escape(item["title"])}</div>
                <div class="factor-item-text">{html.escape(item["detail"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_insight_card(css_class: str, title: str, text: str, extra: str | None = None) -> None:
    extra_html = f'<div class="method-note">{html.escape(extra)}</div>' if extra else ""
    st.markdown(
        f"""
        <div class="{css_class}">
            <div class="card-title">{html.escape(title)}</div>
            <p>{html.escape(text)}</p>
            {extra_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_section(
    probability: float,
    predicted_class: int,
    risk_label: str,
    explanation: dict[str, Any],
) -> None:
    risk_level = get_risk_level(probability, predicted_class, risk_label)
    risk_profile = get_risk_profile(risk_level)
    risk_title, protective_title = get_risk_titles(risk_level)

    top_left, top_right = st.columns([0.92, 1.28])
    with top_left:
        render_metric_card(probability)
    with top_right:
        render_summary_card(
            risk_profile=risk_profile,
            summary=explanation["summary"],
            risk_label=risk_label,
            recommendation=explanation["follow_up"],
        )

    st.markdown('<div class="result-block-spacer"></div>', unsafe_allow_html=True)
    factor_left, factor_right = st.columns(2)
    with factor_left:
        render_factor_card(
            risk_title,
            "Sinais analíticos do perfil informado que merecem atenção no cenário atual.",
            explanation["risk_factors"],
            tone="risk",
        )
    with factor_right:
        render_factor_card(
            protective_title,
            "Sinais de proteção que ajudam a sustentar a estabilidade acadêmica e orientar o acompanhamento.",
            explanation["protective_factors"],
            tone="protective",
        )

    st.markdown('<div class="result-block-spacer"></div>', unsafe_allow_html=True)
    insight_left, insight_right = st.columns(2)
    with insight_left:
        render_insight_card(
            "management-box",
            "Interpretação para a gestão",
            explanation["management_reading"],
        )
    with insight_right:
        render_insight_card(
            "management-box recommendation-box",
            "Recomendação de acompanhamento",
            explanation["follow_up"],
        )

    st.markdown('<div class="result-block-spacer"></div>', unsafe_allow_html=True)
    render_insight_card(
        "responsible-box",
        "Uso responsável e nota metodológica",
        explanation["responsible_use"],
        extra=explanation["method_note"],
    )


inject_styles()

st.sidebar.markdown("### Configuração")
st.sidebar.caption(
    "Interface analítica em português com predição local, usando os artefatos treinados do próprio projeto."
)

render_hero()

with st.form("student_form"):
    with st.container(border=True):
        render_section_header(*SECTION_TEXT["section_1"])
        col1, col2 = st.columns(2)
        with col1:
            school = select_mapped_option(
                "Escola de origem",
                SCHOOL_OPTIONS,
                "GP",
                "Selecione a escola associada ao registro. O valor interno continua sendo GP ou MS.",
            )
            subject = select_mapped_option(
                "Disciplina de referência",
                SUBJECT_OPTIONS,
                "mathematics",
                "Escolha se o registro corresponde a Matemática ou Português.",
            )
            sex = select_mapped_option(
                "Sexo do estudante",
                SEX_OPTIONS,
                "F",
                "Campo categórico conforme a estrutura original do conjunto de dados.",
            )
            age = number_input_with_caption(
                "Idade do estudante",
                min_value=15,
                max_value=22,
                value=16,
                caption="Informe a idade em anos completos. Faixa aceita pelo modelo: 15 a 22 anos.",
                help_text="Valor numérico contínuo em anos completos.",
            )
            address = select_mapped_option(
                "Local de residência",
                ADDRESS_OPTIONS,
                "U",
                "Indica se o estudante vive em zona urbana ou rural.",
            )
            famsize = select_mapped_option(
                "Tamanho da família",
                FAMILY_SIZE_OPTIONS,
                "GT3",
                "Categoria familiar do conjunto de dados: até 3 pessoas ou mais de 3 pessoas.",
            )
        with col2:
            Pstatus = select_mapped_option(
                "Situação de convivência dos pais",
                PARENT_STATUS_OPTIONS,
                "T",
                "Indica se os pais vivem juntos ou separados.",
            )
            guardian = select_mapped_option(
                "Responsável principal",
                GUARDIAN_OPTIONS,
                "mother",
                "Pessoa que responde mais diretamente pelo estudante no contexto do registro.",
            )
            Medu = slider_with_caption(
                "Escolaridade da mãe",
                0,
                4,
                2,
                "0 = nenhuma • 1 = ensino fundamental I • 2 = ensino fundamental II • 3 = ensino médio • 4 = ensino superior",
                help_text="Escala ordinal de escolaridade materna usada no conjunto de dados.",
            )
            Fedu = slider_with_caption(
                "Escolaridade do pai",
                0,
                4,
                2,
                "0 = nenhuma • 1 = ensino fundamental I • 2 = ensino fundamental II • 3 = ensino médio • 4 = ensino superior",
                help_text="Escala ordinal de escolaridade paterna usada no conjunto de dados.",
            )
            Mjob = select_mapped_option(
                "Ocupação da mãe",
                JOB_OPTIONS,
                "other",
                "Categoria profissional cadastrada no conjunto de dados original.",
            )
            Fjob = select_mapped_option(
                "Ocupação do pai",
                JOB_OPTIONS,
                "other",
                "Categoria profissional cadastrada no conjunto de dados original.",
            )
            reason = select_mapped_option(
                "Motivo da escolha da escola",
                REASON_OPTIONS,
                "course",
                "Escolha a razão predominante registrada para a seleção da escola.",
            )

    with st.container(border=True):
        render_section_header(*SECTION_TEXT["section_2"])
        col1, col2 = st.columns(2)
        with col1:
            traveltime = slider_with_caption(
                "Tempo de deslocamento até a escola",
                1,
                4,
                1,
                "1 = menos de 15 min • 2 = 15 a 30 min • 3 = 30 min a 1 h • 4 = mais de 1 h",
                help_text="Escala categórica usada no conjunto de dados para o tempo de viagem entre casa e escola.",
            )
            studytime = slider_with_caption(
                "Tempo de estudo semanal",
                1,
                4,
                2,
                "1 = menos de 2 h • 2 = 2 a 5 h • 3 = 5 a 10 h • 4 = mais de 10 h",
                help_text="Escala categórica que representa o volume semanal de estudo fora da sala de aula.",
            )
            failures = slider_with_caption(
                "Reprovações anteriores",
                0,
                4,
                0,
                "Quantidade de reprovações anteriores.",
                help_text="Número de reprovações anteriores registradas no histórico do estudante.",
            )
        with col2:
            absences = number_input_with_caption(
                "Faltas escolares",
                min_value=0,
                max_value=100,
                value=4,
                caption="Número total de faltas escolares registradas.",
                help_text="Informe a quantidade acumulada de faltas do estudante.",
            )
            G1 = slider_with_caption(
                "Nota G1",
                0,
                20,
                10,
                "Escala de 0 a 20 referente ao primeiro período letivo.",
                help_text="Nota do primeiro período letivo na escala original do conjunto de dados.",
            )
            G2 = slider_with_caption(
                "Nota G2",
                0,
                20,
                10,
                "Escala de 0 a 20 referente ao segundo período letivo.",
                help_text="Nota do segundo período letivo na escala original do conjunto de dados.",
            )

    with st.container(border=True):
        render_section_header(*SECTION_TEXT["section_3"])
        col1, col2 = st.columns(2)
        with col1:
            schoolsup = yes_no(
                "Recebe apoio escolar extra?",
                help_text="Marque se o estudante recebe suporte pedagógico adicional oferecido pela escola.",
            )
            famsup = yes_no(
                "Recebe apoio educacional da família?",
                "yes",
                "Indica se há apoio familiar voltado aos estudos e à vida escolar.",
            )
            paid = yes_no(
                "Faz aulas particulares pagas?",
                help_text="Refere-se à participação em aulas extras particulares ou reforço pago.",
            )
            activities = yes_no(
                "Participa de atividades extracurriculares?",
                "yes",
                "Inclui esportes, clubes, oficinas e outras atividades além das aulas regulares.",
            )
            nursery = yes_no(
                "Frequentou creche ou educação infantil?",
                "yes",
                "Informação histórica presente no conjunto de dados original.",
            )
            higher = yes_no(
                "Pretende cursar o ensino superior?",
                "yes",
                "Reflete a expectativa declarada do estudante em relação à continuidade dos estudos.",
            )
            internet = yes_no(
                "Possui acesso à internet em casa?",
                "yes",
                "Indica se o estudante dispõe de internet residencial.",
            )
        with col2:
            romantic = yes_no(
                "Está em relacionamento amoroso?",
                help_text="Campo categórico do conjunto de dados relacionado ao contexto pessoal do estudante.",
            )
            famrel = slider_with_caption(
                "Relação familiar",
                1,
                5,
                4,
                "1 = muito ruim • 5 = excelente",
                help_text="Escala ordinal sobre como o estudante percebe a relação com a família.",
            )
            freetime = slider_with_caption(
                "Tempo livre após a escola",
                1,
                5,
                3,
                "1 = muito baixo • 5 = muito alto",
                help_text="Escala ordinal para a quantidade de tempo livre disponível após as aulas.",
            )
            goout = slider_with_caption(
                "Saídas com amigos",
                1,
                5,
                3,
                "1 = raramente • 5 = com muita frequência",
                help_text="Escala ordinal para a frequência de saídas com amigos.",
            )
            Dalc = slider_with_caption(
                "Consumo de álcool nos dias úteis",
                1,
                5,
                1,
                "1 = muito baixo • 5 = muito alto",
                help_text="Escala ordinal para o consumo de álcool ao longo da semana.",
            )
            Walc = slider_with_caption(
                "Consumo de álcool no fim de semana",
                1,
                5,
                2,
                "1 = muito baixo • 5 = muito alto",
                help_text="Escala ordinal para o consumo de álcool aos fins de semana.",
            )
            health = slider_with_caption(
                "Estado de saúde atual",
                1,
                5,
                3,
                "1 = muito ruim • 5 = muito bom",
                help_text="Autoavaliação do estado geral de saúde em escala ordinal.",
            )

    submitted = st.form_submit_button("Calcular risco")

payload = {
    "school": school,
    "sex": sex,
    "age": int(age),
    "address": address,
    "famsize": famsize,
    "Pstatus": Pstatus,
    "Medu": int(Medu),
    "Fedu": int(Fedu),
    "Mjob": Mjob,
    "Fjob": Fjob,
    "reason": reason,
    "guardian": guardian,
    "traveltime": int(traveltime),
    "studytime": int(studytime),
    "failures": int(failures),
    "schoolsup": schoolsup,
    "famsup": famsup,
    "paid": paid,
    "activities": activities,
    "nursery": nursery,
    "higher": higher,
    "internet": internet,
    "romantic": romantic,
    "famrel": int(famrel),
    "freetime": int(freetime),
    "goout": int(goout),
    "Dalc": int(Dalc),
    "Walc": int(Walc),
    "health": int(health),
    "absences": int(absences),
    "G1": int(G1),
    "G2": int(G2),
    "subject": subject,
}

with st.container(border=True):
    render_section_header(*SECTION_TEXT["section_4"])
    if submitted:
        try:
            prediction = predict_student_risk(payload)
            probability = float(prediction.risk_probability)
            predicted_class = int(prediction.predicted_class)
            localized_risk_label = localize_api_risk_label(str(prediction.risk_label))
            explanation = build_hybrid_explanation(payload, probability, predicted_class)
            render_result_section(
                probability=probability,
                predicted_class=predicted_class,
                risk_label=localized_risk_label,
                explanation=explanation,
            )
        except Exception as exc:
            render_notice(
                "Falha ao executar a predição local",
                f"Não foi possível carregar os artefatos ou calcular a predição localmente: {exc}",
                kind="error",
            )
    else:
        render_notice(
            "Análise pronta para execução",
            "Preencha os dados do estudante e clique em “Calcular risco” para gerar a leitura preditiva.",
            kind="info",
        )
