"""Strands Agent manager for Digital Twin application."""

import os
import uuid
import time
from typing import Dict, List, Any
from datetime import datetime

from strands.tools import tool
from strands.session.repository_session_manager import (
    RepositorySessionManager
)
from flotorch.strands.session import FlotorchStrandsSession
from flotorch.strands.agent import FlotorchStrandsAgent

from ..core.config import CompanyConfiguration
from ..knowledge.knowledge_base import KnowledgeBaseClient


class StrandsAgentManager:
    """Manager for Strands agents."""

    def __init__(self) -> None:
        """Initialize the Strands Agent Manager."""
        self._knowledge_client = KnowledgeBaseClient()
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        self._shared_agent = None
        self._shared_session_manager = None

        self._api_key = os.getenv("FLOTORCH_API_KEY", "")
        self._base_url = os.getenv("FLOTORCH_BASE_URL", "")
        self._model_id = os.getenv(
            "FLOTORCH_MODEL_ID",
            "anthropic.claude-3-sonnet-20240229-v1:0"
        )
    
    def create_new_session(
        self,
        company_key: str,
        company_config: CompanyConfiguration,
        initial_query: str = None
    ) -> Dict[str, Any]:
        """Create a new Strands session for a company.
        
        Args:
            company_key: Unique identifier for the company
            company_config: Company configuration object
            initial_query: Optional initial query for the session
            
        Returns:
            Dictionary containing session creation result
        """
        try:
            session_id = str(uuid.uuid4())
            
            # Initialize shared agent for each new session to ensure unique session IDs
            self._initialize_shared_agent(session_id)

            session_title = self._generate_session_title(
                initial_query, company_config.name
            )

            # Store session metadata only - no agent recreation
            self._active_sessions[session_id] = {
                'company_key': company_key,
                'company_name': company_config.name,
                'created_at': time.time(),
                'session_title': session_title
            }

            return {
                "success": True,
                "session_id": session_id,
                "company_name": company_config.name,
                "company_key": company_key,
                "session_title": session_title
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create session: {str(e)}"
            }
    
    def process_query(
        self,
        session_id: str,
        query: str,
        company_key: str = None,
        company_config: CompanyConfiguration = None
    ) -> Dict[str, Any]:
        """Process a query using an existing session.
        
        Args:
            session_id: Unique identifier for the session
            query: User query string
            company_key: Optional company key for context switching
            company_config: Optional company config for context switching
            
        Returns:
            Dictionary containing query response and metadata
        """
        try:
            if session_id not in self._active_sessions:
                return {
                    "success": False,
                    "error": "Session not found"
                }

            # Initialize shared agent if not already done
            if self._shared_agent is None:
                self._initialize_shared_agent()

            session_info = self._active_sessions[session_id]

            # Update session metadata if company context changed
            if (company_key and company_config and
                    session_info['company_key'] != company_key):
                session_info['company_key'] = company_key
                session_info['company_name'] = company_config.name

            # Use shared agent - no need to recreate
            response = self._shared_agent(query)

            return {
                "success": True,
                "response": str(response),
                "session_id": session_id,
                "company_name": session_info['company_name']
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing query: {str(e)}"
            }
    
    def get_session_information(self, session_id: str) -> Dict[str, Any]:
        """Get session information.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Dictionary containing session information
        """
        if session_id not in self._active_sessions:
            return {
                "success": False,
                "error": "Session not found"
            }

        session_info = self._active_sessions[session_id]
        return {
            "success": True,
            "session_id": session_id,
            "company_name": session_info['company_name'],
            "company_key": session_info['company_key'],
            "session_title": session_info['session_title']
        }

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions.
        
        Returns:
            List of session dictionaries sorted by creation time
        """
        sessions = []
        for session_id, session_info in self._active_sessions.items():
            sessions.append({
                'session_id': session_id,
                'company_name': session_info['company_name'],
                'company_key': session_info['company_key'],
                'session_title': session_info['session_title'],
                'created_at': session_info['created_at'],
                'created_at_formatted': datetime.fromtimestamp(
                    session_info['created_at']
                ).strftime('%Y-%m-%d %H:%M')
            })

        sessions.sort(key=lambda x: x['created_at'], reverse=True)
        return sessions

    def switch_to_session(self, session_id: str) -> Dict[str, Any]:
        """Switch to an existing session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Dictionary containing session switch result
        """
        if session_id not in self._active_sessions:
            return {
                "success": False,
                "error": "Session not found"
            }

        session_info = self._active_sessions[session_id]
        return {
            "success": True,
            "session_id": session_id,
            "company_name": session_info['company_name'],
            "company_key": session_info['company_key'],
            "session_title": session_info['session_title']
        }

    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete a session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Dictionary containing deletion result
        """
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
            return {
                "success": True,
                "message": "Session deleted successfully"
            }
        else:
            return {
                "success": False,
                "error": "Session not found"
            }
    
    def _initialize_shared_agent(self, session_id: str) -> None:
        """Initialize the shared agent instance for each new session.
        
        Args:
            session_id: Session ID to use for the shared agent
        """
        try:
            # Create a generic knowledge tool that works for all companies
            knowledge_tool = self._create_generic_knowledge_tool()

            repository = FlotorchStrandsSession(
                api_key=self._api_key,
                base_url=self._base_url
            )

            # Use the provided session_id for the shared agent
            self._shared_session_manager = RepositorySessionManager(
                session_id=session_id,
                session_repository=repository
            )

            flotorch_client = FlotorchStrandsAgent(
                agent_name=os.getenv("FLOTORCH_AGENT_NAME"),
                api_key=os.getenv("FLOTORCH_API_KEY"),
                base_url=os.getenv("FLOTORCH_BASE_URL"),
                custom_tools=[knowledge_tool],
                session_manager=self._shared_session_manager
            )

            self._shared_agent = flotorch_client.get_agent()

        except Exception as e:
            raise Exception(f"Failed to initialize shared agent: {str(e)}")

    def _create_generic_knowledge_tool(self):
        """Create a generic knowledge base tool for all companies.
        
        Returns:
            Configured knowledge tool that works for all companies
        """
        @tool
        def company_knowledge_tool(query: str) -> str:
            """Retrieve information from the shared knowledge base.
            
            Use this tool to get accurate, up-to-date information.
            The agent will frame the query properly with company context.
            
            Args:
                query: User query string (already enhanced with context)
                
            Returns:
                Retrieved information or error message
            """
            try:
                result = self._knowledge_client.retrieve_company_information(
                    query
                )

                if result.get('success'):
                    return result.get(
                        'raw_content', 'No information found.'
                    )
                else:
                    return ("Unable to retrieve information from "
                            "knowledge base.")

            except Exception as e:
                return f"Error retrieving information: {str(e)}"

        return company_knowledge_tool

    def _generate_session_title(
        self,
        initial_query: str,
        company_name: str
    ) -> str:
        """Generate session title from initial query or company name.
        
        Args:
            initial_query: Optional initial query string
            company_name: Company display name
            
        Returns:
            Generated session title
        """
        if initial_query and len(initial_query) > 50:
            return initial_query[:50] + "..."
        elif initial_query:
            return initial_query
        else:
            return f"Chat with {company_name}"