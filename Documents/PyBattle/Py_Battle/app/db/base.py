#Base is like a parent class. Every database table you create later will inherit from this. Think of it as a blueprint template.

from sqlalchemy.orm import declarative_base
Base= declarative_base()