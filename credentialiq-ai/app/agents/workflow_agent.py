"""Agent 5: Workflow Agent."""

from datetime import datetime, timedelta
from typing import Any

from app.agents.base import BaseAgent
from app.core.enums import AuditEventType, RecommendationType, RiskLevel
from app.schemas.responses import WorkflowRecommendationResponse


class WorkflowAgent(BaseAgent):
    """Formulates workflow recommendations, action items, and review schedules."""

    def __init__(self):
        super().__init__(name="WorkflowAgent")

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Formulate workflow recommendation based on risk assessment."""
        risk_data = state.get("risk_assessment", {})
        risk_level_str = risk_data.get("risk_level", "Clean")
        risk_level = RiskLevel(risk_level_str)

        action_items: list[str] = []
        now = datetime.utcnow()

        if risk_level == RiskLevel.CLEAN:
            recommendation = RecommendationType.AUTO_APPROVE
            requires_committee = False
            next_review = (now + timedelta(days=730)).strftime("%Y-%m-%d")  # 2 years NCQA standard
            rationale = (
                "Automated approval recommended. Provider meets all NCQA primary source license "
                "and sanction screening standards without exceptions."
            )
            action_items.append("Issue network participation agreement.")
            action_items.append("Schedule re-credentialing in 24 months.")

        elif risk_level == RiskLevel.EXCEPTION:
            recommendation = RecommendationType.COMMITTEE_REVIEW
            requires_committee = True
            next_review = (now + timedelta(days=30)).strftime("%Y-%m-%d")
            rationale = (
                "Routed to Credentialing Committee for peer review due to credentialing exceptions "
                "(e.g., past expired license, administrative board inquiry, or lack of board certification)."
            )
            action_items.append("Prepare case packet for monthly Credentialing Committee agenda.")
            action_items.append("Request written explanation from provider regarding board inquiry.")

        else:  # HOLD
            recommendation = RecommendationType.DENY
            requires_committee = True
            next_review = None
            rationale = (
                "Recommendation for Network Denial / Participation Exclusion. Active federal sanctions "
                "or state medical license suspensions detected."
            )
            action_items.append("Flag provider in health plan credentialing registry as Excluded.")
            action_items.append("Issue formal Notice of Adverse Credentialing Decision.")

        recommendation_resp = WorkflowRecommendationResponse(
            recommendation=recommendation,
            rationale=rationale,
            action_items=action_items,
            requires_committee_approval=requires_committee,
            next_review_due_date=next_review,
        )

        audit_logs = list(state.get("audit_logs", []))
        audit_logs.append(
            {
                "event_type": AuditEventType.WORKFLOW_RECOMMENDED.value,
                "agent_name": self.name,
                "details": {
                    "recommendation": recommendation.value,
                    "requires_committee": requires_committee,
                    "action_items_count": len(action_items),
                },
            }
        )

        return {
            "workflow_recommendation": recommendation_resp.model_dump(),
            "final_status": risk_level_str,
            "audit_logs": audit_logs,
        }
