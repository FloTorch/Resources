"""Main service for Digital Twin application."""

from typing import Dict, Any, Optional, List

from .config import ConfigurationManager, CompanyConfiguration
from ..agents.manager import StrandsAgentManager


class DigitalTwinService:
    """Main service for the Digital Twin application."""

    def __init__(self) -> None:
        """Initialize the service.
        
        Args:
            aws_region: AWS region for service initialization
        """
        self._config_manager = ConfigurationManager()
        self._agent_manager = StrandsAgentManager()

    def process_query(
        self,
        company_key: str,
        user_query: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user query for a company.
        
        Args:
            company_key: Unique identifier for the company
            user_query: User's question or request
            session_id: Optional existing session ID
            
        Returns:
            Dictionary containing response data and success status
        """
        try:
            if not self._validate_inputs(company_key, user_query):
                return {
                    "success": False,
                    "error": "Invalid inputs"
                }

            company_config = self._config_manager.get_company_configuration(
                company_key
            )
            if not company_config:
                return {
                    "success": False,
                    "error": f"Company '{company_key}' not found"
                }

            # Enhance user query with company context
            enhanced_query = self._enhance_user_query(
                user_query, company_config
            )

            if session_id:
                response = self._agent_manager.process_query(
                    session_id, enhanced_query, company_key, company_config
                )
            else:
                session_result = self._agent_manager.create_new_session(
                    company_key, company_config, enhanced_query
                )
                if not session_result['success']:
                    return session_result

                session_id = session_result['session_id']
                response = self._agent_manager.process_query(
                    session_id, enhanced_query, company_key, company_config
                )

            if response['success']:
                response['session_id'] = session_id

            return response

        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def get_available_companies(self) -> List[Dict[str, str]]:
        """Get list of available companies.
        
        Returns:
            List of dictionaries containing company information
        """
        companies = []
        for key, config in self._config_manager.companies.items():
            companies.append({
                "key": key,
                "name": config.name,
                "description": config.description,
                "industry": config.industry
            })
        return companies

    def get_industries(self) -> List[str]:
        """Get list of available industries.
        
        Returns:
            List of industry names
        """
        return self._config_manager.get_industries()

    def get_companies_by_industry(self, industry: str) -> List[Dict[str, str]]:
        """Get companies for a specific industry.
        
        Args:
            industry: Industry name to filter by
            
        Returns:
            List of companies in the specified industry
        """
        return self._config_manager.get_companies_by_industry(industry)

    def get_service_status(self) -> Dict[str, Any]:
        """Get service status information.
        
        Returns:
            Dictionary containing service status and metrics
        """
        return {
            "service_status": "operational",
            "total_companies": len(self._config_manager.companies),
            "available_companies": self.get_available_companies()
        }

    def create_new_session(
        self, 
        company_key: str, 
        initial_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new session for a company.
        
        Args:
            company_key: Unique identifier for the company
            initial_query: Optional initial query for the session
            
        Returns:
            Dictionary containing session creation result
        """
        try:
            company_config = self._config_manager.get_company_configuration(
                company_key
            )
            if not company_config:
                return {
                    "success": False,
                    "error": f"Company '{company_key}' not found"
                }

            return self._agent_manager.create_new_session(
                company_key, company_config, initial_query
            )

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create session: {str(e)}"
            }

    def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """Get session information.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Dictionary containing session information
        """
        return self._agent_manager.get_session_information(session_id)

    def list_user_sessions(self, limit: int = 20) -> Dict[str, Any]:
        """List active sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            Dictionary containing list of sessions and metadata
        """
        try:
            sessions = self._agent_manager.list_active_sessions()
            return {
                "success": True,
                "sessions": sessions[:limit],
                "total_count": len(sessions)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list sessions: {str(e)}"
            }

    def switch_to_session(self, session_id: str) -> Dict[str, Any]:
        """Switch to an existing session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Dictionary containing session switch result
        """
        return self._agent_manager.switch_to_session(session_id)

    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete a session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Dictionary containing deletion result
        """
        return self._agent_manager.delete_session(session_id)

    def _enhance_user_query(
        self,
        user_query: str,
        company_config: CompanyConfiguration
    ) -> str:
        """Enhance user query with company context information.
        
        Args:
            user_query: Original user query
            company_config: Company configuration object
            
        Returns:
            Enhanced query with company context
        """
        return self._QUERY_ENHANCEMENT_TEMPLATE.format(
            company_name=company_config.name,
            industry=company_config.industry,
            description=company_config.description,
            original_query=user_query.strip()
        )

    def _validate_inputs(self, company_key: str, user_query: str) -> bool:
        """Validate input parameters.
        
        Args:
            company_key: Company identifier to validate
            user_query: User query to validate
            
        Returns:
            True if inputs are valid, False otherwise
        """
        available_keys = self._config_manager.get_available_company_keys()
        if company_key.lower() not in [key.lower() for key in available_keys]:
            return False

        if (not user_query or not user_query.strip() or
                len(user_query.strip()) < 2):
            return False

        return True

    # Template for enhancing user queries with company context
    _QUERY_ENHANCEMENT_TEMPLATE = (
        "Company: {company_name} ({industry} industry) - {description}. "
        "User Query: {original_query}"
    )