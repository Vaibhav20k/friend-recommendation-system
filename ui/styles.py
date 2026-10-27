"""Custom CSS styling system supporting both Light and Dark Streamlit themes.

Uses CSS variables and theme-adaptive classes to ensure readability and high aesthetics
on all displays, projectors, and themes.
"""

GLOBAL_CSS = """
<style>
/* CSS Variable Definitions based on Streamlit's theme context */
:root {
    --cc-primary: #2563EB;
    --cc-primary-light: rgba(37, 99, 235, 0.12);
    --cc-success: #10B981;
    --cc-success-light: rgba(16, 185, 129, 0.12);
    --cc-warning: #F59E0B;
    --cc-warning-light: rgba(245, 158, 11, 0.12);
    --cc-danger: #EF4444;
    --cc-danger-light: rgba(239, 68, 68, 0.12);
    --cc-card-bg: rgba(148, 163, 184, 0.08);
    --cc-card-border: rgba(148, 163, 184, 0.25);
    --cc-radius: 12px;
}

/* Metric Card enhancements */
div[data-testid="stMetric"] {
    background-color: var(--secondary-background-color, #F1F5F9);
    border: 1px solid var(--cc-card-border);
    padding: 12px 18px;
    border-radius: var(--cc-radius);
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

/* Base Card Style */
.cc-card {
    background-color: var(--secondary-background-color, #F8FAFC);
    border: 1px solid var(--cc-card-border);
    border-radius: var(--cc-radius);
    padding: 18px 22px;
    margin-bottom: 16px;
    transition: transform 0.15s ease, border-color 0.15s ease;
}
.cc-card:hover {
    border-color: var(--cc-primary);
}

/* Student Hero / Profile Card */
.cc-hero-card {
    background: linear-gradient(135deg, var(--secondary-background-color, #F1F5F9) 0%, rgba(37, 99, 235, 0.06) 100%);
    border: 1px solid var(--cc-card-border);
    border-left: 5px solid var(--cc-primary);
    border-radius: var(--cc-radius);
    padding: 20px 24px;
    margin-bottom: 20px;
}

/* Avatar Initials Circle */
.cc-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background-color: var(--cc-primary);
    color: #FFFFFF;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 17px;
    margin-right: 12px;
    vertical-align: middle;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Chips and Badges */
.cc-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 14px;
    font-size: 12px;
    font-weight: 600;
    margin: 2px 4px 2px 0;
    border: 1px solid transparent;
}

.cc-badge-branch {
    background-color: var(--cc-primary-light);
    color: var(--cc-primary);
    border-color: rgba(37, 99, 235, 0.25);
}

.cc-badge-year {
    background-color: rgba(148, 163, 184, 0.15);
    color: var(--text-color, inherit);
    border-color: var(--cc-card-border);
}

.cc-badge-interest {
    background-color: rgba(100, 116, 139, 0.12);
    color: var(--text-color, inherit);
    border-color: var(--cc-card-border);
}

.cc-badge-mutual {
    background-color: var(--cc-success-light);
    color: var(--cc-success);
    border-color: rgba(16, 185, 129, 0.25);
    font-weight: 700;
}

.cc-badge-hop {
    background-color: var(--cc-warning-light);
    color: var(--cc-warning);
    border-color: rgba(245, 158, 11, 0.3);
    font-size: 14px;
    padding: 4px 14px;
    border-radius: 16px;
    font-weight: 700;
}

.cc-badge-verified {
    background-color: var(--cc-success-light);
    color: var(--cc-success);
    border-color: rgba(16, 185, 129, 0.3);
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 13px;
    font-weight: 600;
}

/* Path chain container */
.cc-path-container {
    background-color: var(--secondary-background-color, #F8FAFC);
    border: 1px solid var(--cc-card-border);
    border-left: 5px solid var(--cc-warning);
    border-radius: var(--cc-radius);
    padding: 18px 24px;
    margin: 16px 0;
}

.cc-chain-step {
    display: inline-flex;
    align-items: center;
    background: var(--background-color, #FFFFFF);
    border: 1px solid var(--cc-card-border);
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    margin: 4px;
}

.cc-chain-arrow {
    display: inline-block;
    color: var(--cc-warning);
    font-size: 18px;
    margin: 0 4px;
    font-weight: 700;
}

/* Narration Box for BFS Visualizer */
.cc-narration-box {
    background-color: var(--secondary-background-color, #F8FAFC);
    border: 1px solid var(--cc-card-border);
    border-left: 5px solid var(--cc-primary);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 14px;
    font-size: 15px;
    line-height: 1.5;
}

/* Hash Table Bucket Bar */
.cc-bucket-row {
    display: flex;
    align-items: center;
    padding: 4px 0;
    font-size: 13px;
}
.cc-bucket-idx {
    width: 60px;
    font-family: monospace;
    font-weight: 600;
}
.cc-bucket-bar {
    height: 18px;
    background-color: var(--cc-primary);
    border-radius: 4px;
    margin: 0 8px;
    min-width: 4px;
    transition: width 0.2s ease;
}

/* Graph Container */
.cc-graph-frame {
    border: 1px solid var(--cc-card-border);
    border-radius: var(--cc-radius);
    overflow: hidden;
    background-color: var(--background-color, #FFFFFF);
}
</style>
"""


def apply_custom_styles() -> None:
    """Inject global CSS rules into current Streamlit page."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
