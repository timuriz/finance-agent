from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
TEST1_DATA_PATH = os.environ["TEST1_DATA_PATH"]