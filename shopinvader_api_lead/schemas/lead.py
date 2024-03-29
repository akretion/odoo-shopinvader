# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel


class Lead(StrictExtendableBaseModel):
    id: int
    subject: str
    email: str | None = None
    description: str | None = None

    @classmethod
    def from_crm_lead(cls, lead):
        return cls.model_construct(
            id=lead.id,
            subject=lead.name,
            email=lead.email_from or None,
            description=lead.description or None,
        )


class LeadInput(StrictExtendableBaseModel):
    subject: str
    email: str | None = None
    description: str | None = None

    def to_crm_lead_vals(self) -> dict:
        return {
            "name": self.subject,
            "email_from": self.email,
            "description": self.description,
        }
