
from pathlib import Path

# 除外するディレクトリのリスト
EXCLUDE_DIRS = [
    # バージョン管理システム
    ".git", ".svn", ".hg",
    # 仮想環境とパッケージ管理
    ".venv", "venv", "node_modules",
    # Python関連
    "__pycache__", "*.egg-info", ".mypy_cache", ".pytest_cache", ".tox",
    # IDE・エディタ設定
    ".idea", ".vscode", ".vs",
    # ビルド・キャッシュディレクトリ
    "build", "dist", ".cache", ".coverage",
    # フレームワーク固有
    ".serverless", ".terraform", ".stack-work", ".next", ".nuxt",".svelte-kit",
    # その他
    ".DS_Store", "migrations", ".gradle","locale","*secret*",
]


EXCLUDE_FILES = [
    "*.pyc", "*.pyo", "__pycache__", ".DS_Store", "Thumbs.db",
    "*.swp", "*.swo", "*~", ".vscode", ".idea",
    "build", "dist", "*.egg-info", "*.log", "*.bak",
    ".cache", "venv", "env", ".env", "node_modules",
    ".git", ".svn", ".hg", "local_settings.py",
    "*.pem", "*.key", "*.sqlite3", "*.db",
    "*.min.js", "*.min.css","summary.config.json",
]

# デフォルトの出力ファイル名
DEFAULT_OUTPUT_FILENAME = "summary.md"

# デフォルトのターゲットファイル
DEFAULT_TARGET_FILES = ["README.md","Dockerfile","docker-compose.yml","requirements.txt","package.json","svelte.config.js","tsconfig.json","*.config.ts","manifest.json"]

# サポートするファイル拡張子
SUPPORTED_EXTENSIONS = [
    ".md", ".html", ".css", ".txt", ".json", ".yml", ".yaml",
    ".py", ".ts", ".js", ".java", ".cpp", ".c", ".h", ".hpp",
    ".rb", ".php", ".go", ".rs", ".swift", ".kt", ".scala",
    ".sql", ".sh", ".bat", ".ps1", ".xml", ".csv", ".ini",
    ".conf", ".toml", ".jsx", ".tsx", ".vue",".svelte", ".sass", ".scss"
]

# デフォルトの出力ディレクトリ
DEFAULT_OUTPUT_DIR = Path.home() / "Desktop"