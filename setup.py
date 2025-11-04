from setuptools import setup, find_packages

setup(
    name="ai-sales-coach",
    version="1.0.0",
    description="AI Sales Coach Platform",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "openai==1.3.0",
        "chromadb==0.4.15",
        "sqlalchemy==2.0.23",
        "python-dotenv==1.0.0",
        "sentence-transformers==2.2.2",
        "numpy==1.24.3",
        "requests==2.31.0",
        "slowapi==0.1.9",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
    ],
    python_requires=">=3.9,<3.12",
)

