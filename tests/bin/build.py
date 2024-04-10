import bpy
import os
import shutil
import tempfile


def copytree(src, dst, symlinks=False, ignore=None):
    """Custom copytree implementation to handle cases
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)


def new_folder(path):
    """Create a new folder if it doesn't exist yet
    """
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


# Remove old build files
try:
    os.remove(bpy.path.abspath('//test'))
except Exception:
    pass
try:
    shutil.rmtree(bpy.path.abspath('//3.6'))
except Exception:
    pass
try:
    shutil.rmtree(bpy.path.abspath('//license'))
except Exception:
    pass


path = bpy.path.abspath('//')
OUTPUT_PATH = bpy.path.abspath('//test')

def CopyPythonLibs(dst, overwrite_lib, report=print):
    import platform

    # use python module to find python's libpath
    src = os.path.dirname(platform.__file__)

    # dst points to lib/, but src points to current python's library path, eg:
    #  '/usr/lib/python3.2' vs '/usr/lib'
    # append python's library dir name to destination, so only python's
    # libraries would be copied
    if os.name == 'posix':
        dst = os.path.join(dst, os.path.basename(src))

    if os.path.exists(src):
        write = False
        if os.path.exists(dst):
            if overwrite_lib:
                shutil.rmtree(dst)
                write = True
        else:
            write = True
        if write:
            shutil.copytree(src, dst, ignore=lambda dir, contents: [i for i in contents if i == '__pycache__'])
    else:
        report({'WARNING'}, "Python not found in %r, skipping python copy" % src)


def WriteRuntime():
    import struct

    # Setup main folders
    blender_dir = os.path.dirname(bpy.app.binary_path)
    runtime_dir = os.path.dirname(OUTPUT_PATH)

    # Extract new version string. Only take first 3 digits (i.e 3.0)
    string = bpy.app.version_string.split()[0]
    version_string = string[:3]

    # Create temporal directory
    tempdir = tempfile.mkdtemp()
    blender_bin_path = bpy.app.binary_path
    blender_bin_dir = os.path.dirname(blender_bin_path)
    ext = os.path.splitext(blender_bin_path)[-1].lower()
    blenderplayer_name = 'blenderplayer'
    player_path_temp = os.path.join(blender_bin_dir, blenderplayer_name + ext)

    # Get the player's binary and the offset for the blend
    file = open(player_path_temp, 'rb')
    player_d = file.read()
    offset = file.tell()
    file.close()

    # Create a tmp blend file (Blenderplayer doesn't like compressed blends)
    blend_path = os.path.join(tempdir, bpy.path.clean_name(OUTPUT_PATH))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path,
                                relative_remap=False,
                                compress=False,
                                copy=True,
                                )

    # Get the blend data
    blend_file = open(blend_path, 'rb')
    blend_d = blend_file.read()
    blend_file.close()

    # Get rid of the tmp blend, we're done with it
    os.remove(blend_path)
    os.rmdir(tempdir)

    # Create a new file for the bundled runtime
    output = open(OUTPUT_PATH, 'wb')

    # Write the player and blend data to the new runtime
    print("Writing runtime...", end=" ")
    output.write(player_d)
    output.write(blend_d)

    # Store the offset (an int is 4 bytes, so we split it up into 4 bytes and save it)
    output.write(struct.pack('B', (offset>>24)&0xFF))
    output.write(struct.pack('B', (offset>>16)&0xFF))
    output.write(struct.pack('B', (offset>>8)&0xFF))
    output.write(struct.pack('B', (offset>>0)&0xFF))

    # Stuff for the runtime
    output.write(b'BRUNTIME')
    output.close()

    print("done")

    # Make the runtime executable on Linux
    if os.name == 'posix':
        os.chmod(OUTPUT_PATH, 0o755)

    print("Copying Python files...", end=" ")
    py_folder = os.path.join(version_string, "python", "lib")
    dst = os.path.join(runtime_dir, py_folder)
    CopyPythonLibs(dst, True, print)
    print("done")

    # Copy datafiles folder
    print("Copying datafiles...", end=" ")
    datafiles_folder = os.path.join(version_string, "datafiles", "gamecontroller")
    src = os.path.join(blender_dir, datafiles_folder)
    dst = os.path.join(runtime_dir, datafiles_folder)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    datafiles_folder = os.path.join(version_string, "datafiles", "colormanagement")
    src = os.path.join(blender_dir, datafiles_folder)
    dst = os.path.join(runtime_dir, datafiles_folder)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    datafiles_folder = os.path.join(version_string, "datafiles", "fonts")
    src = os.path.join(blender_dir, datafiles_folder)
    dst = os.path.join(runtime_dir, datafiles_folder)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    datafiles_folder = os.path.join(version_string, "datafiles", "studiolights")
    src = os.path.join(blender_dir, datafiles_folder)
    dst = os.path.join(runtime_dir, datafiles_folder)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print("done")

    print("Copying scripts and modules...", end=" ")
    scripts_folder = os.path.join(version_string, "scripts")
    src = os.path.join(blender_dir, scripts_folder)
    dst = os.path.join(runtime_dir, scripts_folder)
    shutil.copytree(src, dst)
    print("done")

    # Copy license folder
    print("Copying UPBGE license folder...", end=" ")
    src = os.path.join(blender_dir, "license")
    dst = os.path.join(runtime_dir, "engine.license")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    license_folder = os.path.join(runtime_dir, "engine.license")
    src = os.path.join(blender_dir, "copyright.txt")
    dst = os.path.join(license_folder, "copyright.txt")
    shutil.copy2(src, dst)
    print("done")


import time
print("Saving runtime to %r" % bpy.path.abspath('//'))
start_time = time.time()
WriteRuntime()
print("Finished in %.4fs" % (time.time() - start_time))

blpath = bpy.utils.resource_path(type='LOCAL')
new_folder(bpy.path.abspath('//lib'))
copytree(os.path.join(blpath, '..', 'lib'), bpy.path.abspath('//lib'))
