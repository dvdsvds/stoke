# Sinatra

Create a Sinatra project via:

```bash
stoke init sinatra
```

Sinatra is a lightweight DSL for building web apps in Ruby.

## Prompts

- **Project name**: directory name for the project

## Generated files

    myapp/
    ├── stoke.toml
    ├── Gemfile
    └── src/
        └── main.rb           # Sinatra entry point

## Dependencies

- `sinatra` `~> 4.0` (declared in `Gemfile`, installed via `bundle install`)

## Default settings

- **Port**: `4567` (Sinatra's default, set explicitly via `set :port, 4567`)
- **Endpoints**:
  - `GET /` → `Hello from Sinatra + stoke!`
  - `GET /hello/:name` → `Hello, {name}!`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:4567/`

## Customization

- Change port: edit `set :port, 4567` in `src/main.rb`
- Add routes: add `get "/path" do ... end` / `post "/path" do ... end` blocks
- Add gems: add to `Gemfile`, then `stoke build` to `bundle install`

## Why not Rails?

Rails apps are started with `bin/rails server`, a separate CLI subcommand — not by directly executing an entry script. That doesn't fit stoke's current run model (`ruby <entry>` / `bundle exec ruby <entry>`), so `stoke run` would just print Rails' CLI help instead of starting a server. Sinatra fits naturally because the classic-style app starts its own server the moment the entry file itself runs.
