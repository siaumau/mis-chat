# AI 對話介面 | AI Chat Interface

## 專案簡介 | Introduction
這是一個支援多模型的 AI 對話介面，可同時使用 API 模型（如 DeepSeek）和本地模型（如 Ollama），提供了簡潔的使用者界面和即時回應功能。

## 功能特點 | Features
### 多模型支援 | Multiple Model Support
- 支援 DeepSeek API 模型 | DeepSeek API models
- 支援本地 Ollama 模型 | Local Ollama models
- 可在設定頁面中管理 API 模型 | API model management in settings
- 自動檢測並載入本地可用模型 | Auto-detect local models

### 聊天介面 | Chat Interface
- 即時串流回應 | Real-time streaming responses
- Markdown 格式支援 | Markdown support
  - 粗體 (`**text**` 或 `__text__`) | Bold text
  - 斜體 (`*text*` 或 `_text_`) | Italic text
  - 行內程式碼 (`` `text` ``) | Inline code
  - 標題 (`# Heading`) | Headers
  - 無序列表 (`- item` 或 `* item`) | Unordered lists
  - 有序列表 (`1. item`) | Ordered lists
- 程式碼區塊顯示 | Code block display
  - 自動語言識別 | Auto language detection
  - 語法高亮 | Syntax highlighting
  - 保持原始格式 | Original format preservation
- 表格顯示 | Table display
- 聊天歷史記錄 | Chat history
- 新對話功能 | New chat function

### 設定功能 | Settings
- API 設定 | API Settings
  - API URL 配置 | API URL configuration
  - API Key 管理 | API key management
- 模型管理 | Model Management
  - 新增/刪除 API 模型 | Add/Remove API models
  - 設定模型參數 | Model parameter configuration
  - 測試模型連線 | Model connection testing
- 應用程式設定 | App Settings
  - 自定義應用名稱 | Custom app name

## 技術規格 | Technical Specifications
- Python Flask
- Tailwind CSS
- Server-Sent Events (SSE)
- 響應式設計 | Responsive design

## 安裝需求 | Requirements
- Python 3.8+
- Flask
- Requests
- Flask-CORS
- PyYAML
- python-dotenv
- Ollama (選用，用於本地模型) | Optional for local models

## 安裝步驟 | Installation
1. 安裝依賴套件 | Install dependencies
```bash
pip install -r requirements.txt
```

2. 設定環境變數 | Set environment variables
- 複製 `.env.example` 為 `.env`
- 填入您的 API 金鑰和其他設定

3. 啟動應用 | Start application
- Windows：執行 `setup.bat`
- Linux/Mac：執行 `setup.sh`

4. 在瀏覽器中訪問 | Access in browser
```
http://localhost:8080
```

## 配置文件 | Configuration
### config.yaml
```yaml
api:
  key: your-api-key
  url: https://api.example.com
app:
  name: AI Chat
  host: 0.0.0.0
  port: 8080
models:
  - name: model-name
    display_name: Model Display Name
    type: api
    temperature: 0.7
    max_tokens: 2000
```

## 專案結構 | Project Structure
```
project/
├── app.py              # Flask 應用主程式
├── config.py           # 配置處理模組
├── templates/          # HTML 模板
│   ├── index.html     # 主要介面模板
│   └── settings.html  # 設定頁面模板
├── setup.bat          # Windows 啟動腳本
├── setup.sh           # Linux/Mac 啟動腳本
├── config.yaml        # 配置文件
├── requirements.txt   # 依賴套件清單
├── .env              # 環境變數
└── README.md         # 專案說明文件
```

## 更新日誌 | Version History
### 2024-02-26
- 改進程式碼塊顯示功能 | Improved code block display
- 新增 Markdown 格式支援 | Added Markdown support
- 優化文本格式化處理 | Optimized text formatting
- 修復特殊字符顯示問題 | Fixed special character display

### 2024-02-25
- 新增本地模型支援 | Added local model support
- 新增模型測試功能 | Added model testing feature
- 改進設定頁面介面 | Improved settings page UI

## 問題排解 | Troubleshooting
如果遇到問題，請檢查：
1. API 金鑰和 URL 是否正確配置
2. 本地模型使用時，確認 Ollama 服務是否運行中
3. 檢查網路連接狀態
4. 查看應用日誌以獲取詳細錯誤信息
