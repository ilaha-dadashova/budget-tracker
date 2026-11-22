"""
app.py - the Budget Tracker web page.

Start it with:   streamlit run app.py
(or just double-click run.bat on Windows)
"""

import calendar
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

import database as db

# --------------------------------------------------------------------------- #
#  Settings you can change
# --------------------------------------------------------------------------- #
CATEGORIES = ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Other"]
CATEGORY_EMOJI = {
    "Food": "🍔", "Transport": "🚗", "Entertainment": "🎬",
    "Bills": "🧾", "Shopping": "🛍️", "Other": "📦",
}
CATEGORY_COLORS = {
    "Food": "#F97316", "Transport": "#3B82F6", "Entertainment": "#8B5CF6",
    "Bills": "#14B8A6", "Shopping": "#EC4899", "Other": "#94A3B8",
}
GREEN, YELLOW, RED = "#22C55E", "#EAB308", "#EF4444"


def money(x: float) -> str:
    return f"${x:,.2f}"


def with_emoji(category: str) -> str:
    return f"{CATEGORY_EMOJI.get(category, '📦')} {category}"


# --------------------------------------------------------------------------- #
#  Page look & feel
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="Budget Tracker", page_icon="💰", layout="wide")

st.markdown(
    """
    <style>
      .block-container { padding-top: 2rem; max-width: 1200px; }
      .card {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px;
        padding: 1.25rem 1.5rem; box-shadow: 0 1px 3px rgba(15, 23, 42, .06);
        height: 100%;
      }
      .card-label {
        color: #64748B; font-size: .8rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: .06em;
      }
      .big-number {
        font-size: 3rem; font-weight: 800; color: #0F172A;
        line-height: 1.1; margin: .35rem 0 .25rem;
      }
      .sub { color: #64748B; font-size: .95rem; }
      .track {
        background: #E2E8F0; border-radius: 999px; height: 18px;
        overflow: hidden; margin: .9rem 0 .6rem;
      }
      .fill { height: 100%; border-radius: 999px; }
      .status { font-weight: 600; font-size: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
#  Load data
# --------------------------------------------------------------------------- #
db.init_db()
expenses = db.load_expenses()

today = date.today()
month_start = today.replace(day=1)
days_in_month = calendar.monthrange(today.year, today.month)[1]

this_month = expenses[
    (expenses["date"].dt.year == today.year) & (expenses["date"].dt.month == today.month)
]

# Show a little pop-up message left over from the last action (e.g. "Added!")
flash = st.session_state.pop("flash", None)
if flash:
    st.toast(flash, icon="✅")

# --------------------------------------------------------------------------- #
#  Sidebar: filters, budget, sample data
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("🔎 Filters")
    selected_categories = st.multiselect(
        "Categories", CATEGORIES, default=CATEGORIES, format_func=with_emoji
    )
    picked = st.date_input(
        "Date range", value=(month_start, today), format="MM/DD/YYYY"
    )
    # While you're still clicking, only one date may be picked - handle that.
    if isinstance(picked, (tuple, list)):
        if len(picked) == 2:
            start_date, end_date = picked
        elif len(picked) == 1:
            start_date = end_date = picked[0]
        else:
            start_date, end_date = month_start, today
    else:
        start_date = end_date = picked
    st.caption("Filters apply to the pie chart and the table. "
               "Category filters also apply to the daily bar chart.")

    st.divider()
    st.header("🎯 Monthly Budget")
    if "budget" not in st.session_state:
        st.session_state.budget = db.get_budget()
    st.number_input(
        "Budget limit ($)",
        min_value=0.0,
        step=50.0,
        format="%.2f",
        key="budget",
        on_change=lambda: db.set_budget(st.session_state.budget),
    )
    budget = float(st.session_state.budget)

    sample_count = int((expenses["is_sample"] == 1).sum())
    if sample_count:
        st.divider()
        st.header("🧹 Sample Data")
        st.caption(f"{sample_count} example expenses were added so you can see how the "
                   "app looks. Remove them when you're ready to track your own.")
        if st.button("Remove sample data"):
            db.clear_sample_data()
            st.session_state.flash = "Sample data removed"
            st.rerun()

# --------------------------------------------------------------------------- #
#  Header: total spent + budget progress
# --------------------------------------------------------------------------- #
st.title("💰 My Budget Tracker")
st.caption(f"{today:%A, %B} {today.day}, {today.year}")

spent = float(this_month["amount"].sum())
percent = (spent / budget * 100) if budget > 0 else (100.0 if spent > 0 else 0.0)

if spent > budget:
    bar_color, status = RED, f"🚨 Over budget by {money(spent - budget)}"
elif percent > 80:
    bar_color, status = YELLOW, f"⚠️ Careful! Only {money(budget - spent)} left"
else:
    bar_color, status = GREEN, f"✅ {money(budget - spent)} left to spend"

days_left = days_in_month - today.day
daily_avg = spent / today.day

col_total, col_budget = st.columns(2)
with col_total:
    st.markdown(
        f"""
        <div class="card">
          <div class="card-label">💸 Total spent in {today:%B}</div>
          <div class="big-number">{money(spent)}</div>
          <div class="sub">{len(this_month)} expenses · about {money(daily_avg)} per day ·
               {days_left} days left this month</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_budget:
    st.markdown(
        f"""
        <div class="card">
          <div class="card-label">🎯 Budget used</div>
          <div class="big-number" style="color:{bar_color}">{percent:.0f}%</div>
          <div class="track"><div class="fill"
               style="width:{min(percent, 100):.1f}%; background:{bar_color}"></div></div>
          <div class="status">{status}</div>
          <div class="sub">{money(spent)} of {money(budget)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# --------------------------------------------------------------------------- #
#  Add an expense
# --------------------------------------------------------------------------- #
st.subheader("➕ Add an Expense")

# After a successful add, empty the boxes (must happen before they are drawn).
if st.session_state.pop("reset_form", False):
    st.session_state.new_name = ""
    st.session_state.new_amount = 0.0
    st.session_state.new_date = today
if "new_date" not in st.session_state:
    st.session_state.new_date = today

with st.form("add_expense", border=True):
    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    name = c1.text_input("What did you buy?", placeholder="e.g. coffee, groceries, uber",
                         key="new_name")
    category = c2.selectbox("Category", CATEGORIES, format_func=with_emoji, key="new_category")
    amount = c3.number_input("Amount ($)", min_value=0.0, step=1.0, format="%.2f",
                             key="new_amount")
    when = c4.date_input("Date", format="MM/DD/YYYY", key="new_date")
    submitted = st.form_submit_button("Add Expense", type="primary")

if submitted:
    if not name.strip():
        st.error("Please type what the expense was for (for example: coffee).")
    elif amount <= 0:
        st.error("Please enter an amount bigger than $0.")
    else:
        db.add_expense(when, name.strip(), category, amount)
        st.session_state.flash = f"Added {name.strip()} — {money(amount)}"
        st.session_state.reset_form = True
        st.rerun()

# --------------------------------------------------------------------------- #
#  Dashboard charts
# --------------------------------------------------------------------------- #
filtered = expenses[
    expenses["category"].isin(selected_categories)
    & (expenses["date"] >= pd.Timestamp(start_date))
    & (expenses["date"] <= pd.Timestamp(end_date))
]

st.subheader("📊 Dashboard")
chart_left, chart_right = st.columns(2)

with chart_left:
    with st.container(border=True):
        st.markdown(f"**🥧 Spending by category**  \n"
                    f"<span style='color:#64748B'>{start_date:%b} {start_date.day} – "
                    f"{end_date:%b} {end_date.day}, {end_date.year}</span>",
                    unsafe_allow_html=True)
        if filtered.empty:
            st.info("No expenses match your filters.")
        else:
            by_category = (filtered.groupby("category", as_index=False)["amount"].sum()
                           .sort_values("amount", ascending=False))
            pie = px.pie(by_category, names="category", values="amount", color="category",
                         color_discrete_map=CATEGORY_COLORS, hole=0.55)
            pie.update_traces(
                textinfo="percent+label",
                hovertemplate="%{label}: $%{value:,.2f}<extra></extra>",
                marker=dict(line=dict(color="#FFFFFF", width=2)),
                sort=False,
            )
            pie.update_layout(
                showlegend=False, height=360, margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                annotations=[dict(text=f"<b>{money(by_category['amount'].sum())}</b>",
                                  showarrow=False, font=dict(size=20, color="#0F172A"))],
            )
            st.plotly_chart(pie, config={"displayModeBar": False})

with chart_right:
    with st.container(border=True):
        st.markdown(f"**📅 Daily spending in {today:%B}**  \n"
                    f"<span style='color:#64748B'>Each bar is one day</span>",
                    unsafe_allow_html=True)
        month_rows = this_month[this_month["category"].isin(selected_categories)]
        all_days = pd.date_range(month_start, periods=days_in_month, freq="D")
        daily = (month_rows.groupby(month_rows["date"].dt.normalize())["amount"].sum()
                 .reindex(all_days, fill_value=0.0))
        daily_df = pd.DataFrame({"day": all_days, "amount": daily.values})

        bar = px.bar(daily_df, x="day", y="amount")
        bar.update_traces(marker_color="#6366F1",
                          hovertemplate="%{x|%b %d}: $%{y:,.2f}<extra></extra>")
        bar.update_layout(
            height=360, margin=dict(t=10, b=10, l=10, r=10), bargap=0.25,
            xaxis_title=None, yaxis_title=None, yaxis_tickprefix="$",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        bar.update_xaxes(tickformat="%b %d", showgrid=False)
        bar.update_yaxes(gridcolor="#E2E8F0")
        st.plotly_chart(bar, config={"displayModeBar": False})

# --------------------------------------------------------------------------- #
#  Expense table
# --------------------------------------------------------------------------- #
st.subheader("📋 My Expenses")
table = filtered[["id", "date", "name", "category", "amount"]].copy()
table["category"] = table["category"].map(with_emoji)

st.caption(f"{len(table)} expenses · {money(table['amount'].sum())} total "
           f"(using the filters in the sidebar)")
st.dataframe(
    table.drop(columns="id"),
    hide_index=True,
    column_config={
        "date": st.column_config.DateColumn("📆 Date", format="MMM D, YYYY"),
        "name": st.column_config.TextColumn("📝 Name"),
        "category": st.column_config.TextColumn("🏷️ Category"),
        "amount": st.column_config.NumberColumn("💵 Amount", format="$%.2f"),
    },
)

col_dl, col_del = st.columns([1, 2])
with col_dl:
    st.download_button(
        "⬇️ Download as spreadsheet (CSV)",
        data=filtered[["date", "name", "category", "amount"]]
        .assign(date=lambda d: d["date"].dt.strftime("%Y-%m-%d"))
        .to_csv(index=False),
        file_name="expenses.csv",
        mime="text/csv",
    )
with col_del:
    with st.expander("🗑️ Delete an expense"):
        if table.empty:
            st.write("Nothing to delete with the current filters.")
        else:
            labels = {
                row.id: f"{row.date:%b %d, %Y} · {row.name} · {row.category} · {money(row.amount)}"
                for row in table.itertuples()
            }
            to_delete = st.selectbox("Pick the expense to delete", list(labels),
                                     format_func=labels.get)
            if st.button("Delete this expense"):
                db.delete_expense(to_delete)
                st.session_state.flash = "Expense deleted"
                st.rerun()
