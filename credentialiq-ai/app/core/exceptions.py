"""Custom application exceptions."""


class CredentialIQException(Exception):
    """Base exception for CredentialIQ AI."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class CaseNotFoundError(CredentialIQException):
    """Raised when a credentialing case is not found."""

    def __init__(self, case_id: str):
        super().__init__(f"Case with ID '{case_id}' not found.", code="CASE_NOT_FOUND")
        self.case_id = case_id


class InvalidCaseStateError(CredentialIQException):
    """Raised when an operation is invalid for the current case state."""

    def __init__(self, message: str):
        super().__init__(message, code="INVALID_CASE_STATE")


class ConnectorError(CredentialIQException):
    """Raised when a verification connector fails."""

    def __init__(self, connector_name: str, details: str):
        super().__init__(
            f"Connector '{connector_name}' error: {details}",
            code="CONNECTOR_ERROR",
        )
        self.connector_name = connector_name


class RAGRepositoryError(CredentialIQException):
    """Raised when policy retrieval fails."""

    def __init__(self, details: str):
        super().__init__(f"RAG Repository error: {details}", code="RAG_ERROR")


class LLMServiceError(CredentialIQException):
    """Raised when language model service fails."""

    def __init__(self, details: str):
        super().__init__(f"LLM Service error: {details}", code="LLM_ERROR")
