import yaml
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_config():
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

        # 確保基本結構存在
        if 'app' not in config:
            config['app'] = {
                'name': 'AI Chat',
                'host': '0.0.0.0',
                'port': 8080
            }

        # 確保 API 配置存在
        for api in ['deepseek', 'anthropic', 'openai']:
            if api not in config:
                config[api] = {
                    'url': '',
                    'key': '',
                    'model': ''
                }

        # 從環境變數更新配置
        if os.getenv('DEEPSEEK_API_KEY'):
            config['deepseek']['key'] = os.getenv('DEEPSEEK_API_KEY')
        if os.getenv('DEEPSEEK_API_URL'):
            config['deepseek']['url'] = os.getenv('DEEPSEEK_API_URL')
        if os.getenv('ANTHROPIC_API_KEY'):
            config['anthropic']['key'] = os.getenv('ANTHROPIC_API_KEY')
        if os.getenv('OPENAI_API_KEY'):
            config['openai']['key'] = os.getenv('OPENAI_API_KEY')

        return config
    except Exception as e:
        print(f"載入配置文件時出錯: {e}")
        # 返回默認配置
        return {
            'app': {
                'name': 'AI Chat',
                'host': '0.0.0.0',
                'port': 8080
            },
            'deepseek': {
                'url': os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com'),
                'key': os.getenv('DEEPSEEK_API_KEY', ''),
                'model': 'deepseek-chat'
            },
            'anthropic': {
                'url': os.getenv('ANTHROPIC_API_URL', 'https://api.anthropic.com'),
                'key': os.getenv('ANTHROPIC_API_KEY', ''),
                'model': 'claude-3'
            },
            'openai': {
                'url': os.getenv('OPENAI_API_URL', 'https://api.openai.com'),
                'key': os.getenv('OPENAI_API_KEY', ''),
                'model': 'gpt-4'
            }
        }

def save_config(config):
    try:
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
        return True
    except Exception as e:
        print(f"保存配置文件時出錯: {e}")
        return False

# Create a global config object
config = load_config()
