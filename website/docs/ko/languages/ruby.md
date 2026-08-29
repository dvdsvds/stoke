# Ruby

stoke는 Ruby 인터프리터와 Bundler를 사용해 Ruby 프로젝트를 지원합니다.

## 요구사항

- Ruby ([ruby-lang.org/en/downloads](https://www.ruby-lang.org/en/downloads/))
- 프로젝트에 `Gemfile`이 있으면 Bundler 필요 (`gem install bundler`)

## 설정

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "ruby"
entry = "src/main.rb"
```

## 동작 방식

- `stoke build`는 프로젝트 루트에 `Gemfile`이 있으면 `bundle install` 실행 (없으면 스킵)
- `stoke run`은 `Gemfile`이 있으면 `bundle exec ruby <entry>`, 없으면 그냥 `ruby <entry>` 실행
- 의존성은 `Gemfile` / `Gemfile.lock`으로 관리

## 예시

새 Ruby 프로젝트 생성:

```bash
mkdir myapp
cd myapp
stoke init
```

언어 메뉴에서 `Ruby` 선택. stoke가:

- `stoke.toml` 생성
- Hello World가 있는 `src/main.rb` 생성

그 다음:

```bash
stoke build
stoke run
```

## 프레임워크 스캐폴딩

```bash
stoke init sinatra      # Sinatra — 경량 웹 앱 DSL
```

자세한 내용은 [Frameworks](../../frameworks/overview.md) 참조.

## 참고

- stoke는 `stoke.toml`의 `entry` 필드를 읽어서 Ruby(또는 `bundle exec ruby`)로 실행
- `.stoke/`와 함께 `.bundle/`, `vendor/bundle/`도 `.gitignore`에 자동 추가됨
- `stoke init`은 선택적으로 pin할 Ruby 버전을 물어봄 ([비대화형 모드](../../commands/init.md#non-interactive-mode-ci-team-onboarding)에서는 `--version`). 입력하면 `.ruby-version`이 생성되고, rbenv/rvm/asdf/chruby가 이 파일을 자동으로 읽어서 그 버전을 사용함. 비워두면 pin 안 함 — 단, 팀에서 이런 버전 매니저를 실제로 쓸 때만 효과가 있음
- Rails는 프레임워크 스캐폴딩으로 제공 안 함 — Rails는 entry 스크립트를 직접 실행하는 게 아니라 `bin/rails server`로 띄우는 구조라 지금 stoke의 실행 모델에 안 맞음. Sinatra는 entry 파일 자체를 실행하면 서버가 뜨는 구조라 선택함.
