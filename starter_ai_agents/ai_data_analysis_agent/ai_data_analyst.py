import json
import tempfile
import csv
import re
import streamlit as st
import pandas as pd
import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckdb import DuckDbTools
from agno.tools.pandas import PandasTools

# Function to preprocess and save the uploaded file
def preprocess_and_save(file):
    try:
        # Read the uploaded file into a DataFrame
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file, na_values=['NA', 'N/A', 'missing'])
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None, None
        
        # Ensure string columns are properly quoted
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].astype(str).replace({r'"': '""'}, regex=True)
        
        # Parse dates and numeric columns
        for col in df.columns:
            if 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    # Keep as is if conversion fails
                    pass
        
        # Create a temporary file to save the preprocessed data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_path = temp_file.name
            # Save the DataFrame to the temporary CSV file with quotes around string fields
            df.to_csv(temp_path, index=False, quoting=csv.QUOTE_ALL)
        
        return temp_path, df.columns.tolist(), df  # Return the DataFrame as well
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None, None, None

# Streamlit app
st.title("📊 Data Analyst Agent")

# Sidebar for Auth instructions
with st.sidebar:
    st.header("Google Cloud (Vertex AI)")
    st.info("Ensure you are authenticated via `gcloud auth application-default login` in your terminal.")
    st.success("Configured for project: ai-agents-practice-488122")

# File upload widget
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Preprocess and save the uploaded file
    temp_path, columns, df = preprocess_and_save(uploaded_file)
    
    if temp_path and columns and df is not None:
        # Display the uploaded data as a table
        st.write("Uploaded Data:")
        st.dataframe(df)  # Use st.dataframe for an interactive table
        
        # Display the columns of the uploaded data
        st.write("Uploaded columns:", columns)
        
        # Initialize DuckDbTools
        duckdb_tools = DuckDbTools()
        
        # Load the CSV file into DuckDB as a table
        duckdb_tools.load_local_csv_to_table(
            path=temp_path,
            table="uploaded_data",
        )

            
        # Initialize the Agent with DuckDB and Pandas tools
        data_analyst_agent = Agent(
            model=Gemini(
                id="gemini-2.0-flash-001",
                vertexai=True,
                project_id="ai-agents-practice-488122",
                location="us-central1"
            ),
            tools=[duckdb_tools, PandasTools()],
            system_message='''You are an expert data analyst. Use the 'uploaded_data' table to answer user queries. Generate SQL queries using DuckDB tools to solve the user's query. Provide clear and concise answers with the results.
If the user asks for a chart or visualization, write pure Python code using `st.bar_chart`, `st.line_chart`, `st.scatter_chart`, or `matplotlib` to display it in Streamlit.
You have access to a special function `run_query(query: str)` which executes a SQL query against the DuckDB database and returns a pandas DataFrame. Use this to fetch aggregated data directly without writing complex pandas groupby code on the raw `df` variable.
Enclose the code in triple backticks with "python".
CRITICAL INSTRUCTION: YOU MUST actually write the chart rendering line (e.g. `st.bar_chart(...)`) inside your Python block. Do not just print the dataframe.
CRITICAL INSTRUCTION 2: DO NOT evaluate the truthiness of a dataframe (e.g. DO NOT write `if chart_df:`). Just run the chart command directly, or if you must verify it, use `if not chart_df.empty:`.
CRITICAL INSTRUCTION 3: When writing SQL for the `run_query` function, ALWAYS wrap column names in double quotes (e.g. `"SPECIALTY CODE"` and `"CLAIMS FLAG"`), because columns with spaces in their name will crash the DuckDB SQL parser if unquoted. DO NOT use backticks for SQL column quotes.
For example:
```python
chart_df = run_query('SELECT "Category", SUM("Sales") as Total FROM uploaded_data GROUP BY "Category"')
st.bar_chart(chart_df, x="Category", y="Total")
```
Do not say you cannot create a chart. Respond with the Python code to do it.''',
            markdown=True,
        )
        
        # Initialize code storage in session state
        if "generated_code" not in st.session_state:
            st.session_state.generated_code = None
        
        # Main query input widget
        user_query = st.text_area("Ask a query about the data:")
        
        # Add info message about terminal output
        st.info("💡 Check your terminal for a clearer output of the agent's response")
        
        if st.button("Submit Query"):
            if user_query.strip() == "":
                st.warning("Please enter a query.")
            else:
                try:
                    # Show loading spinner while processing
                    with st.spinner('Processing your query...'):
                        # Get the response from the agent
                        response = data_analyst_agent.run(user_query)

                        # Extract the content from the response object
                        if hasattr(response, 'content'):
                            response_content = response.content
                        else:
                            response_content = str(response)

                    # Display the response in Streamlit
                    st.markdown(response_content)
                    
                    # Extract and execute any Python code blocks
                    code_matches = re.findall(r'```python\n(.*?)\n```', response_content, re.DOTALL)
                    if code_matches:
                        for code in code_matches:
                            st.subheader("Generated Visualization Code:")
                            st.code(code, language="python")
                            
                            try:
                                # Provide the agent's expected tools directly into the generated code's environment!
                                def run_query(query: str):
                                    # DuckDB tool returns a CSV string, we parse it into a Pandas DataFrame
                                    import io
                                    import pandas as pd
                                    result_str = duckdb_tools.run_query(query)
                                    try:
                                        return pd.read_csv(io.StringIO(result_str))
                                    except Exception:
                                        return pd.DataFrame()

                                exec_globals = {
                                    'df': df, 
                                    'st': st, 
                                    'pd': pd, 
                                    'run_query': run_query
                                }
                                exec(code, exec_globals)
                            except Exception as code_e:
                                st.error(f"Error executing the visualization code: {code_e}")
                
                    
                except Exception as e:
                    st.error(f"Error generating response from the agent: {e}")
                    st.error("Please try rephrasing your query or check if the data format is correct.")