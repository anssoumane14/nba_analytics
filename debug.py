
# -------------------------------
# II. SALARIES
# -------------------------------
with tab_salaries:
    st.markdown(f"### Player Salaries — {selected_team}")

    if not df_salaries.empty:
        # all years available in salary dataset (except static columns)
        all_years = sorted([c for c in df_salaries.columns if c not in ["PLAYER", "TEAM", "Guaranteed"]])
        selected_year = st.selectbox("Select Contract Year", all_years, index=0, key="salary_year")

        df_team_year = df_salaries[df_salaries["TEAM"] == selected_team][
            ["PLAYER", "TEAM", selected_year, "Guaranteed"]
        ]

        if df_team_year.empty:
            st.info("No salary data available for this team.")
        else:
            st.dataframe(df_team_year, hide_index=True, use_container_width=True)
    else:
        st.info("No salary data available.")

