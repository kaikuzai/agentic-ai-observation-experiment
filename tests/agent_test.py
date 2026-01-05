from agent_framework.devui import serve 
from pathlib import Path 
import sys 

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcat_agents.agents.resource_agent import resource_agent
from mcat_agents.agents.knowledge_agent import knowledge_agent
from mcat_agents.agents.helper_agent import helper_agent
from mcat_agents.agents.network_agent import network_agent 

def main():
    serve(entities=[resource_agent, knowledge_agent, helper_agent, network_agent])

if __name__ == '__main__':
    main()