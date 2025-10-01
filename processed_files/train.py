import streamlit as st
from streamlit_ace import st_ace
import io, contextlib, ast

st.title("📘 Learn Python with NBA Data")
st.subheader("Lesson 1: Variables and Basics 🏀")

# --- Utility function with type-aware checking ---
def run_exercise(starter_code, expected_output, expected_type, success_msg, hint_msg, key):
    code = st_ace(
        value=starter_code,
        language="python",
        theme="merbivore",
        height=200,
        font_size=14,
        tab_size=4,
        show_gutter=True,
        wrap=True,
        auto_update=True,
        key=key
    )

    if st.button("Run My Code", key=key+"-btn"):
        output_buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(output_buffer):
                exec(code, {})
            output = output_buffer.getvalue()
        except Exception as e:
            output = f"❌ Error: {e}"

        st.subheader("Execution Result:")
        if output.strip() == "":
            st.info("Your code ran, but produced no output.")
            return
        else:
            st.code(output, language="text")

        # ✅ Type-aware checker
        try:
            user_value = ast.literal_eval(output.strip())
        except Exception:
            user_value = output.strip()

        if isinstance(user_value, expected_type) and user_value == expected_output:
            st.success(success_msg)
        else:
            st.warning(hint_msg)


# --- Exercise 1 ---
st.write("### Exercise 1: Assign and Print a Value")
st.write("""
LeBron scored **30 points** in his last game.  
👉 Assign `30` to the variable `lebron_points`, and then print it.
""")
run_exercise(
    starter_code="""# TODO: Assign 30 to lebron_points and print it
""",
    expected_output=30,
    expected_type=int,
    success_msg="✅ Correct! LeBron scored 30 points 🎉",
    hint_msg="⚠️ Try again. Make sure you are printing the **number**.",
    key="ex1"
)

