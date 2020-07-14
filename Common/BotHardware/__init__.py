

# ev3dev version "jessie" recomended
# Still using version 1 of the python-ev3dev library
# To migrate, see: https://python-ev3dev.readthedocs.io/en/ev3dev-stretch/upgrading-to-stretch.html
# However, not sure if it is worthwile


from .educator_base import _EducatorBase

EducatorBot = _EducatorBase  # deprecated name
EducatorBase = _EducatorBase


from .enterprise_base import _EnterpriseBase

EnterpriseBot = _EnterpriseBase  # deprecated name
EnterpriseBase = _EnterpriseBase

