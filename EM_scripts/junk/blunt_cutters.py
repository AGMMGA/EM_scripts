from pprint import pprint
from Bio.Restriction import AllEnzymes

a = [e for e in AllEnzymes if e.is_blunt() and len(e) == 6 and ('N' in e.suppl) and ('M' in e.suppl) and e.opt_temp == 37]
pprint([(name, name.site) for name in a]) 