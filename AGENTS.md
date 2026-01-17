# AGENTS.md - Development Guidelines for Bot-Telegram

This file contains essential information for AI agents working on the bot-telegram codebase. Follow these guidelines to maintain consistency and quality.

## Build, Lint, Test Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the bot
python -m src.main
```

### Testing Commands
```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=xml

# Run a specific test file
pytest tests/unit/test_pdf_parser.py -v

# Run a specific test function
pytest tests/unit/test_pdf_parser.py::TestPDFParser::test_extract_date_spanish_format -v

# Run tests in verbose mode with short traceback
pytest tests/ -v --tb=short
```

### Linting and Formatting
```bash
# Check linting (includes formatting check)
ruff check src/

# Auto-fix linting issues
ruff check src/ --fix

# Check formatting only
ruff format --check src/

# Auto-format code
ruff format src/
```

### Type Checking
```bash
# Run MyPy type checking
mypy src/
```

### Code Quality Checks
```bash
# Run pre-commit quality checks (recommended before committing)
python pre-commit-checks.py

# Format code
ruff format src/

# Check formatting without fixing
ruff format --check src/

# Run linting
ruff check src/

# Auto-fix linting issues
ruff check --fix src/

# Run type checking
mypy src/
```

### Pre-commit Workflow
Before committing changes, always run the quality checks:

```bash
# 1. Stage your changes
git add .

# 2. Run quality checks
python pre-commit-checks.py

# 3. If checks fail, fix issues and restage
# 4. Commit when all checks pass
git commit -m "your message"
```

The pre-commit script will:
- ✅ Check code formatting with Ruff
- ✅ Run linting checks
- ✅ Report any issues that need to be fixed
- ✅ Allow commit only when all checks pass

### Full Quality Check
```bash
# Run all checks (used in CI)
ruff check src/ && ruff format --check src/ && mypy src/ && pytest tests/ -v --cov=src
```

## Code Style Guidelines

### General Principles
- **Language**: Python 3.11+
- **Line Length**: 100 characters (enforced by Ruff)
- **Encoding**: UTF-8
- **Documentation**: All functions, classes, and modules must have docstrings
- **Type Hints**: Use comprehensive type hints throughout
- **Async/Await**: Use async patterns consistently for I/O operations
- **Error Handling**: Implement proper exception handling with logging
- **Logging**: Use structured logging for all operations

### Imports
```python
# Standard library imports first
import asyncio
from datetime import date, datetime

# Third-party imports (alphabetically sorted by isort)
from telegram import Update
from telegram.ext import ContextTypes

# Local imports (with src. prefix)
from src.database.engine import get_session_factory
from src.utils.logging import get_logger
```

### Naming Conventions
- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Modules**: `snake_case`
- **Private members**: `_leading_underscore`

### Type Hints
```python
# Use modern typing syntax
from typing import Any, Dict, List, Optional

# For SQLAlchemy models, use Mapped types
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

# Function signatures
async def process_user(user_id: int) -> Optional[User]:
    pass

# Complex types
def get_users(ids: List[int]) -> Dict[int, User]:
    pass
```

### Docstrings
```python
def calculate_total(items: List[Dict[str, Any]]) -> float:
    """
    Calculate total value from a list of items.

    Args:
        items: List of item dictionaries containing 'price' and 'quantity' keys.

    Returns:
        Total calculated value as a float.

    Raises:
        ValueError: If an item is missing required keys or has invalid values.
    """
    pass

class Competition(Base):
    """
    Competición de atletismo.

    Representa una competición completa con su PDF asociado.
    """
    pass
```

### Async Patterns
```python
# Always use async context managers for database sessions
async def get_competition(competition_id: int) -> Optional[Competition]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        repo = CompetitionRepository(session)
        return await repo.get_by_id(competition_id)

# Proper error handling in async functions
async def send_notification(user_id: int, message: str) -> bool:
    try:
        # Async operation
        await bot.send_message(chat_id=user_id, text=message)
        return True
    except Exception as e:
        logger.error(f"Failed to send notification to {user_id}: {e}")
        return False
```

### Database Operations
```python
# Use repositories for data access
class CompetitionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_upcoming(self) -> List[Competition]:
        stmt = select(Competition).where(Competition.competition_date >= date.today())
        result = await self.session.execute(stmt)
        return list(result.scalars())

# Always use transactions for writes
async def create_competition(competition: Competition) -> Competition:
    async with session_factory() as session:
        async with session.begin():
            session.add(competition)
            await session.flush()  # Get the ID
            await session.refresh(competition)
            return competition
```

### Error Handling
```python
# Use specific exception types
try:
    result = await parse_pdf(pdf_content)
except PDFParseError as e:
    logger.error(f"Failed to parse PDF: {e}")
    raise CompetitionParseError(f"Invalid PDF format: {e}") from e
except Exception as e:
    logger.error(f"Unexpected error parsing competition: {e}")
    raise

# Log errors with context
async def scrape_competitions() -> List[Competition]:
    try:
        competitions = await scraper.scrape_all()
        logger.info(f"Successfully scraped {len(competitions)} competitions")
        return competitions
    except ScraperError as e:
        logger.error(f"Scraping failed: {e}", extra={"component": "scraper"})
        raise
```

### Logging
```python
# Use structured logging with context
logger = get_logger(__name__)

def process_competition(competition: Competition) -> None:
    logger.info(
        "Processing competition",
        extra={
            "competition_id": competition.id,
            "competition_date": competition.competition_date.isoformat(),
            "event_count": len(competition.events)
        }
    )

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.debug("Detailed debug information")
logger.info("General information about operation")
logger.warning("Warning about potential issues")
logger.error("Error that doesn't stop execution")
logger.critical("Critical error requiring immediate attention")
```

### Testing Patterns
```python
# Use descriptive test names
class TestPDFParser:
    def test_extract_date_spanish_format(self):
        """Test extracción de fecha en formato español."""
        parser = PDFParser()
        text = "Fecha: 11 de enero de 2026"

        result = parser._extract_date(text)

        assert result is not None
        assert result.day == 11
        assert result.month == 1
        assert result.year == 2026

# Use fixtures for common setup
@pytest.fixture
async def db_session():
    """Provide a test database session."""
    session_factory = get_test_session_factory()
    async with session_factory() as session:
        yield session

# Use mocking for external dependencies
async def test_send_notification_success(self, mocker):
    """Test successful notification sending."""
    mock_bot = mocker.AsyncMock()
    mocker.patch('src.notifications.service.bot', mock_bot)

    result = await send_notification(123, "Test message")

    assert result is True
    mock_bot.send_message.assert_called_once_with(chat_id=123, text="Test message")
```

### File Organization
```
src/
├── bot/               # Telegram bot handlers and keyboards
├── database/          # Models, repositories, and database setup
├── notifications/     # Notification service and formatting
├── scraper/          # Web scraping and PDF parsing
├── scheduler/        # Background jobs and scheduling
├── utils/            # Shared utilities (logging, hashing, etc.)
├── config.py         # Configuration management
└── main.py           # Application entry point

tests/
├── unit/             # Unit tests for individual components
└── integration/      # Integration tests (if any)
```

### Configuration
```python
# Use Pydantic for configuration validation
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    admin_user_id: int = Field(..., env="ADMIN_USER_ID")
    database_url: str = Field("sqlite+aiosqlite:///./data/bot.db", env="DATABASE_URL")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Security Considerations
- Never log sensitive information (tokens, passwords, user data)
- Use environment variables for secrets
- Validate all user inputs
- Use parameterized queries to prevent SQL injection
- Handle exceptions gracefully without exposing internal details

### Performance Guidelines
- Use async operations for I/O bound tasks
- Implement proper database indexing
- Use connection pooling for database operations
- Cache expensive operations when appropriate
- Profile performance-critical code paths

### Commit Messages
Follow conventional commit format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example: `feat: add competition search by date`

### Pull Request Guidelines
- Ensure all tests pass
- Run full linting and type checking
- Update documentation if needed
- Add tests for new features
- Keep PRs focused on a single feature or fix
- Use descriptive PR titles and descriptions

This document should be updated as the codebase evolves and new patterns emerge.