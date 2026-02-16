import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import json

from algorithm import run_line_balancing
from database import init_db, save_run, load_runs, load_run_by_id
from report import generate_pdf

# PAGE CONFIG 
st.set_page_config(page_title="Line Balancing Tool", layout="wide")
st.title("Line Balancing Simulation")

# DATABASE INIT 
conn, cursor = init_db()

# DISPLAY FUNCTION 
def display_results(alloc_df, target_rate, actual_rate, cycle_time, stations, efficiency, save_path=None):
    st.subheader("Workstation Allocation")
    st.dataframe(alloc_df, use_container_width=True)

    st.subheader("Key Metrics")
    st.write(f"Target Output Rate: {target_rate}")
    st.write(f"Actual Output Rate: {actual_rate:.2f}%")
    st.write(f"Cycle Time: {cycle_time}")
    st.write(f"Number of Workstations: {stations}")
    st.write(f"Efficiency: {efficiency:.2f}%")

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(alloc_df["Station"], alloc_df["Total Time (min)"], width=0.5)
    ax.axhline(cycle_time, linestyle="--", color="red", label="Cycle Time")
    ax.set_xlabel("Station")
    ax.set_ylabel("Workload (min)")
    ax.set_title("Workload of Each Station")
    ax.legend()
    plt.tight_layout() 

    if save_path:
        fig.savefig(save_path)

    st.pyplot(fig)
    return fig

# TABS
tab1, tab2 = st.tabs(["Simulation", "History"])

# SIMULATION TAB 
with tab1:
    df = st.data_editor(
        pd.DataFrame({
            "Task": pd.Series(dtype=str),
            "Time (min)": pd.Series(dtype=float),
            "Predecessors": pd.Series(dtype=str)
        }),
        num_rows="dynamic",
        use_container_width=True
    )

    target_rate = st.number_input(
        "Target Output Rate (units/hour)",
        min_value=1.0,
        step=1.0
    )

    if st.button("Run Simulation"):

        stations, cycle_time, actual_rate, num_stations = run_line_balancing(df, target_rate)

        alloc_df = pd.DataFrame([
            {
                "Station": s,
                "Tasks": " | ".join(d["tasks"]),
                "Total Time (min)": round(d["time"], 2)
            }
            for s, d in stations.items()
        ])

        efficiency = (df["Time (min)"].sum() / (num_stations * cycle_time)) * 100

        graph_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        display_results(
            alloc_df,
            target_rate,
            actual_rate,
            cycle_time,
            num_stations,
            efficiency,
            save_path=graph_path
        )

        # Save to database
        save_run(
            cursor, conn,
            target_rate, actual_rate,
            cycle_time, num_stations,
            efficiency, alloc_df
        )

        st.session_state.latest = {
            "alloc_df": alloc_df,
            "target_rate": target_rate,
            "actual_rate": actual_rate,
            "cycle_time": cycle_time,
            "stations": num_stations,
            "efficiency": efficiency,
            "graph_path": graph_path
        }

    # PDF Download
    if "latest" in st.session_state:
        if st.button("Download"):
            pdf = generate_pdf(st.session_state.latest)
            with open(pdf, "rb") as f:
                st.download_button("Download Report", f, "Line_Balancing_Report.pdf")

# HISTORY TAB
with tab2:
    records = load_runs(cursor)

    if records:
        labels = {f"Run {r[0]} | {r[1]}": r[0] for r in records}
        selected = st.selectbox("Select Run", labels.keys())

        run = load_run_by_id(cursor, labels[selected])
        _, _, target_rate, actual_rate, cycle_time, stations, efficiency, allocation = run

        alloc_df = pd.DataFrame(json.loads(allocation))

        display_results(
            alloc_df,
            target_rate,
            actual_rate,
            cycle_time,
            stations,
            efficiency
        )
