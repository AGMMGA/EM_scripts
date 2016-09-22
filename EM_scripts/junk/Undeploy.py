import os, getpass

MOUNT_POINT_SSD = '/processing'
MOUNT_POINT_STORAGE = '/local_storage'

def _getuser():
    userdef = getpass.getuser()
    print 'Please select a username. [default: {0}]'.format(userdef)
    user = raw_input('>')
    if user == '':
        return userdef
    return user
            
def get_project_folder():
    project_folder = ''
    while project_folder =='':
        print 'Please specify the name of the project to be relocated'
        project_folder = raw_input('>')
    return project_folder

def get_program_folder_names():
    check = 0
    while not check:
        print ('Please insert the name of the folder for relion processing ["relion"]')
        image_folder=raw_input('>')
        if image_folder == '':
            image_folder = 'relion'
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
                  '''.format(image_folder, eman2_folder, scipion_folder))
        check = correct_y_n()
    return image_folder, eman2_folder, scipion_folder

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

def recap(p):
    print '\nUsername : {}'.format(p['user'])
    print 'Project name : {}'.format(p['project_folder'])
    print 'image_folder : {}'.format(p['image_folder'])
    
def check_if_exist(p):
    offending = []
    processing = os.path.join(MOUNT_POINT_SSD, p['user'], p['project'])
    storage = os.path.join(MOUNT_POINT_STORAGE, p['user'], p['project'])
    if not os.path.isdir(processing):
        offending.append(processing)
    if not os.path.isdir(storage):
        offending.append(storage)
    if not os.path.isdir(os.path.join(storage, p['relion'])):
        offending.append(os.path.join(storage, p['relion']))
    
def main():
    p = {} #the dictionary that contains all parameters
    p['user_check'] = 0
    p['folder_found'] = 0
    # getting user input
    while not p['user_check']:
        p['user'] = _getuser()
#         p['user'] = 'andrea'
        while not p['folder_found']:
            p['project_folder'] = get_project_folder()
#             p['project_folder'] = '20160126_BRCA1_GO'
            if os.path.isdir(os.path.join(MOUNT_POINT_SSD, p['user'], 
                                          p['project_folder'])):
                p['folder_found']=1
            else:
                print ('the folder {0} does not exist'.format(p['project_folder']))
                continue
        
        
        # p['image_folder'], p['eman2_folder'], p['scipion_folder'] = \
#                                         get_program_folder_names()
        p['image_folder'], p['eman2_folder'], p['scipion_folder'] = \
                        'relion', 'eman2', 'scipion'
        recap(p)
        p['user_check'] = correct_y_n()
    # checking all folders exist
    
    
    
    
    
    
if __name__ == '__main__':
    main()