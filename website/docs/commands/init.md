# stoke init

Create a new stoke project interactively.

## Usage

```bash
stoke init
```

Runs an interactive wizard in the current directory.

## What it does

The wizard asks:

1. **Project name** — defaults to the current folder name
2. **Language** — Python, Java, C, or C++
3. **Language version** — Python 3.12, Java 25, C11, C++20, etc.
4. **Entry point / main class** — depending on the language
5. **Dependencies** — optional

Then it generates:

- `stoke.toml` — project configuration
- `src/` — source directory
- A hello-world source file

## Example: C++ project
$ mkdir myapp && cd myapp
$ stoke init
Project name [myapp]:
Language [python/java/c/cpp]: cpp
C++ standard [17/20/23] [20]:
Executable name [myapp]:
Install vcpkg for C/C++ library management? [y/N]: n
Created:
stoke.toml
src/main.cpp
Try:
stoke build
stoke run

Generated `stoke.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "cpp"
sources = ["src/**/*.cpp"]
cpp_standard = "c++20"
```

## Example: Python project
$ mkdir myapp && cd myapp
$ stoke init
Project name [myapp]:
Language [python/java/c/cpp]: python
Python version [3.10/3.11/3.12/3.13]: 3.12
Entry file [src/main.py]:
Created:
stoke.toml
src/main.py

Generated `stoke.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "python"
python_version = "3.12"
entry = "src/main.py"
sources = ["src/**/*.py"]
```

## Example: Java project
$ mkdir myapp && cd myapp
$ stoke init
Project name [myapp]:
Language [python/java/c/cpp]: java
Java version [17/21/25]: 25
Package [com.myapp]:
Main class [Main]:
Created:
stoke.toml
src/main/java/com/myapp/Main.java

Generated `stoke.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "java"
java_version = "25"
sources = ["src/main/java/**/*.java"]
main_class = "com.myapp.Main"
```

## After init

Build and run:

```bash
stoke build
stoke run
```

## Related

- [Quick Start](../getting-started/quick-start.md)
- [`stoke.toml` reference](../configuration/stoke-toml.md)