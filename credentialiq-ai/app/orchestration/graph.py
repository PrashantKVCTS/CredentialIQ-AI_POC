"""LangGraph workflow definition for 5-agent pipeline."""

from typing import Any

from langgraph.graph import END, START, StateGraph

from app.agents.credential_verification_agent import CredentialVerificationAgent
from app.agents.license_verification_agent import LicenseVerificationAgent
from app.agents.risk_assessment_agent import RiskAssessmentAgent
from app.agents.sanction_check_agent import SanctionCheckAgent
from app.agents.workflow_agent import WorkflowAgent
from app.orchestration.state import CredentialingState


def build_credentialing_graph() -> Any:
    """Build LangGraph state graph for credentialing orchestrator."""

    agent1 = CredentialVerificationAgent()
    agent2 = LicenseVerificationAgent()
    agent3 = SanctionCheckAgent()
    agent4 = RiskAssessmentAgent()
    agent5 = WorkflowAgent()

    # Node functions wrapping agent executions
    def node_verify_credentials(state: CredentialingState) -> dict:
        return agent1.execute(dict(state))

    def node_verify_licenses(state: CredentialingState) -> dict:
        return agent2.execute(dict(state))

    def node_screen_sanctions(state: CredentialingState) -> dict:
        return agent3.execute(dict(state))

    def node_assess_risk(state: CredentialingState) -> dict:
        return agent4.execute(dict(state))

    def node_workflow_recommendation(state: CredentialingState) -> dict:
        return agent5.execute(dict(state))

    workflow = StateGraph(CredentialingState)

    # Add nodes
    workflow.add_node("verify_credentials", node_verify_credentials)
    workflow.add_node("verify_licenses", node_verify_licenses)
    workflow.add_node("screen_sanctions", node_screen_sanctions)
    workflow.add_node("assess_risk", node_assess_risk)
    workflow.add_node("workflow_recommendation", node_workflow_recommendation)

    # Add edges sequentially
    workflow.add_edge(START, "verify_credentials")
    workflow.add_edge("verify_credentials", "verify_licenses")
    workflow.add_edge("verify_licenses", "screen_sanctions")
    workflow.add_edge("screen_sanctions", "assess_risk")
    workflow.add_edge("assess_risk", "workflow_recommendation")
    workflow.add_edge("workflow_recommendation", END)

    return workflow.compile()
