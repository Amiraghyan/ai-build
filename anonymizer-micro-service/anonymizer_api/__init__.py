"""
Paquet `anonymizer_api`

Expose les fonctions publiques pour un import direct :
    from anonymizer_api import anonymize_all
"""

from .anonymizer import anonymize_all, anonymize_all_many 

__all__ = ("anonymize_all", "anonymize_all_many")

