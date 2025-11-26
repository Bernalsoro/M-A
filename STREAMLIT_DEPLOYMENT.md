# 🚀 Deploying Financial RAG Agent to Streamlit Cloud

## 📋 Files Required for Streamlit Deployment

Make sure these files are in your repository root:

```
M-A/
├── streamlit_app.py              # Main Streamlit application
├── requirements_streamlit.txt    # Python dependencies
├── .streamlit/
│   └── config.toml              # Streamlit configuration
├── packages.txt                  # System packages (if needed)
└── financial-rag-agent/         # Your project code
    └── src/
        └── financial_rag_agent/
            ├── data/
            │   ├── sample_financials.csv
            │   └── sample_news.json
            ├── agents/
            ├── retrieval/
            ├── llm/
            └── ...
```

## 🌐 Deployment Steps

### Option 1: Deploy from GitHub (Recommended)

1. **Push to GitHub**
   ```bash
   git add streamlit_app.py requirements_streamlit.txt .streamlit/
   git commit -m "Add Streamlit deployment files"
   git push
   ```

2. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Click "New app"
   - Select your repository: `Bernalsoro/M-A`
   - Set main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Optional: Add Secrets (for real LLM responses)**
   - In Streamlit Cloud dashboard, click "⚙️ Settings"
   - Go to "Secrets"
   - Add:
     ```toml
     OPENAI_API_KEY = "your-key-here"
     # OR
     ANTHROPIC_API_KEY = "your-key-here"
     LLM_PROVIDER = "openai"
     ```

### Option 2: Local Testing

```bash
# Navigate to project root
cd /home/user/M-A

# Install dependencies
pip install -r requirements_streamlit.txt

# Run Streamlit locally
streamlit run streamlit_app.py
```

## 📦 What Gets Installed

The `requirements_streamlit.txt` includes:

- **streamlit** - Web framework
- **pandas, numpy** - Data processing
- **sentence-transformers** - Embeddings
- **faiss-cpu** - Vector search
- **openai, anthropic** - LLM clients (optional)
- **pydantic** - Validation

## ⚠️ Important Notes

### 1. **Mock Mode vs. Real LLM**

**Without API Keys** (Default):
- App works but uses mock responses
- Shows message: "⚠️ LLM not configured. Using mock responses."
- Good for demo/testing

**With API Keys**:
- Real AI-generated responses
- Add keys in Streamlit Cloud Secrets

### 2. **Memory Limits**

Streamlit Cloud free tier has memory limits (~1GB). The app is optimized:
- Uses `faiss-cpu` (smaller than GPU version)
- Caches vector store with `@st.cache_resource`
- Uses lightweight embedding model

### 3. **First Load Time**

First time loading may take 1-2 minutes:
- Downloading embedding model (~80MB)
- Building vector store
- Subsequent loads are much faster (cached)

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'financial_rag_agent'"

**Fix:** Make sure `financial-rag-agent/src/` directory structure is correct in your repo.

### Error: "Cannot load data files"

**Fix:** Ensure these files exist:
- `financial-rag-agent/src/financial_rag_agent/data/sample_financials.csv`
- `financial-rag-agent/src/financial_rag_agent/data/sample_news.json`

### Error: "Memory limit exceeded"

**Fix:**
1. Use smaller embedding model (already using smallest)
2. Reduce number of documents in vector store
3. Consider Streamlit Cloud paid tier

### App is slow

**Normal on first load:**
- Downloading models: 30-60 seconds
- Building vector store: 10-20 seconds
- After that, should be fast (cached)

## 🎨 Customization

### Change Theme

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor="#YOUR_COLOR"
backgroundColor="#FFFFFF"
```

### Modify Layout

Edit `streamlit_app.py`:
- Change `layout="wide"` to `layout="centered"`
- Modify CSS in the `st.markdown()` section
- Adjust sidebar content

## 📊 Features

The deployed app includes:

✅ **Interactive UI**
- Ticker selection dropdown
- Question text area
- Example questions sidebar

✅ **Real-time Analysis**
- Agent planning visualization
- Tool execution tracking
- Retrieved documents display

✅ **Responsive Design**
- Works on mobile and desktop
- Clean, professional interface

✅ **Error Handling**
- Graceful degradation without API keys
- Clear error messages
- Debug mode in expanders

## 🔐 Security Notes

- **Never commit `.env` files** with real API keys
- Use Streamlit Secrets for production keys
- The app runs in sandbox mode on Streamlit Cloud
- Data stays in your Streamlit Cloud instance

## 📈 Monitoring

In Streamlit Cloud dashboard:
- View real-time logs
- Monitor resource usage
- See visitor analytics
- Manage secrets

## 🆘 Support

If issues persist:
1. Check Streamlit Cloud logs (click "Manage app")
2. Review this README
3. Test locally first
4. Check Streamlit docs: https://docs.streamlit.io/

## ✅ Deployment Checklist

Before deploying:
- [ ] All required files in repo root
- [ ] `requirements_streamlit.txt` is correct
- [ ] Data files exist in `financial-rag-agent/src/financial_rag_agent/data/`
- [ ] Tested locally with `streamlit run streamlit_app.py`
- [ ] Pushed to GitHub
- [ ] (Optional) Added API keys to Streamlit Secrets

Ready to deploy! 🚀
