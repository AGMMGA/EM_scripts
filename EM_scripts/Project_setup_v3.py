import os, getpass, time

MOUNT_POINT_SSD = '/processing'
MOUNT_POINT_STORAGE = '/local_storage'

def _getuser():
    userdef = getpass.getuser()
    print 'Please select a username. [default: {0}]'.format(userdef)
    user = raw_input('>')
    if user == '':
        return userdef
    return user
            
def get_project_name():
    project_name = ''
    while project_name =='':
        print 'Please specify the name of the project'
        print 'The final directory will be [date]_[project]'
        project_name = raw_input('>')
    return project_name

def get_date():
    curr_date = time.strftime("%Y%m%d")
    print 'Insert the desired date for the project (YYYYMMDD) [{0}]'.format(curr_date)
    date = raw_input('>')
    if date =='':
        return curr_date
    return date

def get_program_folder_names():
    check = 0
    while not check:
        print ('Please insert the name of the folder for relion processing ["relion"]')
        relion_folder=raw_input('>')
        if relion_folder == '':
            relion_folder = 'relion'
        print ('Please insert the name of the folder for eman2 processing ["eman2"]')
        eman2_folder=raw_input('>')
        if eman2_folder == '' :
            eman2_folder = 'eman2'
        print ('Please insert the name of the folder for scipion processing ["scipion"]')
        scipion_folder=raw_input('>')
        if scipion_folder == '' :
            scipion_folder = 'scipion'
        print ('''\nThe folders are:
                  relion: {0}
                  eman2: {1}
                  scipion: {2}
                  '''.format(relion_folder, eman2_folder, scipion_folder))
        check = correct_y_n()
    return relion_folder, eman2_folder, scipion_folder

def correct_y_n(msg=''):
    print msg
    print ('Is this correct? (y/n)')
    answer = raw_input('>')
    while not(answer == 'y' or answer == 'n'):
        print ('Please answer "y" or "n"')
        answer = raw_input('>')
    if answer == 'n':
        print ('\n')
        return 0
    else:
        return 1
        
def create_relion_folder_names(user, project, relion_folder):
    '''
    Creates the following tree:
    /local_storage/user/project/relion/Class2D
                                      /Class3D
                                      /Refine3D
                                      /@Micrographs
                                      /@Particles
    /processing/user/project/relion/@Class2D
                                   /@Class3D
                                   /@Refine3D
                                   /Particles
                                   /Micrographs
    '''
    dirs_to_create = []
    links_to_create = []  
    base_relion_path_processing = os.path.join(MOUNT_POINT_SSD, user, project, \
                                               relion_folder)
    base_relion_path_storage = os.path.join(MOUNT_POINT_STORAGE, user, project,\
                                             relion_folder)
    dirs_to_create.append(base_relion_path_processing)
    dirs_to_create.append(base_relion_path_storage)
    for i in ['Class2D', 'Class3D', 'Refine3D']:
        dirs_to_create.append(os.path.join(base_relion_path_storage, i))
        target = os.path.join(base_relion_path_storage, i)
        link_name = os.path.join(base_relion_path_processing, i)
        links_to_create.append((target, link_name)) #tuple
    for i in ['Micrographs', 'Particles']:
        dirs_to_create.append(os.path.join(base_relion_path_processing, i))
        target = os.path.join(base_relion_path_processing, i)
        link_name = os.path.join(base_relion_path_storage, i)
        links_to_create.append((target, link_name)) #tuple
    return dirs_to_create, links_to_create

def create_eman2_folder_names(user, project, eman2_folder, relion_folder):
    '''
    Creates the following tree:
    /local_storage/user/project/eman2/@micrographs -> /processing/..../eman2/micrographs
                                     /@Particles -> /processing/..../relion/Particles
                               /relion/Micrographs/@eman2 #saves clicking when browsing
                               /relion/Particles/@eman2   #ditto
    /processing/user/project/@eman2 -> /local_storage/user/project/eman2/
    '''
    dirs_to_create = []
    links_to_create = []  
    base_eman2_path_storage = os.path.join(MOUNT_POINT_STORAGE, user, project,\
                                             eman2_folder)
    base_eman2_path_processing = os.path.join(MOUNT_POINT_SSD, user, project,\
                                             eman2_folder)
    relion_base_folder = os.path.join(MOUNT_POINT_SSD, user, project, relion_folder)
    dirs_to_create.append(base_eman2_path_storage)
    links_to_create.append((os.path.join(relion_base_folder, 'Micrographs'),  \
                        os.path.join (base_eman2_path_storage, 'Micrographs')))
    links_to_create.append((os.path.join(relion_base_folder, 'Particles'),  \
                        os.path.join (base_eman2_path_storage, 'Particles')))
    links_to_create.append((base_eman2_path_storage, \
                        os.path.join(relion_base_folder, 'Particles', eman2_folder)))
    links_to_create.append((base_eman2_path_storage, \
                        os.path.join(relion_base_folder, 'Micrographs',eman2_folder)))
    links_to_create.append((base_eman2_path_storage, base_eman2_path_processing))
    
    return dirs_to_create, links_to_create
    
def create_base_folder_names(user, project):
    dirs_to_create = []
    dirs_to_create.append(os.path.join(MOUNT_POINT_SSD, user))
    dirs_to_create.append(os.path.join(MOUNT_POINT_STORAGE, user))
    dirs_to_create.append(os.path.join(MOUNT_POINT_SSD, user, project))
    dirs_to_create.append(os.path.join(MOUNT_POINT_STORAGE, user, project))
    dirs_to_create.append(os.path.join(MOUNT_POINT_STORAGE, user, project, 'movies'))
    return dirs_to_create 
    
def create_folders(folders_to_create):
    #as a policy, user directory are readable by everyone. if the directory 
    #already exists, the error will be silenced. Any other OSError will be raised
    #I prefer not to use os.makedirs() to have more control 
    for folder in folders_to_create:
        try:    
            os.mkdir(folder, 0777)
        except OSError:       
            if not os.path.isdir(folder): 
                raise
    return 1 

def create_links(links_list): #links_list: list of (target, link_name)
    for link in links_list:
        try:
            os.symlink(link[0], link[1])
        except OSError as e:
            if e.errno != 17: #link exists already
                raise                 


if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    msg1 = '''
This script will setup your directories to take advantage of the SSD\n
    '''
    links_list = []
    check = 0
    print (msg1)
    while not check:
        user = _getuser()
        date = get_date()
        project = '{0}_{1}'.format(date, get_project_name())
        print '\n\nThe username is {0}'.format(user)
        print 'The final project name will be {0}'.format(project)
        check = correct_y_n()
    
    relion_folder, eman2_folder, scipion_folder = \
        get_program_folder_names()
#     user = 'thor'
#     project = '20151212_BRCA1A'
#     relion_folder = 'relion'
    folders_list = create_base_folder_names(user, project)
    folders_relion, links_relion = create_relion_folder_names(user, project, \
                                                              relion_folder)
    folders_list += folders_relion
    links_list += links_relion
    folders_eman2, links_eman2 = create_eman2_folder_names(user, project, \
                                                eman2_folder, relion_folder)
    folders_list += folders_eman2
    links_list += links_eman2
    #adding scipion base path
    folders_list.append(os.path.join(MOUNT_POINT_SSD, user, project, scipion_folder))
    folders_list.append(os.path.join(MOUNT_POINT_STORAGE, user, project, scipion_folder))
    create_folders(folders_list)
    create_links(links_list)
    