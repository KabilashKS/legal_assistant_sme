Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Use uv python manager instead of pip. It is fast and better then pip.
- First install the uv on your windows or linux and mac OS
  - For windows run this comand on your terminal:
        - powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  
  - for linux and mac run this comand on your terminal:
        - curl -LsSf https://astral.sh/uv/install.sh | sh

  - Once the download was complete and then initiate the uv by this command inside your project directory:
        - uv init     
  
  - Any queries in installation refer this document page:
        - https://docs.astral.sh/uv/getting-started/installation/ 


### Step-1

### Installation

1.**Clone the repository**
```bash
    git clone https://github.com/yourusername/legal-assistant-sme.git
    cd legal-assistant-sme

### Step-2

#OpenAI API Setup (Optional for Enhanced Features)

    1.Get your API key from OpenAI Platform

    2.Add it in the app sidebar under "API Configuration"

    3.Enable real AI analysis for detailed insights

#Environment Variables

Create a .env file in the root directory:    

OPENAI_API_KEY=your_api_key_here
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

### Step-3

Create a virtual environment 
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

### Step-4

#Install dependencies
pip install -r requirements.txt

### Step-5
#Run the application
streamlit run app.py

### Step-6
Open your browser and navigate to http://localhost:8501

Usage Guide
Step 1: Upload Your Contract

    Click "Upload Contract" in the sidebar

    Supported formats: PDF, Word (.docx, .doc), Text (.txt)

    Or paste contract text directly in the text area

    Try the "Load Sample Contract" button for a demo

Step 2: Run AI Analysis

    Click "🤖 Run Detailed AI Analysis" button

    Wait for the AI to process each clause

    View progress with the progress bar

Step 3: Review Results

    📊 Overview Tab: See contract metrics and overall risk

    🔍 Analysis Tab: Detailed clause-by-clause breakdown

    ⚠️ Risks Tab: Comprehensive risk assessment

    📄 Report Tab: Generate and download reports

Step 4: Take Action

    Download comprehensive reports

    Use negotiation strategies provided

    Consult with legal professionals using the analysis


### Technical Details

#Document Processing

# Key components:
- PyPDF2: PDF text extraction
- python-docx: Word document processing
- Custom clause segmentation algorithms
- Text cleaning and normalization

# AI Analysis Engine

# Risk detection patterns:
- Foreign jurisdiction detection
- Unlimited liability identification
- Arbitrary termination flags
- Indefinite confidentiality alerts
- Unreasonable penalty clause detection


### Security & Privacy

## Data Protection

    ✅ No contract data stored permanently

    ✅ All processing happens in memory

    ✅ Optional OpenAI API with user consent

    ✅ No third-party data sharing

## Best Practices

    Always use HTTPS in production

    Keep API keys secure in environment variables

    Regular dependency updates

    Input validation and sanitization

## Deployment

## Deploy on Streamlit Cloud

    Push your code to GitHub

    Visit share.streamlit.io

    Connect your repository

    Set environment variables

    Deploy!