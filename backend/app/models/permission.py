from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from app.db.session import Base


class Permission(Base):
    """Permission model for RBAC - defines what actions can be performed on resources"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), nullable=False, index=True)  # admin, doctor, nurse, etc.
    resource = Column(String(50), nullable=False, index=True)  # patient, diagnosis, prescription, etc.
    action = Column(String(50), nullable=False)  # create, read, update, delete
    granted = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint('role', 'resource', 'action', name='unique_role_permission'),
    )


# Predefined permissions based on Indonesian hospital roles
PREDEFINED_PERMISSIONS = [
    # Admin permissions
    {"role": "admin", "resource": "user", "action": "create", "granted": True},
    {"role": "admin", "resource": "user", "action": "read", "granted": True},
    {"role": "admin", "resource": "user", "action": "update", "granted": True},
    {"role": "admin", "resource": "user", "action": "delete", "granted": True},
    {"role": "admin", "resource": "config", "action": "update", "granted": True},
    {"role": "admin", "resource": "audit_log", "action": "read", "granted": True},

    # Doctor permissions
    {"role": "doctor", "resource": "patient", "action": "read", "granted": True},
    {"role": "doctor", "resource": "patient", "action": "update", "granted": True},
    {"role": "doctor", "resource": "diagnosis", "action": "create", "granted": True},
    {"role": "doctor", "resource": "diagnosis", "action": "read", "granted": True},
    {"role": "doctor", "resource": "diagnosis", "action": "update", "granted": True},
    {"role": "doctor", "resource": "prescription", "action": "create", "granted": True},
    {"role": "doctor", "resource": "prescription", "action": "read", "granted": True},
    {"role": "doctor", "resource": "vitals", "action": "create", "granted": True},
    {"role": "doctor", "resource": "vitals", "action": "read", "granted": True},
    {"role": "doctor", "resource": "lab_order", "action": "create", "granted": True},
    {"role": "doctor", "resource": "lab_order", "action": "read", "granted": True},
    {"role": "doctor", "resource": "radiology_order", "action": "create", "granted": True},
    {"role": "doctor", "resource": "radiology_order", "action": "read", "granted": True},
    {"role": "doctor", "resource": "encounter", "action": "create", "granted": True},
    {"role": "doctor", "resource": "encounter", "action": "read", "granted": True},
    {"role": "doctor", "resource": "encounter", "action": "update", "granted": True},

    # Nurse permissions
    {"role": "nurse", "resource": "patient", "action": "read", "granted": True},
    {"role": "nurse", "resource": "vitals", "action": "create", "granted": True},
    {"role": "nurse", "resource": "vitals", "action": "read", "granted": True},
    {"role": "nurse", "resource": "diagnosis", "action": "read", "granted": True},
    {"role": "nurse", "resource": "prescription", "action": "read", "granted": True},
    {"role": "nurse", "resource": "lab_order", "action": "read", "granted": True},
    {"role": "nurse", "resource": "radiology_order", "action": "read", "granted": True},
    {"role": "nurse", "resource": "encounter", "action": "read", "granted": True},
    {"role": "nurse", "resource": "nursing_note", "action": "create", "granted": True},

    # Pharmacist permissions
    {"role": "pharmacist", "resource": "patient", "action": "read", "granted": True},
    {"role": "pharmacist", "resource": "prescription", "action": "read", "granted": True},
    {"role": "pharmacist", "resource": "prescription", "action": "update", "granted": True},  # For dispense status
    {"role": "pharmacist", "resource": "medication", "action": "create", "granted": True},
    {"role": "pharmacist", "resource": "medication", "action": "read", "granted": True},
    {"role": "pharmacist", "resource": "inventory", "action": "create", "granted": True},
    {"role": "pharmacist", "resource": "inventory", "action": "read", "granted": True},
    {"role": "pharmacist", "resource": "inventory", "action": "update", "granted": True},

    # Receptionist permissions
    {"role": "receptionist", "resource": "patient", "action": "create", "granted": True},
    {"role": "receptionist", "resource": "patient", "action": "read", "granted": True},
    {"role": "receptionist", "resource": "patient", "action": "update", "granted": True},
    {"role": "receptionist", "resource": "encounter", "action": "create", "granted": True},
    {"role": "receptionist", "resource": "encounter", "action": "read", "granted": True},
    {"role": "receptionist", "resource": "queue", "action": "create", "granted": True},
    {"role": "receptionist", "resource": "queue", "action": "read", "granted": True},
    {"role": "receptionist", "resource": "queue", "action": "update", "granted": True},

    # Lab staff permissions
    {"role": "lab_staff", "resource": "patient", "action": "read", "granted": True},
    {"role": "lab_staff", "resource": "lab_order", "action": "read", "granted": True},
    {"role": "lab_staff", "resource": "lab_order", "action": "update", "granted": True},
    {"role": "lab_staff", "resource": "lab_result", "action": "create", "granted": True},
    {"role": "lab_staff", "resource": "lab_result", "action": "read", "granted": True},

    # Radiology staff permissions
    {"role": "radiology_staff", "resource": "patient", "action": "read", "granted": True},
    {"role": "radiology_staff", "resource": "radiology_order", "action": "read", "granted": True},
    {"role": "radiology_staff", "resource": "radiology_order", "action": "update", "granted": True},
    {"role": "radiology_staff", "resource": "radiology_exam", "action": "create", "granted": True},
    {"role": "radiology_staff", "resource": "radiology_exam", "action": "read", "granted": True},

    # Billing staff permissions
    {"role": "billing_staff", "resource": "patient", "action": "read", "granted": True},
    {"role": "billing_staff", "resource": "encounter", "action": "read", "granted": True},
    {"role": "billing_staff", "resource": "bill", "action": "create", "granted": True},
    {"role": "billing_staff", "resource": "bill", "action": "read", "granted": True},
    {"role": "billing_staff", "resource": "bill", "action": "update", "granted": True},
    {"role": "billing_staff", "resource": "payment", "action": "create", "granted": True},
]
