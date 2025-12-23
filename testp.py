import sys

# Safe version checking
try:
    import bs4
    print(f"BeautifulSoup version: {bs4.__version__}")
except ImportError:
    print("BeautifulSoup is not installed")
except AttributeError:
    try:
        import importlib.metadata
        version = importlib.metadata.version("beautifulsoup4")
        print(f"BeautifulSoup version: {version}")
    except:
        print("BeautifulSoup version: Unable to determine")

print(f"Python version: {sys.version}")