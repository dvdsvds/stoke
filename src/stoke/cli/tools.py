"""python/java/c/cpp list 명령어."""
from stoke.config import find_config_file
from stoke.languages.python.versions import detect_all

def _current_project_root():
    try:
        return find_config_file().parent
    except FileNotFoundError:
        return None

def cmd_python_list():
    installs = detect_all(_current_project_root())
    if not installs:
        print("No Python installations detected.")
        return
    print(f"Detected {len(installs)} Python installation(s):\n")
    for install in installs:
        default_mark = " (default)" if install.is_default else ""
        print(f"  Python {install.version}{default_mark}")
        print(f"    -> {install.executable}")

def cmd_java_list():
    from stoke.languages.java.versions import detect_all as detect_java
    installs = detect_java(_current_project_root())
    if not installs:
        print("No JDK detected.")
        print("Install a JDK or set the JAVA_HOME environment variable.")
        return
    print(f"Detected {len(installs)} JDK(s):\n")
    for install in installs:
        default_mark = " (default)" if install.is_default else ""
        print(f"  Java {install.version} (major: {install.major_version}){default_mark}")
        print(f"    JAVA_HOME: {install.java_home}")
        print(f"    javac:     {install.javac}")
        print(f"    java:      {install.java}")
        print()

_COMPILER_LABEL = {"gcc": "gcc", "clang": "clang", "msvc": "cl (MSVC)"}

def cmd_c_list():
    from stoke.languages.c.versions import detect_all as detect_c
    installs = [i for i in detect_c(_current_project_root()) if i.kind == "c"]
    if not installs:
        print("No C compiler detected.")
        print("Install gcc/clang, or Visual Studio Build Tools (MSVC) for cl.exe.")
        return
    print(f"Detected {len(installs)} C compiler(s):\n")
    for install in installs:
        default_mark = " (default)" if install.is_default else ""
        label = _COMPILER_LABEL.get(install.family, install.family)
        print(f"  {label} {install.version} (major: {install.major_version}){default_mark}")
        print(f"    executable: {install.executable}")
        print()

def cmd_cpp_list():
    from stoke.languages.c.versions import detect_all as detect_c
    installs = [i for i in detect_c(_current_project_root()) if i.kind == "cpp"]
    if not installs:
        print("No C++ compiler detected.")
        print("Install g++/clang++, or Visual Studio Build Tools (MSVC) for cl.exe.")
        return
    print(f"Detected {len(installs)} C++ compiler(s):\n")
    for install in installs:
        default_mark = " (default)" if install.is_default else ""
        label = _COMPILER_LABEL.get(install.family, install.family)
        print(f"  {label} {install.version} (major: {install.major_version}){default_mark}")
        print(f"    executable: {install.executable}")
        print()