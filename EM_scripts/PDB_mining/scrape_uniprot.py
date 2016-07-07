import os
import pickle
import glob
import shutil
from pprint import pprint
from Bio.PDB import PDBList
from Bio import ExPASy, SwissProt
from urllib.error import HTTPError

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

def parse_pdbredo_seq(folder, filename):
    '''
    use this code to make a dictionary with pdb_code : sequence (from seqres)
    pdbredo_seqdeb.txt was mined by Bart Beusekom during the making of pdb_redo
    and has the format: >pdbcode_chain\n seqUENCE
    where inside the sequence, the residues that could be traced in the density are
    capitalized, whereas the ones not observed but nevertheless present in the 
    original construct (tags, disordered regions, etc) are not capitalized
    '''
    with open(os.path.join(folder, filename), 'r') as f:
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
    return entries

def serialize(obj, folder, filename):
        with open(os.path.join(folder, filename), 'wb') as out:
            pickle.dump(obj, out)

def retrieve(folder, filename):
        with open(os.path.join(folder, filename), 'rb') as f:
            return pickle.load(f)

def check_all_exist(PDB_list_nochain, pdb_folder):
    file_list = sorted(['pdb{}.ent'.format(x) for x in PDB_list_nochain])
    files_in_dir = [x.split('/')[-1] for x in \
                    sorted(glob.iglob(os.path.join(pdb_folder, '*.ent')))]
    diff = [x for x in file_list if x not in files_in_dir]
    if not (len(diff)==0):
        raise IOError('some pdb files are missing from {}'.format(pdb_folder))

def find_uniprot_in_pdb(PDB_list_nochain, pdb_folder):
    pdb_files = sorted(glob.iglob(os.path.join(pdb_folder, '*.ent')))
    pdb_to_uniprot = {}
    for file in pdb_files:
        entry_code = file.split('/')[-1][3:7]
        pdb_to_uniprot[entry_code] = dbref_finder(file)
    return pdb_to_uniprot


#######
#config parameters - quick and dirty

overwrite = True
reparse_pdbseq = False
new_subset = True
n_entries = 10
working_dir = '/home/andrea/git/EM_scripts/EM_scripts/PDB_mining/'
pdbredo_seq_file = 'pdbredo_seqdb.txt'
pdbredo_seq_folder = working_dir
entries_json_file = 'pdb_seq.pickle'
pdb_folder = '/home/andrea/git/EM_scripts/EM_scripts/PDB_mining/PDB_structures'
pdb_list = 'pdb_entry_list'
uniprot_folder = '/home/andrea/git/EM_scripts/EM_scripts/PDB_mining/uniprot_entries'
uniprot_file = 'uniprot.pickle'
#######

#startup check for files etc. - refactor in a proper way
if new_subset and overwrite:
    print('Removing folders from the previous run.')
    try:
        shutil.rmtree(pdb_folder)
        shutil.rmtree(uniprot_folder)
    except FileNotFoundError:
        pass
elif new_subset:
    if os.path.isdir(pdb_folder) or os.path.isdir(uniprot_folder):
        raise SystemExit('one or more directories exist, aborting. set overwrite true to bypass')
elif not new_subset:
    if not(os.path.isdir(pdb_folder) and os.path.isdir(uniprot_folder)):
        raise SystemExit('PDB and/or uniprot foders are missing, aborting')
    
#######

if reparse_pdbseq:
    #turn pdb_redo_out to a {pdbcode:seq} format
    try:
        entries = parse_pdbredo_seq(working_dir, pdbredo_seq_file)      
        serialize(entries, pdbredo_seq_folder, entries_json_file)
    except IOError:
        raise('Missing some file')
else:
    entries = retrieve(pdbredo_seq_folder, entries_json_file)
    
if new_subset:
    #grab some subset of the pdb, download files and parse for uniprot xreferences
    os.mkdir(pdb_folder)
    os.mkdir(uniprot_folder)
        
    #select a pseudo_random subset of entries by slicing the entries dict 
    #(which is in pseudo-random) order
    PDB_subset = list(entries.keys())[:n_entries]
    PDB_subset_nochain = [x.split('_')[0] for x in PDB_subset]
    #fetch and save all the pdb files
    pdbl = PDBList()
    for entry in PDB_subset_nochain:
        pdbl.retrieve_pdb_file(entry, pdir=pdb_folder)
    #serialize the PDB list for future use
    serialize(PDB_subset, pdb_folder, pdb_list)
    # parse the pdb headers for DBREF to uniprot
    pdb_to_uniprot = find_uniprot_in_pdb(PDB_subset_nochain, pdb_folder)
    #determine the uniprot references to fetch
    to_fetch = []
    for entry in pdb_to_uniprot.keys():
        for ref in pdb_to_uniprot[entry].values():
            if ref not in to_fetch:
                to_fetch.append(ref)
    #fetch uniprot references as Record objects, then move them to a serializable dict
    uniprot_records = {}
    uniprot_failed = []
    for ref in to_fetch:
        try:
            with ExPASy.get_sprot_raw(ref) as handle:
                uniprot_records[ref] = {'record' : SwissProt.read(handle)}
        except (HTTPError, ValueError):
            uniprot_failed.append(ref) #deprecated uniprot entries fail on urllib problems
    serialize(uniprot_records, uniprot_folder, uniprot_file)
    serialize(uniprot_failed, uniprot_folder, uniprot_file.replace('.', '_failed.'))
    
    ###### Let's get all the pdb xreferences from the uniprot entries we have, and put them in
    # a sensible data structure
    clean = uniprot_records.copy()
    for ref in list(uniprot_records.keys()):
        clean[ref]['xrefs'] = {}
        clean[ref]['seq'] = uniprot_records[ref]['record'].sequence
        for xref in uniprot_records[ref]['record'].cross_references:
            #xref format ('PDB', ....... ,'A=1-451') for what we want
            if xref[0] == 'PDB':
                # possible format (1): E=28-337, F=731-744 - this will raise ValueError
                # possible format (2): A/B/C/D=1-367
                # possible format (3): A=1-367
                try:
                    chain, __ = xref[-1].split('=')
                    start, stop = __.split('-')
                    clean[ref]['xrefs'].update({xref[1]: {'chain' : chain,
                                                          'start' : start,
                                                          'stop' : stop}})
                except ValueError:
                    pass # who cares if we miss one
    serialize(clean, uniprot_folder, uniprot_file.replace('.','_clean.'))

    
elif not new_subset:
    #opening previous PDb list from pickle file
    PDB_subset = retrieve(pdb_folder, pdb_list)
    PDB_subset_nochain = [x.split('_')[0] for x in PDB_subset]
    #checking that all files exist
    check_all_exist(PDB_subset_nochain, pdb_folder)
    # retrieve uniprot entries
    uniprot_records = retrieve(uniprot_folder, uniprot_file)
    clean = retrieve(uniprot_folder, uniprot_file.replace('.','_clean.'))
pprint(clean)

