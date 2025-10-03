# FinalProject
1. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows

2. Install dependencies:
   pip install -r requirements.txt

3. Start the FastAPI backend (run this in one terminal):
   uvicorn main:app --reload --port 8000

4. Start the simulator (optional, run in another terminal):
   python ingest_simulator.py

5. Run the dashboard (in another terminal):
   streamlit run streamlit_app.py

Open the Streamlit dashboard (usually http://localhost:8501). The dashboard fetches data from the FastAPI server at http://localhost:8000.
