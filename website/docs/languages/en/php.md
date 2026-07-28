# PHP

stoke supports PHP projects using the PHP interpreter and Composer.

## Requirements

- PHP ([php.net/downloads](https://www.php.net/downloads))
- Composer, if the project has a `composer.json` ([getcomposer.org](https://getcomposer.org/download/))

## Configuration

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "php"
entry = "src/main.php"
```

## How it works

- `stoke build` runs `composer install` if a `composer.json` exists in the project root (skipped otherwise)
- `stoke run` executes `php <entry>`
- Dependencies are managed via `composer.json` / `composer.lock`

## Example

Create a new PHP project:

```bash
mkdir myapp
cd myapp
stoke init
```

Select `PHP` from the language menu. stoke will:

- Create `stoke.toml`
- Generate `src/main.php` with a hello-world example

Then:

```bash
stoke build
stoke run
```

## Framework scaffolding

```bash
stoke init slim      # Slim Framework — lightweight PSR-7 micro-framework
```

See [Frameworks](../../frameworks/en/overview.md) for details.

## Notes

- stoke reads the `entry` field from `stoke.toml` and runs it with `php`
- `vendor/` is added to `.gitignore` alongside `.stoke/`
- `stoke init` optionally prompts for a PHP version to pin (`--version` in [non-interactive mode](../../commands/init.md#non-interactive-mode-ci-team-onboarding)). If given, it writes a `composer.json` with a `require.php` constraint — `composer install` (which then runs automatically as part of `stoke build`, since `composer.json` now exists) fails if the local PHP version doesn't satisfy it. Leave it blank to skip pinning; note this means a `composer.json`-less project stays composer-free until you add one yourself.
- Laravel isn't offered as a framework scaffold — it's served via `php artisan serve` rather than by executing an entry file directly, which doesn't fit stoke's current run model. Slim's `public/index.php` still needs PHP's built-in dev server (`php -S`) to actually serve requests; see the [Slim framework page](../../frameworks/en/slim.md) for the manual step.
