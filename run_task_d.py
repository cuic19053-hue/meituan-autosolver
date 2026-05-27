import sys
sys.path.insert(0, 'd:/美团')
from backend.compliance_check import check_compliance, print_compliance_report
result = check_compliance(r'd:/美团')
print_compliance_report(result)