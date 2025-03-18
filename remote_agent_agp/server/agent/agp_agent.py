

"""Module containing the AgpAgent class for managing agent details."""
 
class AgpAgent:
    """
    Represents an agent with configuration details.

    Public Methods:
        get_details() -> dict: Returns a dictionary with the agent's details.
        set_details(organization: str, namespace: str, local_agent: str) -> None: Updates the agent details.
        get_organization() -> str: Retrieves the organization of the agent.
        get_namespace() -> str: Retrieves the namespace of the agent.
        get_local_agent() -> str: Retrieves the local agent identifier.
    """

    organization: str = "cisco"
    namespace: str = "default"
    local_agent: str = "server"

    @classmethod
    def get_details(cls) -> dict:
        """
        Retrieve details of the agent, including its organization, namespace, and local agent.

        Returns:
            dict: A dictionary with the following keys:
                - "organization": The organization associated with the agent.
                - "namespace": The namespace of the agent.
                - "local_agent": The local agent identifier.
        """
        return {
            "organization": cls.organization,
            "namespace": cls.namespace,
            "local_agent": cls.local_agent,
        }

    @classmethod
    def set_details(cls, organization: str, namespace: str, local_agent: str) -> None:
        """
        Set the class-level details for organization, namespace, and local agent.

        Parameters:
            organization (str): The name of the organization.
            namespace (str): The namespace associated with the agent.
            local_agent (str): The identifier for the local agent.

        Returns:
            None
        """
        cls.organization = organization
        cls.namespace = namespace
        cls.local_agent = local_agent

    @classmethod
    def get_organization(cls) -> str:
        """
        Retrieve the organization associated with the agent.

        Returns:
            str: The organization of the agent.
        """
        return cls.organization

    @classmethod
    def get_namespace(cls) -> str:
        """
        Retrieve the namespace associated with the agent.

        Returns:
            str: The namespace of the agent.
        """
        return cls.namespace

    @classmethod
    def get_local_agent(cls) -> str:
        """
        Retrieve the local agent identifier.

        Returns:
            str: The local agent identifier.
        """
        return cls.local_agent
