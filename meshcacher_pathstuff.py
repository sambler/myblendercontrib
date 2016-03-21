import os
import json
import random
import bpy

'''
Things to do
A Path stuff
set up non svn folder (maybe should be in one file)
drill down to blend file and create 'shadow folder'
Meshcacher root folder within blendfile ? probably
Subfolders for each cache? yes
figure out names of cache subfolders for uniqueness, and multi cache objects.

Config stuff
Any path configuration in the file (supercedes global configs)
list of cached things

'''

SEP = os.path.sep
CONFIGTEXT = "meshcacher_config.JSON"
MAX_ID = 999999 # theoretical max number of caches in a file


class MeshcacherPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    project_root_full_path = bpy.props.StringProperty(
        name="Project Path",
        description="Top Directory of Project e.g. /home/bassam/tubeSVN",
        default="", subtype='DIR_PATH')
    cache_root_name = bpy.props.StringProperty(
        name="None SVN Name",
        description="Name of Directory of non SVN tree(caches, etc)",
        default="non_svn")


class CacheConfig(object):
    '''
    Save and Read Configs from current file
    Config Stucture
    {'root_dir': 'root directory', 'caches': [ caches ]}
    cache structure:
    {
    'ID': 'unique cache ID', # an integer
    'rig': 'rig name',
    'action': 'action name',
    'cache_dir': '', path of caches on disk

    'transform': [,,,], # matrix of rig object if not in action
    'bone_transforms': {'bone_name': [,,,]}, # unkeyed, transformed bones

    }
    '''

    def __init__(self, context):
        if CONFIGTEXT in bpy.data.texts:
            self.configtext = bpy.data.texts[CONFIGTEXT]
            self.configs.injest()
            self._create_root_dir(self.configstruct['root_dir']) # XXX needed?
        else:
            self.configstruct = {
                'root_dir':self._set_root_dir(context), 'caches':[]}
            self.configtext = bpy.data.texts.new(name=CONFIGTEXT)
            self.configtext.from_string(json.dumps(self.configstruct))

    def injest(self):
        self.configstruct = json.loads(self.configtext.as_string())

    def add_cache(self, cache_data):
        while True:
            cache_id = random.randint(0, MAX_ID)
            if cache_id not in [cache['ID'] for cache in self.configstruct]:
                break # XXX slow if close to MAX_ID
        cache_data['ID'] = cache_id
        self.configstruct['caches'].append(cache_data)
        self.configtext.from_string(json.dumps(self.configstruct))
        return cache_id

    def get_cache(self, cache_id):
        for cache in self.configstruct['caches']:
            if cache['ID'] == cache_id:
                return cache

    def _set_root_dir(self, context):
        '''
        Create the Root of the Caches in non svn based on the current file
        '''
        # get project_root and cache_root_name from preferences
        user_prefs = context.user_preferences
        addon_prefs = user_prefs.addons[__name__].preferences
        project_root_full_path = addon_prefs.project_root_full_path
        cache_root_name = addon_prefs.cache_root_name

        # generate paths as lists of nested folders
        project_root_path = bpy.path.abspath(project_root_full_path).split(SEP)
        cache_root_path = project_root_path[:-1]
        cache_root_path.append(cache_root_name)

        # recreate tree down to current file (.blend to a folder name)
        blend_path = os.path.split(
            bpy.path.abspath(bpy.context.blend_data.filepath))
         current_path = os.path.join(
            blend_path[0], blend_path[-1].replace('.blend', '')).split(SEP)

        # now we need individual cache paths
        sub_paths = current_path[len(project_root_path):]
        cache_path = cache_root_path.join(sub_paths)

        # create the cache paths
        cache_path = SEP.join(cache_path)
        self._create_root_dir(cache_path)
        return cache_path

    def _create_root_dir(self, cache_path):
        try:
            os.makedirs(cache_path)
        except FileExistsError:
            print('dir exists')
