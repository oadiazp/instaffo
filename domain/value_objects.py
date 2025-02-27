"""
Domain value objects for the job matching system.

Value objects are immutable objects that don't have an identity but are defined
by their attributes. They represent concepts that are important to the domain.
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import NewType


class SeniorityLevel(Enum):
    """Enumeration of valid seniority levels."""
    NONE = "none"
    JUNIOR = "junior"
    MIDLEVEL = "midlevel"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"


@dataclass(frozen=True)
class Seniority:
    """Value object representing a seniority level."""
    level: SeniorityLevel

    @classmethod
    def from_string(cls, seniority_str: str) -> 'Seniority':
        """Create a Seniority value object from a string."""
        try:
            level = SeniorityLevel(seniority_str.lower())
            return cls(level)
        except ValueError:
            valid_levels = [level.value for level in SeniorityLevel]
            raise ValueError(f"Invalid seniority level: {seniority_str}. "
                             f"Valid levels are: {', '.join(valid_levels)}")

    def __str__(self) -> str:
        return self.level.value


@dataclass(frozen=True)
class Salary:
    """Value object representing a monetary amount for salary."""
    value: int

    def __post_init__(self):
        """Validate the salary value."""
        if self.value < 0:
            raise ValueError("Salary cannot be negative")

    def __str__(self) -> str:
        return f"{self.value}"


@dataclass(frozen=True)
class Skill:
    """Value object representing a professional skill."""
    name: str

    def __post_init__(self):
        """Normalize the skill name."""
        object.__setattr__(self, 'name', self.name.strip())
        if not self.name:
            raise ValueError("Skill name cannot be empty")

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name.lower())
        
    def __eq__(self, other) -> bool:
        if not isinstance(other, Skill):
            return False
        return self.name.lower() == other.name.lower()


# Type definitions for improved type hinting
MatchScore = NewType('MatchScore', float)
