import os

# ===== Paths =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EMBEDDINGS_DIR = os.path.join(BASE_DIR, 'embeddings')

# Data files
RECIPES_CSV = os.path.join(DATA_DIR, 'thai_food_processed.csv')
NUTRITION_CSV = os.path.join(DATA_DIR, 'nutrition.csv')

# Embeddings files
EMBEDDINGS_NAME_PATH = os.path.join(EMBEDDINGS_DIR, 'embeddings_name.pkl')
EMBEDDINGS_INGREDIENT_PATH = os.path.join(EMBEDDINGS_DIR, 'embeddings_ingredient.pkl')

# ===== Model Settings =====
DEFAULT_MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

# ===== Search Settings =====
DEFAULT_TOP_K = 5
DEFAULT_MIN_SIMILARITY = 0.3
DEFAULT_EXACT_MATCH_THRESHOLD = 0.95

# ===== UI Settings =====
PAGE_TITLE = "ระบบค้นหาสูตรอาหารตามโภชนาการ"
PAGE_ICON = "🍽️"

# ===== Create directories if not exist =====
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)