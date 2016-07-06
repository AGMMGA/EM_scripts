import os
import json
import glob
from pprint import pprint
from Bio.PDB import PDBParser, PDBList
from Bio.PDB.PDBExceptions import PDBConstructionWarning

def dbref_finder(pdb_file):
    '''
    Parses the header of the PDB file for DBREF entries
    returns all the references to uniprot
    returns an empty dictionary if no references to uniprot are found
    '''
    
    dbrefs = {}
    with open(pdb_file) as pdb:
        for line in pdb:
            if not line.startswith('DBREF'):
                continue
            else:
                if line.split()[5] == 'UNP':
                    chain = line.split()[2]
                    ref = line.split()[6]
                    dbrefs[chain]=ref
    return dbrefs

'''
use this code to make a dictionary with pdb_code : sequence (from seqres)
pdbredo_seqdeb.txt was mined by Bart Beusekom during the making of pdb_redo
and has the format: >pdbcode_chain\n seqUENCE
where inside the sequence, the residues that could be traced in the density are
capitalized, whereas the ones not observed but nevertheless present in the 
original construct (tags, disordered regions, etc) are not capitalized
'''
#config parameters - quick and dirty
working_dir = '/home/andrea/git/EM_scripts/EM_scripts/PDB_mining/'
pdbredo_seq_file = 'pdbredo_seqdb.txt'
json_dir = working_dir
entries_json_file = 'pdb_seq.json'
pdb_folder = '/home/andrea/git/EM_scripts/EM_scripts/PDB_mining/PDB_structures'
new_pdb = False
pdb_list = 'pdb_entry_list'

#turn pdb_redo_out to a {pdbcode:seq} format
if not os.path.isfile(os.path.join(json_dir, entries_json_file)):
    with open(os.path.join(working_dir, pdbredo_seq_file), 'r') as f:
        entries = {}
        while True:
            line1 = f.readline()
            line2 = f.readline()
            if not line1:
                break
            if not line1.startswith('>'):
                raise IOError('Uh oh something went wrong with the fasta format of {}'.format(
                                    pdbredo_seq_file))
            name = line1.split('>')[-1].strip()
            seq = line2.strip()
            entries[name] = seq       
    with open(os.path.join(json_dir, entries_json_file), 'w') as out:
        json.dump(entries, out)
else:
    with open(os.path.join(json_dir, entries_json_file), 'r') as json_in: 
        entries = json.load(json_in)

#grab some subset of the pdb, download files and parse for uniprot xreferences
if new_pdb:
    #select a pseudo_random subset of entries by slicing the entries dict 
    # (which is in pseudo-random) order
    PDB_subset = list(entries.keys())[:10]
    PDB_subset_nochain = [x.split('_')[0] for x in PDB_subset]
    #fetch and save all the pdb files
    pdbl = PDBList()
    for entry in PDB_subset_nochain:
        pdbl.retrieve_pdb_file(entry, pdir=pdb_folder)
    #serialize the PDB list for future use
    with open(os.path.join(pdb_folder, pdb_list), 'w') as f:
        json.dump(PDB_subset, f)
    
elif not new_pdb:
    #opening previous PDb list from json file
    with open(os.path.join(pdb_folder, pdb_list), 'r') as f:
        PDB_subset = json.load(f)
        PDB_subset_nochain = [x.split('_')[0] for x in PDB_subset]
    #checking that all files exist
    file_list = sorted(['pdb{}.ent'.format(x) for x in PDB_subset_nochain])
    files_in_dir = [x.split('/')[-1] for x in \
                    sorted(glob.iglob(os.path.join(pdb_folder, '*.ent')))]
    diff = [x for x in file_list if x not in files_in_dir]
    if not (len(diff)==0):
        raise IOError('some pdb files are missing from {}'.format(pdb_folder))
else:
    raise Exception('Uh oh something went wrong in the pdb retrieval logic')

# parse the pdb headers for DBREF to uniprot
pdb_files = sorted(glob.iglob(os.path.join(pdb_folder, '*.ent')))
parser = PDBParser(QUIET=True) #Quiet=true suppresses error messages about PDB parsing
uniprot_refs = {}
for file in pdb_files:
    entry_code = file.split('/')[-1][3:7]
    uniprot_refs[entry_code] = dbref_finder(file)

pprint(uniprot_refs)

# if not os.path.isfile(filename):
#     pdbl = PDBList(pdb='/home/andrea/git/EM_scripts/EM_scripts/PDB mining/')
#     fetched = pdbl.retrieve_pdb_file('1UBQ')
# else:
#     parser = PDBParser()
#     fetched = parser.get_structure('Ubq', filename)
# pprint(fetched.__dict__)

# import json
# from Bio import ExPASy, SeqIO
# 
# if not os.path.isfile('Q9UJ24'):
#     with ExPASy.get_sprot_raw('Q9UJ24') as handle:
#         with open('Q9UJ24', 'w') as f:
#             seq_record = SeqIO.read(handle, 'swiss')
#             SeqIO.write(seq_record, f, 'seqxml')
# else:
#     with open ('Q9UJ24', 'r') as f:
#         seq_record = SeqIO.read(f, 'seqxml') 
#         
# pprint(seq_record)

    