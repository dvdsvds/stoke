# C#

stoke supports C# projects using the standard `dotnet build` and `dotnet run` tooling.

## Requirements

- .NET SDK ([dotnet.microsoft.com/download](https://dotnet.microsoft.com/download))
- `stoke install --language=csharp` is not supported yet — install the .NET SDK directly

## Configuration

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "csharp"
```

That's it. .NET handles its own dependency management via the `.csproj` file and NuGet.

## How it works

- `stoke build` runs `dotnet build --output .stoke/csharp/<target>`
- `stoke run` executes the built binary from that output directory
- The assembly name is taken from the first `*.csproj` file found in the project root
- `--force` maps to `dotnet build --no-incremental`

## Example

Create a new C# project:

```bash
mkdir myapp
cd myapp
stoke init
```

Select `C#` from the language menu. stoke will:

- Create `stoke.toml`
- Run `dotnet new console --name myapp` (falls back to a hand-written `.csproj` if `dotnet` isn't installed)
- Generate `Program.cs` with a hello-world example

Then:

```bash
stoke build
stoke run
```

## Framework scaffolding

```bash
stoke init aspnet-core    # ASP.NET Core — minimal API template
```

See [Frameworks](../../frameworks/en/overview.md) for details.

## Notes

- `bin/` and `obj/` (MSBuild's own output/intermediate folders) are added to `.gitignore` alongside `.stoke/`
- Only one `.csproj` per project is currently supported for assembly-name detection
