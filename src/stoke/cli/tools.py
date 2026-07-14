"""python/java/c/cpp list 명령어."""
from stoke.python_versions import detect_all


def cmd_python_list():
    installs = detect_all()
    if not installs:
        print("No Python installations detected.")
        return
    print(f"Detected {len(installs)} Python installation(s):\n")
    for install in installs:
        default_mark = " (default)" if install.is_default else ""
        print(f"  Python {install.version}{default_mark}")
        print(f"    -> {install.executable}")


def cmd_java_list():
    from stoke.java_versions import detect_all as detect_java
    installs = detect_java()
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


def cmd_c_list():
    from stoke.c_versions import detect_all as detect_c
    installs = [i for i in detect_c() if i.kind == "c"]
    if not installs:
        print("No C compiler detected.")
        print("Install gcc or ensure it's in your PATH.")
        return
    print(f"Detected {len(installs)} C compiler(s):\n")
    for install in installs:
        default_mark = " (default)" if install.is_default else ""
        print(f"  gcc {install.version} (major: {install.major_version}){default_mark}")
        print(f"    executable: {install.executable}")
        print()


def cmd_cpp_list():
    from stoke.c_versions import detect_all as detect_c
    installs = [i for i in detect_c() if i.kind == "cpp"]
    if not installs:
        print("No C++ compiler detected.")
        print("Install g++ or ensure it's in your PATH.")
        return
    print(f"Detected {len(installs)} C++ compiler(s):\n")
    for install in installs:
        default_mark = " (default)" if install.is_default else ""
        print(f"  g++ {install.version} (major: {install.major_version}){default_mark}")
        print(f"    executable: {install.executable}")
        print()