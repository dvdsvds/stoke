# Ruby

stoke supports Ruby projects using the Ruby interpreter and Bundler.

## Requirements

- Ruby ([ruby-lang.org/en/downloads](https://www.ruby-lang.org/en/downloads/))
- Bundler, if the project has a `Gemfile` (`gem install bundler`)

## Configuration

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "ruby"
entry = "src/main.rb"
```

## How it works

- `stoke build` runs `bundle install` if a `Gemfile` exists in the project root (skipped otherwise)
- `stoke run` executes `bundle exec ruby <entry>` if a `Gemfile` is present, otherwise plain `ruby <entry>`
- Dependencies are managed via `Gemfile` / `Gemfile.lock`

## Example

Create a new Ruby project:

```bash
mkdir myapp
cd myapp
stoke init
```

Select `Ruby` from the language menu. stoke will:

- Create `stoke.toml`
- Generate `src/main.rb` with a hello-world example

Then:

```bash
stoke build
stoke run
```

## Framework scaffolding

```bash
stoke init sinatra      # Sinatra — lightweight DSL for web apps
```

See [Frameworks](../../frameworks/overview.md) for details.

## Notes

- stoke reads the `entry` field from `stoke.toml` and runs it with Ruby (or `bundle exec ruby`)
- `.bundle/` and `vendor/bundle/` are added to `.gitignore` alongside `.stoke/`
- `stoke init` optionally prompts for a Ruby version to pin (`--version` in [non-interactive mode](../../commands/init.md#non-interactive-mode-ci-team-onboarding)). If given, it writes `.ruby-version`, which rbenv/rvm/asdf/chruby read automatically to select that version. Leave it blank to skip pinning — note this only takes effect if the team actually uses one of those version managers.
- Rails isn't offered as a framework scaffold — it starts via `bin/rails server` rather than running a single entry script directly, which doesn't fit stoke's current run model. Sinatra was chosen because a Sinatra app starts its own server when the entry file itself is executed.
