"""Notification Template Service

STORY-071: Notification Template Management System
Service for managing notification templates with versioning.

Python 3.5+ compatible
"""

import logging
import re
from datetime import datetime
from typing import Optional, Dict, List, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.notification_templates import (
    NotificationTemplate,
    NotificationTemplateVersion,
    NotificationTemplateVariable
)


logger = logging.getLogger(__name__)


class NotificationTemplateService(object):
    """Service for notification template management"""

    # Variable pattern matching: {variable_name}
    VARIABLE_PATTERN = re.compile(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}')

    def __init__(self, db):
        self.db = db

    async def create_template(
        self,
        name: str,
        category: str,
        channel: str,
        subject: str,
        body: str,
        language: str = "id",
        variables: Optional[List[str]] = None,
        description: Optional[str] = None,
        created_by: Optional[int] = None,
        is_default: bool = False,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """Create a new notification template

        Args:
            name: Template name
            category: Template category
            channel: Notification channel
            subject: Message subject
            body: Message body with variable placeholders
            language: Language code
            variables: List of variables used in template
            description: Template description
            created_by: User ID who created template
            is_default: Whether this is default template
            is_active: Whether template is active

        Returns:
            Dict with template details
        """
        try:
            # Extract variables from body if not provided
            if variables is None:
                variables = self._extract_variables(subject + " " + body)

            # Create template
            template = NotificationTemplate(
                name=name,
                category=category,
                channel=channel,
                language=language,
                subject=subject,
                body=body,
                variables={"variables": variables},
                description=description,
                created_by=created_by,
                updated_by=created_by,
                is_default=is_default,
                is_active=is_active,
                version=1
            )

            self.db.add(template)
            await self.db.flush()

            # Create initial version
            version = NotificationTemplateVersion(
                template_id=template.id,
                version_number=1,
                subject=subject,
                body=body,
                variables={"variables": variables},
                change_reason="Initial version",
                changed_by=created_by
            )
            self.db.add(version)

            await self.db.commit()

            logger.info(
                "Created notification template: {}".format(name)
            )

            return {
                "template_id": template.id,
                "name": template.name,
                "category": template.category,
                "channel": template.channel,
                "language": template.language,
                "version": template.version,
                "is_active": template.is_active,
                "message": "Template created successfully"
            }

        except Exception as e:
            logger.error("Error creating template: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to create template: {}".format(str(e)))

    async def get_template(
        self,
        template_id: int
    ) -> Dict[str, Any]:
        """Get template by ID

        Args:
            template_id: Template ID

        Returns:
            Dict with template details
        """
        try:
            query = select(NotificationTemplate).where(
                NotificationTemplate.id == template_id
            )
            result = await self.db.execute(query)
            template = result.scalar_one_or_none()

            if not template:
                raise ValueError("Template {} not found".format(template_id))

            return {
                "template_id": template.id,
                "name": template.name,
                "category": template.category,
                "channel": template.channel,
                "language": template.language,
                "subject": template.subject,
                "body": template.body,
                "variables": template.variables,
                "is_active": template.is_active,
                "is_default": template.is_default,
                "version": template.version,
                "description": template.description,
                "created_by": template.created_by,
                "updated_by": template.updated_by,
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "updated_at": template.updated_at.isoformat() if template.updated_at else None
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error getting template: {}".format(e))
            raise ValueError("Failed to get template: {}".format(str(e)))

    async def list_templates(
        self,
        category: Optional[str] = None,
        channel: Optional[str] = None,
        language: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """List templates with filtering and pagination

        Args:
            category: Filter by category
            channel: Filter by channel
            language: Filter by language
            is_active: Filter by active status
            page: Page number
            per_page: Items per page

        Returns:
            Dict with templates list and pagination info
        """
        try:
            # Build filters
            filters = []

            if category:
                filters.append(NotificationTemplate.category == category)
            if channel:
                filters.append(NotificationTemplate.channel == channel)
            if language:
                filters.append(NotificationTemplate.language == language)
            if is_active is not None:
                filters.append(NotificationTemplate.is_active == is_active)

            # Get total count
            count_query = select(func.count(NotificationTemplate.id))
            if filters:
                count_query = count_query.where(and_(*filters))
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar() or 0

            # Get templates with pagination
            offset = (page - 1) * per_page
            query = select(NotificationTemplate)
            if filters:
                query = query.where(and_(*filters))
            query = query.order_by(NotificationTemplate.name.asc()).limit(per_page).offset(offset)

            result = await self.db.execute(query)
            templates = result.scalars().all()

            # Build response
            template_list = [
                {
                    "template_id": t.id,
                    "name": t.name,
                    "category": t.category,
                    "channel": t.channel,
                    "language": t.language,
                    "subject": t.subject,
                    "is_active": t.is_active,
                    "is_default": t.is_default,
                    "version": t.version,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None
                }
                for t in templates
            ]

            return {
                "templates": template_list,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
            }

        except Exception as e:
            logger.error("Error listing templates: {}".format(e))
            raise ValueError("Failed to list templates: {}".format(str(e)))

    async def update_template(
        self,
        template_id: int,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        variables: Optional[List[str]] = None,
        description: Optional[str] = None,
        updated_by: Optional[int] = None,
        is_active: Optional[bool] = None,
        change_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing template

        Args:
            template_id: Template ID
            subject: New subject
            body: New body
            variables: New variables list
            description: New description
            updated_by: User ID making update
            is_active: New active status
            change_reason: Reason for change

        Returns:
            Dict with updated template details
        """
        try:
            # Get template
            query = select(NotificationTemplate).where(
                NotificationTemplate.id == template_id
            )
            result = await self.db.execute(query)
            template = result.scalar_one_or_none()

            if not template:
                raise ValueError("Template {} not found".format(template_id))

            # Store old values for versioning
            old_subject = template.subject
            old_body = template.body
            old_variables = template.variables

            # Update fields
            if subject is not None:
                template.subject = subject
            if body is not None:
                template.body = body
            if variables is not None:
                template.variables = {"variables": variables}
            elif body is not None or subject is not None:
                # Re-extract variables if body/subject changed
                new_subject = template.subject or ""
                new_body = template.body or ""
                extracted_vars = self._extract_variables(new_subject + " " + new_body)
                template.variables = {"variables": extracted_vars}
            if description is not None:
                template.description = description
            if is_active is not None:
                template.is_active = is_active

            # Increment version
            template.version = (template.version or 0) + 1
            template.updated_by = updated_by
            template.updated_at = datetime.utcnow()

            # Create new version record
            new_version = NotificationTemplateVersion(
                template_id=template.id,
                version_number=template.version,
                subject=template.subject,
                body=template.body,
                variables=template.variables,
                change_reason=change_reason or "Template updated",
                changed_by=updated_by
            )
            self.db.add(new_version)

            await self.db.commit()

            logger.info(
                "Updated notification template: {} to version {}".format(
                    template.name, template.version
                )
            )

            return {
                "template_id": template.id,
                "name": template.name,
                "version": template.version,
                "message": "Template updated successfully"
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error updating template: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to update template: {}".format(str(e)))

    async def delete_template(
        self,
        template_id: int
    ) -> Dict[str, Any]:
        """Delete a template

        Args:
            template_id: Template ID

        Returns:
            Dict with deletion confirmation
        """
        try:
            # Get template
            query = select(NotificationTemplate).where(
                NotificationTemplate.id == template_id
            )
            result = await self.db.execute(query)
            template = result.scalar_one_or_none()

            if not template:
                raise ValueError("Template {} not found".format(template_id))

            # Don't allow deletion of default templates
            if template.is_default:
                raise ValueError("Cannot delete default template")

            template_name = template.name

            # Delete template (versions will cascade)
            await self.db.delete(template)
            await self.db.commit()

            logger.info(
                "Deleted notification template: {}".format(template_name)
            )

            return {
                "message": "Template deleted successfully",
                "template_id": template_id
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error deleting template: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to delete template: {}".format(str(e)))

    async def preview_template(
        self,
        template_id: int,
        sample_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Preview template with sample data

        Args:
            template_id: Template ID
            sample_data: Sample data for variable substitution

        Returns:
            Dict with rendered subject and body
        """
        try:
            # Get template
            query = select(NotificationTemplate).where(
                NotificationTemplate.id == template_id
            )
            result = await self.db.execute(query)
            template = result.scalar_one_or_none()

            if not template:
                raise ValueError("Template {} not found".format(template_id))

            # Render template
            rendered_subject = self._render_template(
                template.subject or "",
                sample_data
            )
            rendered_body = self._render_template(
                template.body,
                sample_data
            )

            return {
                "template_id": template_id,
                "subject": rendered_subject,
                "body": rendered_body,
                "variables": template.variables
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error previewing template: {}".format(e))
            raise ValueError("Failed to preview template: {}".format(str(e)))

    async def get_template_versions(
        self,
        template_id: int
    ) -> List[Dict[str, Any]]:
        """Get version history for a template

        Args:
            template_id: Template ID

        Returns:
            List of template versions
        """
        try:
            query = select(NotificationTemplateVersion).where(
                NotificationTemplateVersion.template_id == template_id
            ).order_by(
                NotificationTemplateVersion.version_number.desc()
            )

            result = await self.db.execute(query)
            versions = result.scalars().all()

            return [
                {
                    "version_id": v.id,
                    "version_number": v.version_number,
                    "subject": v.subject,
                    "body": v.body,
                    "variables": v.variables,
                    "change_reason": v.change_reason,
                    "changed_by": v.changed_by,
                    "changed_at": v.changed_at.isoformat() if v.changed_at else None
                }
                for v in versions
            ]

        except Exception as e:
            logger.error("Error getting template versions: {}".format(e))
            raise ValueError("Failed to get template versions: {}".format(str(e)))

    async def rollback_template(
        self,
        template_id: int,
        target_version: int,
        updated_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """Rollback template to a previous version

        Args:
            template_id: Template ID
            target_version: Version number to rollback to
            updated_by: User ID making rollback

        Returns:
            Dict with updated template details
        """
        try:
            # Get template
            query = select(NotificationTemplate).where(
                NotificationTemplate.id == template_id
            )
            result = await self.db.execute(query)
            template = result.scalar_one_or_none()

            if not template:
                raise ValueError("Template {} not found".format(template_id))

            # Get target version
            version_query = select(NotificationTemplateVersion).where(
                and_(
                    NotificationTemplateVersion.template_id == template_id,
                    NotificationTemplateVersion.version_number == target_version
                )
            )
            version_result = await self.db.execute(version_query)
            target_version_obj = version_result.scalar_one_or_none()

            if not target_version_obj:
                raise ValueError("Version {} not found".format(target_version))

            # Rollback template to target version
            template.subject = target_version_obj.subject
            template.body = target_version_obj.body
            template.variables = target_version_obj.variables
            template.version = (template.version or 0) + 1
            template.updated_by = updated_by
            template.updated_at = datetime.utcnow()

            # Create new version record for the rollback
            new_version = NotificationTemplateVersion(
                template_id=template.id,
                version_number=template.version,
                subject=target_version_obj.subject,
                body=target_version_obj.body,
                variables=target_version_obj.variables,
                change_reason="Rollback to version {}".format(target_version),
                changed_by=updated_by
            )
            self.db.add(new_version)

            await self.db.commit()

            logger.info(
                "Rolled back template {} to version {}".format(
                    template.name, target_version
                )
            )

            return {
                "template_id": template.id,
                "name": template.name,
                "version": template.version,
                "message": "Template rolled back successfully"
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error rolling back template: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to rollback template: {}".format(str(e)))

    def _extract_variables(self, text: str) -> List[str]:
        """Extract variable names from template text

        Args:
            text: Template text

        Returns:
            List of unique variable names
        """
        matches = self.VARIABLE_PATTERN.findall(text)
        # Return unique variables in order of appearance
        seen = set()
        unique_vars = []
        for var in matches:
            if var not in seen:
                seen.add(var)
                unique_vars.append(var)
        return unique_vars

    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Render template with data

        Args:
            template: Template string
            data: Data for variable substitution

        Returns:
            Rendered string
        """
        def replacer(match):
            var_name = match.group(1)
            value = data.get(var_name, match.group(0))  # Keep placeholder if not found
            return str(value) if value is not None else match.group(0)

        return self.VARIABLE_PATTERN.sub(replacer, template)


def get_notification_template_service(db):
    """Get or create notification template service instance

    Args:
        db: Database session

    Returns:
        NotificationTemplateService instance
    """
    return NotificationTemplateService(db)
