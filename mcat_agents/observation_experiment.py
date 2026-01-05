import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_framework.devui import serve
from dotenv import load_dotenv

from mcat_agents.agents import helper_agent

load_dotenv()


def main():
    serve(entities=[helper_agent])


if __name__ == "__main__":
    main()