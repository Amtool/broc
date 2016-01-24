  
#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module manages the Syntax used in BROC file

Authors: zhousongsong(doublesongsong@gmail.com)
Date:    2015/09/15 10:30:02
"""

import os
import sys
import string
import glob

broc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_path)

from dependency import SyntaxTag
from dependency import Environment
from dependency import Source
from dependency import Target
from util import Function
from util import Log

class NotInSelfModuleError(Exception):
    """
    In Broc file, if files or directories users specify don't belongs to module itself
    raise NotInSelfModuleError 
    """ 
    def __init__(self, _input, _dir):
        """
        Args:
            _input : the file or directory beneathes directory _dir
            _dir : the directory path
        """
        Exception.__init__(self)
        self._input = _input
        self._dir = _dir

    def __str__(self):
        """
        """
        return "couldn't find (%s) in (%s)" % (self._input, self._dir)


class BrocArgumentIllegalError(Exception):
    """
    when arguments in Broc are illegal, raise BrocArgumentIllegalError
    """
    def __init__(self, msg):
        """
        Args:
            msg : error info
        """ 
        Exception.__init__(self)
        self._msg = msg

    def __str__(self):
        """
        """
        return self._msg


class BrocProtoError(Exception):
    """
    when handle proto file failed, raise BrocProtoError
    """
    def __init__(self, msg):
        """
        Args:
            msg : error info
        """ 
        Exception.__init__(self)
        self._msg = msg

    def __str__(self):
        """
        """
        return self._msg


def COMPILER_PATH(k):
    """
    set global path of compiler's directory
    influence main moudle and all dependent modules
    Args:
        k : string object, compiler's directory, for example: if you set k as '/usr/bin',
            we should find 'gcc' and 'g++' in directory /usr/bin
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    env.SetCompilerDir(k)


def CPPFLAGS(d_flags, r_flags):
    """
    set module's global preprocess flags
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    # default build mode is debug, it can be modified by command 'broc' by user
    if env.BuildMode() == "debug":
        env.CppFlags().AddSV(d_flags)
    else:
        env.CppFlags().AddSV(r_flags)


def CppFlags(d_flags, r_flags):
    """
    set local prrprocess flags, override the global CPPFLAGS
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    tag = SyntaxTag.TagCppFlags()
    # default build mode is debug, it can be modified by command 'broc' by user
    if env.BuildMode() == "debug":
        tag.AddSV(d_flags)
    else:
        tag.AddSV(r_flags)
    return tag
    

def CFLAGS(d_flags, r_flags):
    """
    set the global compile options for c files, 
    this influences the all of c files in module
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    # default build mode is debug, it can be modified by command 'broc' by user
    if env.BuildMode() == "debug":
        env.CFlags().AddSV(d_flags)
    else:
        env.CFlags().AddSV(r_flags)


def CFlags(d_flags, r_flags):
    """
    set the local compile options for c files, 
    this influences the all of c files in target tag
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    tag = SyntaxTag.TagCFlags()
    if sys.argv[0]=='PLANISH':
        return tag
    env = Environment.GetCurrent()
    tag = SyntaxTag.TagCFlags()
    if env.BuildMode() == "debug":
        tag.AddSV(d_flags)
    else:
        tag.AddSV(r_flags)
    return tag


def CXXFLAGS(d_flags, r_flags):
    """
    set the global compile options for c++ files, 
    this influences the all of cxx files in module
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    if sys.argv[0]=='PLANISH':
        return
    
    env = Environment.GetCurrent()
    if env.BuildMode() == "debug":
        env.CxxFlags().AddSV(d_flags)
    else:
        env.CxxFlags().AddSV(r_flags)


def CxxFlags(d_flags, r_flags):
    """
    set the local compile option for cxx files, 
    this influences the all of cxx files in target tag
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    tag = SyntaxTag.TagCxxFlags()
    if sys.argv[0]=='PLANISH':
        return tag
    env = Environment.GetCurrent()
    if env.BuildMode() == "debug":
        tag.AddSV(d_flags)
    else:
        tag.AddSV(r_flags)
    return tag


def CONVERT_OUT(s):
    """
    convert a directory of module into a reponsed output directory
    if s doesn't beneath the module, raise NotInSelfModuleError
    Args:
        s : a relative directory beneathed the module
    Returns:
        return the relative path of responsed output directory 
    """
    if sys.argv[0]=='PLANISH':
        return ""
    env = Environment.GetCurrent()
    _s = os.path.normpath(os.path.join(env.BrocDir(), s))
    # to check whether _s beneathes directory of module
    if env.ModulePath() not in _s:
        raise NotInSelfModuleError(env.BrocDir(), _s)
    return os.path.normpath(os.path.join('broc_out', env.BrocCVSDir(), s))


def INCLUDE(*ss):
    """
    set the global head file search path
    Default head files search path includes $WORKSPACE and $OUT_ROOT
    Args:
       ss : a variable number of string objects 
            ss may contain multiple string objects, each object can contain multiple paths
            1. if path does not beneath module, in other words, if user want to specified other modules' path,  should start with $WORKSPACE, 
            2. if path couldn't be founed in module itself and path does not start with $WORKSPACE rasie NotInSelfModuleError
            3. if path is output directory, it must start with 'broc_out/'
            for example: ss can be "./include ./include/foo", "$WORKSPACE/include", "broc_out/test/include"
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    tag = env.IncludePaths()
    broc_dir = env.BrocDir()
    for s in ss:
        ps = s.split()
        for x in ps:
            if x.startswith("$WORKSPACE"):
                tag.AddSV(x.replace("$WORKSPACE/", '')) 
                continue
            elif x.startswith("broc_out/") or os.path.isabs(x):
                tag.AddSV(x)
                continue
            elif x.startswith("$OUT_ROOT"):
                tag.AddSV(x.replace("$OUT_ROOT", 'broc_out'))
                continue
            elif x.startswith("$OUT"):
                out = os.path.join('broc_out', env.ModuleCVSPath(), 'output')
                tag.AddSV(x.replace("$OUT", out))
            else:     
                _x = os.path.normpath(os.path.join(broc_dir, x))
                if env.ModulePath() not in _x:
                    raise NotInSelfModuleError(_x, env.ModulePath())
                else:
                    tag.AddSV(_x)
    

def Include(*ss):
    """
    set the local file search path
    Args:
       ss : a variable number of string objects 
            ss may contain multiple string objects, each object can contain multiple paths
            1. if path does not beneath module, in other words, if user want to specified other modules' path,  should start with $WORKSPACE, 
            2. if path couldn't be founed in module itself and path does not start with $WORKSPACE rasie NotInSelfModuleError
            3. if path is output directory, it must start with 'broc_out/'
            for example: ss can be "./include ./include/foo", "$WORKSPACE/include", "broc_out/test/include"
    """
    tag = SyntaxTag.TagInclude()
    if sys.argv[0]=='PLANISH':
        return tag
    env = Environment.GetCurrent()
    broc_abs_dir = env.BrocDir()
    broc_cvs_dir = env.BrocCVSDir()
    for s in ss:
        ps = string.split(s)
        for x in ps:
            if x.startswith("$WORKSPACE"):
                tag.AddSV(x.replace("$WORKSPACE/", "")) 
                continue
            elif x.startswith('broc_out') or os.path.isabs(x):
                tag.AddSV(x)
                continue
            elif x.startswith("$OUT_ROOT"):
                tag.AddSV(x.replace("$OUT_ROOT/", 'broc_out'))
                continue
            elif x.startswith("$OUT"):
                out = os.path.join('broc_out', env.ModuleCVSPath(), 'output')
                tag.AddSV(x.replace("$OUT", out))
                continue
            else:
                _x = os.path.normpath(os.path.join(broc_abs_dir, x))
                if env.ModulePath() not in _x:
                    raise NotInSelfModuleError(_x, env.ModulePath())
                else:
                    tag.AddSV(os.path.normpath(os.path.join(broc_cvs_dir, x)))
    return tag


def Libs(*ss):
    """
    add .a files to target tag, such as APPLICATION, UT_APPLICATION, STATIC_LIBRARY
    ss may contain multiple arguments, each argument can contain muitiple lib's path,
    each lib's path should start with $OUT_ROOT
    for example Libs("$ROOT_OUT/test/output/lib/libutil.a", "$ROOT_OUT/foo/output/lib/libcommon.a")
    Args:
        ss : a variable number of string objects 
    Returns:
        SyntaxTag.TagLibs() 
    """
    tag = SyntaxTag.TagLibs()
    if sys.argv[0]=='PLANISH':
        return tag
    for s in ss:
        if not isinstance(s, str):
            raise BrocArgumentIllegalError("argument %s is illegal in tag Libs" % s)
        if os.path.isabs(s):
            tag.AddSV(s)
            continue
        elif s.startswith("$OUT_ROOT"):
            tag.AddSV(os.path.normpath(s.replace("$OUT_ROOT", "broc_out")))
            continue
        elif s.startswith('$WORKSPACE'):
            tag.AddSV(os.path.normpath(s.replace("$WORKSPACE/", "")))
            continue
        elif s.startswith("$OUT"):
            env = Environment.GetCurrent()
            out = os.path.join('broc_out', env.ModuleCVSPath(), 'output')
            tag.AddSV(os.path.normpath(s.replace("$OUT", out)))
            continue
        else:
            raise BrocArgumentIllegalError("args(%s) should be a abs path or startswith $WORKSPACE|$OUT|$OUT_ROOT in tag Libs" % s)

    return tag


def LDFLAGS(d_flags, r_flags):
    """
    add global link flags 
    Args:
        d_flags : link flags in debug mode
        r_flags : link flags in release mode
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    if env.BuildMode() == "debug":
        env.LDFlags().AddSV(d_flags)
    else:
        env.LDFlags().AddSV(r_flags)


def LDFlags(d_flags, r_flags):
    """
    add local link flags
    Args:
        d_flags : link flags in debug mode
        r_flags : link flags in release mode
    """
    tag = SyntaxTag.TagLDFlags()
    if sys.argv[0]=='PLANISH':
        return tag
    env = Environment.GetCurrent()
    if env.BuildMode() == "debug":
        tag.AddSV(d_flags)
    else:
        tag.AddSV(r_flags)
    return tag


def GLOB(*ss):
    """
    gather all files belonging to module, if argument specified in ss does not beneath 
    the directory of module, raise BrocArgumentIllegalError 
    Args:
        ss : a variable number of string objects, support regrex
    Returns:
        string containing the relative path of files or directories, each path separeated by blank character
    """
    if sys.argv[0]=='PLANISH':
        return ""
    env = Environment.GetCurrent()
    strs=[]
    for s in ss:
        ps = string.split(s)
        for p in ps:
            if p.startswith(os.path.join("broc_out", env.ModuleCVSPath())):
                norm_path = os.path.normpath(os.path.join(env.Workspace(), p))
                len_abandon = len(os.path.normpath(env.Workspace()))
            else:
                norm_path = os.path.normpath(os.path.join(env.BrocDir(), p))
                len_abandon = len(os.path.normpath(env.BrocDir()))
            if env.ModuleCVSPath() not in norm_path:
                raise NotInSelfModuleError(norm_path, env.ModuleCVSPath())
            else:
                gs = glob.glob(norm_path)
                gs.sort()
                file_list = list()
                for file_name in gs:
                    # remove workspace path from file path
                    file_list.append(file_name[len_abandon + 1:])
                strs.extend(file_list)
    if not strs:
        raise BrocArgumentIllegalError("GLOB(%s) is empty" % str(ss))

    return str(' '.join(strs))


def _ParseNameAndArgs(*ss):
    """
    parse a variable number of arguments, all string arguments in ss will be regarded as source file, 
    and the rest of arguments will be regarded as compile options
    Args:
        ss : a variable number of arguments
    Return:
        a tuple object composed of two iterms: first one is a group of source files, and second are the TagVector objects
    """
    files = []
    args = []
    for s in ss:
        if isinstance(s, str) or isinstance(s, unicode):
            files.extend(string.split(string.strip(s)))
        else:
            args.append(s)
    return (files, args)


def CONFIGS(s):
    """
    gather dependency modules
    """
    if not sys.argv[0]=='PLANISH':
        return
    print(s)

def Sources(*ss):
    """
    create a group of Sources object
    all source file should beneathes the directory of module, if not will raise NotInSelfModuleError
    avoid containing wildcard in ss, so you can use GLOB gathering files firstly, and take the result of GLOB as ss
    Args:
        ss : a variable number of artuments, all string arguments in ss will be regarded as 
             source file, the file can be .c, .cpp and so on, and the reset arguments are 
             regarded as compile flags
    Returns:
        TagSources Object
    """
    tag = SyntaxTag.TagSources()
    if sys.argv[0]=='PLANISH':
        return tag
    # FIX ME: you can extend wildcard
    files, args = _ParseNameAndArgs(*ss)
    env = Environment.GetCurrent()
    all_files = GLOB(" ".join(files)).split(' ')
    for f in all_files:
        if not f.startswith(os.path.join("broc_out", env.ModuleCVSPath())):
            f = os.path.join(env.ModuleCVSPath(), f)
        src = _CreateSources(f, args)
        tag.AddSV(src)

    return tag


def _CreateSources(_file, *args):
    """
    create a Source object
    Args:
        _file : the cvs path of source code file
        _args : a variable number of TagVector object
    Return:
        the Source object
    """
    src = None
    env = Environment.GetCurrent()
    _, ext = os.path.splitext(_file)
    if ext in Source.CSource.EXTS:
        src = Source.CSource(_file, env, args)
    elif ext in Source.CXXSource.EXTS:
        src = Source.CXXSource(_file, env, args)
    else:
        raise BrocArgumentIllegalError("don't support file(%s) whose ext is(%s)" % (_file, ext))
    env.AppendSource(src)
    return src
        

def APPLICATION(name, sources, *args):
    """
    create one Application object
    Args:
        name : the name of target
        sources : the SyntaxTag.TagSource object
        args: a variable number of SyntaxTag.TagLDFlags and SyntaxTag.TagLibs 
    """
    if sys.argv[0]=='PLANISH':
        return
    # to check name of result file 
    if not Function.CheckName(name):
        raise BrocArgumentIllegalError("name(%s) in APPLICATION is illegal" % name)
    
    tag_links = SyntaxTag.TagLDFlags()
    tag_libs = SyntaxTag.TagLibs()
    for arg in args:
        if isinstance(arg, SyntaxTag.TagLDFlags):
            tag_links.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagLibs):
            tag_libs.AddSVs(arg.V())
        else:
            raise BrocArgumentIllegalError("In APPLICATION(%s) don't support %s" % (name, arg))
        
    env = Environment.GetCurrent()
    app = Target.Application(name, env, sources, tag_links, tag_libs)
    if not env.AppendTarget(app):
        raise BrocArgumentIllegalError("APPLICATION(%s) exists already" % name)


def STATIC_LIBRARY(name, *args):
    """
    create one StaticLibrary object
    Args:
        name : the name of .a file
        args : the variable number of SyntagTag.TagSources, SyntaxTag.TagLibs object
    """
    if sys.argv[0]=='PLANISH':
        return
    # to check name of result file
    if not Function.CheckName(name):
        raise BrocArgumentIllegalError("name(%s) in STATIC_LIBRARY is illegal" % name)

    tag_libs = SyntaxTag.TagLibs()
    tag_sources = SyntaxTag.TagSources()
    for arg in args:
        if isinstance(arg, SyntaxTag.TagSources):
            tag_sources.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagLibs):
            tag_libs.AddSVs(arg.V())
        else:
            raise BrocArgumentIllegalError("arguments (%s) in STATIC_LIBRARY is illegal" % \
                                          type(arg))
    env = Environment.GetCurrent()
    lib = Target.StaticLibrary(name, env, tag_sources, tag_libs)
    if len(tag_sources.V()):
        if not env.AppendTarget(lib):
            raise BrocArgumentIllegalError("STATIC_LIBRARY(%s) exists already" % name)
    else:
        # .a file has been built already, just copy it from code directory to output directory
        lib.DoCopy()
    

def UT_APPLICATION(name, sources, *args):
    """
    create one UT Application object
    Args:
        name : the name of target
        sources : the SyntaxTag.TagSource object
        args : a variable number of SyntaxTag.TagLinkLDFlags, SyntaxTag.TagLibs, SyntaxTag.TagUTArgs 
    """
    if sys.argv[0]=='PLANISH':
        return
    # to check name of result file
    if not Function.CheckName(name):
        raise BrocArgumentIllegalError("name(%s) in UT_APPLICATION is illegal")

    tag_links = SyntaxTag.TagLDFlags()
    tag_libs = SyntaxTag.TagLibs()
    tag_utargs = SyntaxTag.TagUTArgs()
    for arg in args:
        if isinstance(arg, SyntaxTag.TagLDFlags):
            tag_links.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagLibs):
            tag_libs.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagUTArgs):
            tag_utargs.AddSVs(arg.V())
        else:
            raise BrocArgumentIllegalError("In UT_APPLICATION(%s) don't support %s" % (name, arg))
    env = Environment.GetCurrent()
    app = Target.UTApplication(name, env, sources, tag_links, tag_libs, tag_utargs)
    if not env.AppendTarget(app):
        raise BrocArgumentIllegalError("UT_APPLICATION(%s) exists already" % name)


def ProtoFlags(*ss):
    """
    add the command options for protoc
    Args:
       ss : a variable number of string objects 
            ss may contain multiple string objects, each object can contain multiple options
            one option may be:
            1. option may contains $WORKSPACE, $OUT Macros value
    Returns:
        return a 
    """
    tag = SyntaxTag.TagProtoFlags()
    if sys.argv[0]=='PLANISH':
        return tag
    env = Environment.GetCurrent()
    for s in ss:
        ps = s.split()
        for x in ps:
            if "$WORKSPACE" in x:
                tag.AddSV(x.replace("$WORKSPACE/", '')) 
            elif "$OUT" in x:
                tag.AddSV(x.replace("$OUT", env.OutputPath()))
            elif "$OUT_ROOT" in x:
                tag.AddSV(x.replace("$OUT_ROOT", env.OutputRoot()))
            else: 
                tag.AddSV(x)
    return tag


def PROTO_LIBRARY(name, files, *args):
    """
    compile proto files into a static library .a
    when parse proto files failed, raise Exception BrocProtoError
    Args:
        name: the name of proto static library
        files: a string sperearated by blank character, representing the relative path of proto files
        args: a variable number of SyntaxTag.TagProtoFlags, SyntaxTag.TagInclude, SyntaxTag.CppFlags, SyntaxTag.CXXFlags, SyntaxTag.TagLibs
    """
    if sys.argv[0]=='PLANISH':
        return
    # check validity of name
    if not Function.CheckName(name):
        raise BrocArgumentIllegalError("name(%s) PROTO_LIBRARY is illegal" % name)

    # check proto file whether belongs to  module
    proto_files = files.split()
    env = Environment.GetCurrent()
    for _file in proto_files:
        abs_path = os.path.normpath(os.path.join(env.BrocDir(), _file))
        if not env.ModulePath() in abs_path:
            raise NotInSelfModuleError(abs_path, env.ModulePath())
     
    # to check args
    tag_protoflags = SyntaxTag.TagProtoFlags()
    tag_cppflags = SyntaxTag.TagCppFlags()
    tag_cxxflags = SyntaxTag.TagCxxFlags()
    tag_libs = SyntaxTag.TagLibs()
    tag_include = SyntaxTag.TagInclude()
    for arg in args:
        if isinstance(arg, SyntaxTag.TagProtoFlags):
            tag_protoflags.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagCppFlags):
            tag_cppflags.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagCxxFlags):
            tag_cxxflags.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagLibs):
            tag_libs.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagInclude):
            tag_include.AddSVs(arg.V())
        else:
            raise BrocArgumentIllegalError("don't support tag(%s) in PROTO_LIBRARY in %s" \
                                             % (str(arg), env.BrocPath()))
   
    include = set()
    source = set()
    for f in proto_files:
        root, _ = os.path.splitext(f)
        result_file = os.path.join(os.path.join('broc_out', env.ModuleCVSPath()), \
                "%s.pb.cc" % root)
        include.add(os.path.dirname(result_file))
        if os.path.dirname(f):
            tag_include.AddV(os.path.join(env.ModuleCVSPath(), os.path.dirname(f)))
        source.add(result_file)
    protolib = Target.ProtoLibrary(env, files, tag_include, tag_protoflags)
    ret, msg = protolib.PreAction()
    if not ret:
        raise BrocProtoError(msg)

    tag_include.AddSVs(include)
    broc_out = os.path.join("broc_out", env.BrocCVSDir())
    if broc_out not in tag_include.V():
        tag_include.AddV(os.path.join("broc_out", env.BrocCVSDir()))
    tag_sources = Sources(" ".join(list(source)), tag_include, tag_cppflags, tag_cxxflags)
    if not env.AppendTarget(Target.StaticLibrary(name, env, tag_sources, tag_libs)):
        raise BrocArgumentIllegalError("PROTO_LIBRARY(%s) name exists already" % name)
    return protolib


def UTArgs(v):
    """
    tag UTArgs
    """
    tag = SyntaxTag.TagUTArgs()
    if sys.argv[0]=='PLANISH':
        return tag
    tag.AddV(v)
    return tag


def DIRECOTYR(v): 
    """
    Add sub directory
    Args:
       v : the name of subdirectory, v is relative path
    """   
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    env.AppendSubDirectory(os.path.normpath(v))


def PUBLISH(srcs, out_dir):
    """
    copy srcs to out_dir
    Args:
        srcs: the files needed to move should belongs to the module
        out_dir: the destination directory that must start with $OUT
        if argument is illeagl, raise BrocArgumentIllegalError 
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    if not out_dir.strip().startswith('$OUT'):
        raise BrocArgumentIllegalError("PUBLISH argument dst(%s) must start with $OUT \
                                         in %s " % (out_dir, env.BrocPath()))
    src_lists = srcs.split()
    for s in src_lists:
        abs_s = os.path.normpath(os.path.join(env.BrocDir(), s))
        if env.ModulePath() not in abs_s:
            raise NotInSelfModuleError(abs_s, env.ModulePath())

    env.AddPublish(srcs, out_dir)


def SVN_PATH():
    """
    return local path of module
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    return env.SvnPath()


def SVN_URL():
    """
    return url of module
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    return env.SvnUrl()


def SVN_REVISION():
    """
    return revision of module
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    return env.SvnRevision()


def SVN_LAST_CHANGED_REV():
    """
    return last changed rev
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    return env.SvnLastChangedRev()


def GIT_PATH():
    """
    return local path of module
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    return env.GitPath()
        
    
def GIT_URL():
    """
    return url of module
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    return env.GitUrl()


def GIT_BRANCH():
    """
    return the branch name of module
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    return env.GitBranch()


def GIT_COMMIT_ID():
    """
    return the commit id of module
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    return env.GitCommitID()


def GIT_TAG():
    """
    return the tag of module
    """
    if sys.argv[0]=='PLANISH':
        return
    env = Environment.GetCurrent()
    return env.GitTag()

