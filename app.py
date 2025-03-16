from flask import Flask, render_template, request, Response, jsonify
import requests
import json
from flask_cors import CORS
from config import config, save_config
import os

app = Flask(__name__)
CORS(app)  # 啟用CORS支援

# 使用設定
api_key = config.get('deepseek', {}).get('key', '')
api_url = config.get('deepseek', {}).get('url', '')
app_name = config.get('app', {}).get('name', 'AI Chat')

@app.route('/models', methods=['GET'])
def get_models():
    try:
        all_models = []

        # 從設定中獲取 API 模型
        api_models = config.get('models', [])
        if not api_models:
            # 如果設定中沒有模型，添加默認的 API 模型
            default_api_model = {
                'name': 'deepseek-chat',
                'display_name': 'Deepseek Chat',
                'type': 'api',
                'temperature': 0.7,
                'max_tokens': 2000
            }
            api_models = [default_api_model]

        all_models.extend(api_models)

        # 獲取本地 Ollama 模型
        try:
            ollama_response = requests.get('http://localhost:11434/api/tags')
            if ollama_response.status_code == 200:
                ollama_models = ollama_response.json().get('models', [])
                # 將 Ollama 模型轉換為我們的格式
                local_models = [{
                    'name': model['name'],
                    'display_name': model['name'].split(':')[0].title(),
                    'type': 'local',
                    'temperature': 0.7,
                    'max_tokens': 2000
                } for model in ollama_models]
                all_models.extend(local_models)
        except:
            pass  # 如果無法獲取本地模型，就忽略錯誤

        return jsonify({'models': all_models})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        model_name = data.get('model', 'deepseek-chat')
        # 獲取對話歷史
        conversation_history = data.get('conversation_history', [])
        # 獲取圖片數據
        image_data = data.get('image')

        # 檢查是否是本地模型
        if ':' in model_name:  # Ollama 模型通常包含冒號，如 mistral:7b
            model_config = {
                'type': 'local',
                'name': model_name
            }
        else:
            # API 模型
            model_config = {
                'type': 'api',
                'name': model_name
            }

        # 系統提示
        system_prompt = "請遵循以下規則：1. 永遠使用繁體中文回答2. 保持專業、友善的語氣3. 如果需要顯示代碼，請保持原本的語言"

        def generate():
            if model_config['type'] == 'api':
                # DeepSeek API
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                }

                # 構建完整的消息歷史
                messages = [{"role": "system", "content": system_prompt}]

                # 添加之前的對話歷史（最多保留最近的10條消息，避免超出上下文限制）
                if conversation_history:
                    # 只保留最近的對話，避免超出上下文限制
                    recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
                    messages.extend(recent_history)
                else:
                    # 如果沒有對話歷史，只添加當前用戶消息
                    user_message = {"role": "user", "content": prompt}
                    if image_data:
                        user_message["image"] = image_data
                    messages.append(user_message)

                payload = {
                    'model': model_name,
                    'messages': messages,
                    'stream': True
                }

                response = requests.post(
                    f'{api_url}/chat/completions',
                    headers=headers,
                    json=payload,
                    stream=True
                )

                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8').replace('data: ', ''))
                            if chunk.get('choices') and chunk['choices'][0].get('delta', {}).get('content'):
                                content = chunk['choices'][0]['delta']['content']
                                yield f"data: {json.dumps({'response': content})}\n\n"
                        except json.JSONDecodeError:
                            continue

            else:
                # 本地 Ollama 模型
                # 構建包含對話歷史的完整提示
                full_prompt = system_prompt + "\n\n"

                # 添加對話歷史
                if conversation_history:
                    # 只保留最近的對話，避免超出上下文限制
                    recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
                    for msg in recent_history:
                        role = "用戶" if msg["role"] == "user" else "助手"
                        content = msg["content"]
                        if msg["role"] == "user" and "image" in msg:
                            content = f"[用戶上傳了一張圖片]\n{content}" if content else "[用戶上傳了一張圖片]"
                        full_prompt += f"{role}: {content}\n\n"

                # 添加當前問題
                current_prompt = prompt
                if image_data:
                    current_prompt = f"[用戶上傳了一張圖片]\n{current_prompt}" if current_prompt else "[用戶上傳了一張圖片]"
                full_prompt += f"用戶: {current_prompt}\n\n助手: "

                # 準備 Ollama API 請求
                ollama_request = {
                    'model': model_name,
                    'prompt': full_prompt,
                    'stream': True
                }

                # 如果有圖片，添加到請求中
                if image_data:
                    ollama_request['images'] = [image_data]

                response = requests.post(
                    'http://localhost:11434/api/generate',
                    json=ollama_request,
                    stream=True
                )

                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'response' in chunk:
                                # 將 Ollama 的回應格式轉換為與 DeepSeek API 相同的格式
                                yield f"data: {json.dumps({'response': chunk['response']})}\n\n"
                        except json.JSONDecodeError:
                            continue

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'發生錯誤: {str(e)}'
        }), 500

@app.route('/settings')
def settings_page():
    return render_template('settings.html', config=config)

@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        # 只返回 API 相關的設定
        settings = {
            'deepseek': config.get('deepseek', {}),
            'anthropic': config.get('anthropic', {}),
            'openai': config.get('openai', {})
        }
        return jsonify(settings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    try:
        new_settings = request.json

        # 更新每個 API 的設定
        for api in ['deepseek', 'anthropic', 'openai']:
            if api in new_settings:
                if api not in config:
                    config[api] = {}
                config[api].update({
                    'url': new_settings[api]['url'],
                    'key': new_settings[api]['key'],
                    'model': new_settings[api]['model']
                })

        # 保存到 config.yaml
        save_config(config)

        # 更新全局變量
        global api_key, api_url
        api_key = config.get('deepseek', {}).get('key', '')
        api_url = config.get('deepseek', {}).get('url', '')

        return jsonify({'success': True, 'message': '設定已更新'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test-model', methods=['POST'])
def test_model():
    try:
        data = request.json
        api_type = data.get('api_type', 'deepseek')
        model_name = data['model']
        api_key = data['api_key']
        api_url = data['api_url']

        # 根據不同的 API 類型使用不同的請求格式
        if api_type == 'anthropic':
            headers = {
                'x-api-key': api_key,
                'content-type': 'application/json',
            }
            payload = {
                'model': model_name,
                'messages': [{'role': 'user', 'content': '你好，這是一個測試訊息'}],
            }
        elif api_type == 'openai':
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }
            payload = {
                'model': model_name,
                'messages': [{'role': 'user', 'content': '你好，這是一個測試訊息'}],
            }
        else:  # deepseek
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }
            payload = {
                'model': model_name,
                'messages': [
                    {'role': 'system', 'content': '請用繁體中文簡短回答'},
                    {'role': 'user', 'content': '你好，這是一個測試訊息'}
                ],
            }

        # 發送測試請求
        response = requests.post(
            f'{api_url}/chat/completions',
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            content = None
            if api_type == 'anthropic':
                content = result.get('content', [{}])[0].get('text')
            elif api_type == 'openai':
                content = result.get('choices', [{}])[0].get('message', {}).get('content')
            else:  # deepseek
                content = result.get('choices', [{}])[0].get('message', {}).get('content')

            if content:
                return jsonify({
                    'success': True,
                    'response': content
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '無法獲取模型回應'
                })
        else:
            return jsonify({
                'success': False,
                'error': f'API 返回錯誤: {response.status_code}'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'發生錯誤: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
