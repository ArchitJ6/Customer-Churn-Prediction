import streamlit as st
import pandas as pd
import pickle
import datetime

with open("artifacts/model.pkl", "rb") as f:
    model = pickle.load(f)
with open("artifacts/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
with open("artifacts/label_encoders.pkl", "rb") as f:
    label_encoders = pickle.load(f)
with open("artifacts/feature_columns.pkl", "rb") as f:
    feature_columns = pickle.load(f)

st.title("🔮 Churn Prediction App")
st.markdown("Enter customer data below to predict churn probability.")

# Create input form
def get_user_input():
    input_dict = {}
    # Sort feature columns to ensure consistent order
    sorted_feature_columns=sorted(feature_columns, key=lambda x: (int(x.split('_')[0][1:]), x.split('_')[1] if '_' in x else ''))
    for col in sorted_feature_columns:
        if col.endswith("_year") or col.endswith("_month"):
            base = col.rsplit("_", 1)[0]
            if base+ "_year" in feature_columns and base + "_month" not in input_dict:
                date = st.date_input(f"{base} (YYYY-MM-DD)", value=datetime.date(2015, 1, 1))
                input_dict[f"{base}_year"] = date.year
                input_dict[f"{base}_month"] = date.month
        elif col in label_encoders:
            options = label_encoders[col].classes_.tolist()
            if col == "month lease":
                options = sorted(options, key=lambda x: int(x.split()[0]))
            else:
                options = sorted(options)
            selection = st.selectbox(f"{col}", options)
            input_dict[col] = label_encoders[col].transform([selection])[0]
        else:
            val = st.number_input(f"{col}", value=0.0, format="%.4f")
            input_dict[col] = val
    return input_dict

user_input = get_user_input()

if st.button("Predict"):
    input_df = pd.DataFrame([user_input])[feature_columns]
    input_scaled = pd.DataFrame(scaler.transform(input_df), columns=feature_columns)
    prediction = model.predict(input_scaled)[0]
    probability = model.predict_proba(input_scaled)[0][1]

    st.success(f"Predicted Churn: {'Yes' if prediction == 1 else 'No'}")
    st.info(f"Churn Probability: {probability:.2%}")