# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

"""
Subversion Partial Inter-Dependency Ranger
Spider does the following:
  Perform a sparse directory-only checkout from project svn
  Provide an api for extracting a specific file via update
  Use of dependencies (cached?) to extract a thing
"""

"""
checkout only the top level folder of a project, includes:
library.json , some kind of dependency tree
to check out a file

some ideas:
- initial 'smarts' are in data and on client side
- each project needs a unique project ID
- automatic dependency crawlers, potentially using bpy, gimp api, others
- manual dependency addition
- external project ID based recognition for future cross project dependencies
- untracked 'generated' folder management with own method of retreiving caches  (if available) or regenerating based on recepies (if available)
- metadata for generated files, problem with reproducability

start with:
- enhance library.json by nesting asset data one deeper, allowing extra data
- implement crawler api + blend based crawler
- ignore generated issue
- ignore cross project deps but:
- create project ID

reference desk enhancements
- update reference desk to be smarter with data types *
- generic posthooks *
- image previews *
- compatibility with library.json changes
- project browser and:
- commit capability
- update capability

initial commit issues:
- single file based commit (easy from blender)
- easy show uncommited files

* these options unrelelated to spider

"""

import pysvn
import os
import bpy
import json
from collections import defaultdict
from . import topsort

LIBRARY_FILE = "library.json"
DEPENDS_FILE = "dependencies.json"
CONFIG_FILE = "config.json"
STANDARD_FOLDER_IGNORES = ['.svn']


def is_blendfile(filepath):
    """ Check that a file is a blend file """
    return filepath.endswith('.blend')


def abspath_path(filepath, rootpath):
    """ Return absolute path from relative to root or just normalize """
    normalized = os.path.normpath(filepath) # Assume root is normalized
    if not rootpath in normalized:
        normalized = os.path.join(root, normalized)
    return normalized


def relpath_path(filepath, rootpath):
    """ Return absolute path based on root """
    normalized = os.path.normpath(filepath)
    if rootpath in normalized:
        return os.path.relpath(normalized, rootpath)
    else:
        return normalized


class ProjectTree():
    """ Smart subversion wrapper with knowledge of project depedencies """

    def __init__(self, path, url=None, user=None, password=None):
        def get_login():
            pass
        self.client = pysvn.Client()
        self.root = os.path.normpath(path)
        if not os.path.exists(self.root):
            self._checkout_empty_project()
        self.url = self._get_url(url)
        self.user = user
        self.password = password

    def _get_url(self, url):
        if not url:
            return self.client.info(self.root).url
        return url

    def _checkout_empty_project(self):
        self.client.checkout(self.url, self.path, recurse=False)

    def _update_path(self, path):
        full_path = self._abs_path(self._rel_path(path))
        self.client.update(
            full_path,
            depth=pysvn.depth.empty,
            make_parents=True)                

    def _rel_path(self, path):
        norm = os.path.normpath(path) 
        if norm.startswith(self.root):
            return os.path.relpath(norm, self.root)
        else:
            return norm

    def _abs_path(self, path):
        return os.path.abspath(os.path.join(self.root, os.path.norm(path))) 


class ProjectCrawler():
    """ Crawl Over Entire Project Generating Dependency Graph """

    def __init__(self, path):
        self.root = os.path.normpath(path)
        self.depedencies_file = os.path.join(self.root, LIBRARY_FILE)
        self.config_file = os.path.join(self.root, DEPENDS_FILE)
        if not any(os.path.exists(fn) in (
                self.dependencies_file, self.config_file)):
            raise IOError('Not a Project Folder')
        self.data = json.loads(open(self.depedencies_file).read())
        self.config = json.loads(open(self.config_file).read())
        self.ignores = STANDARD_FOLDER_IGNORES + self.config.ignore_folders

    def self._relpath(path):
        return relpath_path(path, self.root)

    def self._abspath(path):
        return abspath_path(path, self.root)

    def _walker(self, fn):

        def wrapped():
            for check_dir in os.walk(self.root):
                if all(folder not in check_dir[0] for folder in self.ignores):
                    for filename in check_dir[2]:
                        fn(self, os.path.join(check_dir[0],filename))
        return wrapped

    def get_blendfile_dependencies(self, blend_file):
        normalized = self._abs_path(blend_file)
        if is_blendfile(normalized):
            bpy.ops.wm.open_mainfile(filepath=normalized)
            paths = (
                bpy.path.abspath(path)
                for path in bpy.utils.blend_paths(absolute=True))
            node = {'path':normalized, 'filetype': 'BLEND'}
            self.network.add_node(node)
            for dependency in paths:
                self.network.add_edge(
                    node,
                    {
                        'path':self._relpath(dependency),
                        'filetype':get_file_type(dependency)})

    @self._walker
    def get_all_blend_dependencies(self, blend_file):
        self.get_blendfile_dependencies(blend_file)
