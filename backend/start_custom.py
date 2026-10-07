import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)

# Load from root .env first, then backend .env (root takes priority)
env_path = os.path.join(backend_dir, '.env')
for env_file in [os.path.join(root_dir, '.env'), env_path]:
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip("'\"")
                    os.environ[key] = value

os.environ['WEBUI_SECRET_KEY'] = 'hq2G10439w1HR59FYQF0jn7U'
os.environ['WEBUI_JWT_SECRET_KEY'] = 'hq2G10439w1HR59FYQF0jn7U'
os.environ['OFFLINE_MODE'] = 'True'

from open_webui.main import app
import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8080)
