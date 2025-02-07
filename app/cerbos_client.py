from cerbos.sdk.grpc.client import CerbosClient
from cerbos.engine.v1 import engine_pb2
from google.protobuf.struct_pb2 import Value

class CerbosClientClass:
    """A client class for interacting with Cerbos authorization service.
    
    This class provides methods to check access permissions using Cerbos,
    a policy engine for handling authorization logic.
    """

    def __init__(self, host: str = "cerbos", port: int = 3592):
        """Initialize the Cerbos client.
        
        Args:
            host (str): Hostname of the Cerbos server. Defaults to "cerbos".
            port (int): Port number of the Cerbos server. Defaults to 3592.
        """

        self.base_url = f"{host}:{port}"
        self.client = CerbosClient(self.base_url)

    def check_access(self, principal: dict, resource: dict, action: str):
        """Check if a principal has permission to perform an action on a resource.
        
        Args:
            principal (dict): Dictionary containing principal information with keys:
                - id: Principal identifier
                - roles: List of roles assigned to the principal
                - attr: Optional dictionary of principal attributes
            resource (dict): Dictionary containing resource information with keys:
                - id: Resource identifier (optional, defaults to "0")
                - kind: Type/kind of the resource
                - attr: Optional dictionary of resource attributes
            action (str): The action to check permission for
        
        Returns:
            bool: True if access is allowed, False otherwise
        
        Note:
            The method converts all attribute values to strings when creating
            the protobuf Value objects for compatibility with Cerbos.
        """

        principal_attrs = {}
        for key, value in principal.get("attr", {}).items():
            principal_attrs[key] = Value(string_value=str(value)) 

        # Create principal protobuf object
        principal = engine_pb2.Principal(
            id=str(principal.get("id", "0")),
            roles=principal["roles"],  # Convert to set
            policy_version="default",
            attr=principal_attrs
        )

        resource_attrs = {}
        for key, value in resource.get("attr", {}).items():
            resource_attrs[key] = Value(string_value=str(value))

        # Create resource protobuf object
        resource = engine_pb2.Resource(
            id=resource.get("id", "0"),
            kind=resource["kind"],
            policy_version="default",
            attr=resource_attrs
        )
        try:
            is_allowed = self.client.is_allowed(action, principal, resource)
            return is_allowed
        except Exception:
            # Return False if any error occurs during the permission check
            return False