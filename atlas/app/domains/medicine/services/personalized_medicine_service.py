"""
Personalized Medicine Service - Compatibility wrapper
Re-exports PersonalizedMedicineService from app.domains.medicine.services.personalized_medicine_service
"""

from app.domains.medicine.personalized.personalized_medicine_service import PersonalizedMedicineService

__all__ = ["PersonalizedMedicineService"]