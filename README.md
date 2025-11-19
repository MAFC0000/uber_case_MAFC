# Business Case: Predictive Analytics & Operational Dashboarding for ATD Optimization

## Repository Overview & Strategic Value
This repository contains the complete analytics pipeline designed to enhance delivery accuracy and optimize operational efficiency for Uber Eats in the Mexico region. The core objective is to move from historical reporting to real-time predictive insights.

**Key Deliverables:**
* *Data Extraction query:* Contains the SQL query (.sql file) necessary to consolidate raw operational tables into a clean, model-ready dataset. This query is designed for weekly refreshment, ensuring data integrity for both reporting and predictive modeling.

* *Streamlit Dashboard (streamlit_dashboard/):* Serves as the primary operational and managerial interface, here we will find two pages.
    - Historical & Trend Analysis: Integrates descriptive analytics of delivery performance alongside a Time Series Forecasting model to project future delivery volumes and ATD trends.
    - ATD Prediction (Live Inference): Enables real-time, point-in-time predictions of Actual Time of Delivery (ATD) based on user-selected features (Territory, Hour, Distance, ...). The predictions are provided by three validated models (Random Forest, XGBoost, and a Multilayer Neural Network) to offer enhanced reliability and confidence scores.

* *Final Presentation (summary_presentation.pdf):* A concise, managerial deck that outlines the end-to-end methodology, key business insights derived from the analysis and strategic implications of the models.

## Dataset 
The analysis utilizes a comprehensive dataset detailing deliveries across the marketplace in March and April for Mexico.

The modelling relies on structured features derived from the raw data, including cyclical features (Day of Week, Hour), mapped geographic variables (Territory Average Velocity), and core logistics metrics (pickup_distance, dropoff_distance).

## Setup & Production Notes
* *Reproducibility:* Inside the streamlit_dashboard folder, the requirements.txt file lists all required Python libraries (Pandas, Streamlit, Scikit-learn, XGBoost, Joblib, etc.) necessary to fully run the project. In the 'How to run.txt' file we will find a detailed guide to run the dashboard.

* *Model Deployment:* The entire prediction logic (preprocessor + final model) is encapsulated within a serialized joblib pipeline. This ensures that the live prediction in the dashboard uses the exact same transformations (normalization, cyclical encoding, imputation) as the training environment, ensuring consistency and reliability.
