"""GraphQL schema for HireMeBahamas API."""
from typing import Optional
import logging

import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..graphql.resolvers import Query, Mutation
from ..database import get_db
from ..core.security import get_current_user_optional
from ..models import User

logger = logging.getLogger(__name__)


# Create the GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)


async def get_graphql_context(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> dict:
    """Get the GraphQL context with database session and current user."""
    return {
        "request": request,
        "db": db,
        "current_user": current_user,
    }


def create_graphql_router() -> GraphQLRouter:
    """Create the GraphQL router for FastAPI."""
    return GraphQLRouter(
        schema,
        path="/graphql",
        graphql_ide="graphiql",  # Enable GraphiQL IDE for testing
        context_getter=get_graphql_context,
    )
