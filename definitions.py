import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config/config.ini')
DOTENV_PATH = os.path.join(ROOT_DIR, '.env')
DESC_FUZZY = 'Enable fuzzy search'
DESC_EXACT_MATCH = 'Enable exact match'
DESC_SKIP = 'Skipped, setting default value'
DESC_DB_QUERY = 'DB Query '
DESC_CPU = 'CPU usage is '
DESC_MEMORY = 'MEM usage is '
DESC_TAG_404 = 'Tag not found'
DESC_404 = 'Not Found'
DESC_BRAND_404 = 'Brand not found'
DESC_CATEGORY_404 = 'Category not found'
