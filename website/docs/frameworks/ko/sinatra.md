# Sinatra

Sinatra 프로젝트 생성:

```bash
stoke init sinatra
```

Sinatra는 Ruby로 웹 앱을 만드는 경량 DSL입니다.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름

## 생성 파일

    myapp/
    ├── stoke.toml
    ├── Gemfile
    └── src/
        └── main.rb           # Sinatra 진입점

## 의존성

- `sinatra` `~> 4.0` (`Gemfile`에 선언, `bundle install`로 설치)

## 기본 설정

- **Port**: `4567` (Sinatra 기본값, `set :port, 4567`로 명시)
- **Endpoints**:
  - `GET /` → `Hello from Sinatra + stoke!`
  - `GET /hello/:name` → `Hello, {name}!`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:4567/`

## 커스터마이징

- 포트 변경: `src/main.rb`의 `set :port, 4567` 수정
- 라우트 추가: `get "/path" do ... end` / `post "/path" do ... end` 블록 추가
- gem 추가: `Gemfile`에 추가 후 `stoke build`로 `bundle install`

## 왜 Rails가 아닌가

Rails 앱은 별도 CLI 서브커맨드인 `bin/rails server`로 실행됩니다 — entry 스크립트를 직접 실행하는 방식이 아니에요. 이건 지금 stoke의 실행 모델(`ruby <entry>` / `bundle exec ruby <entry>`)에 안 맞아서, `stoke run`을 돌리면 서버가 안 뜨고 Rails CLI 도움말만 찍힙니다. Sinatra는 classic 스타일 앱이 entry 파일 실행 즉시 자체 서버를 띄우는 구조라 이 모델에 정확히 맞습니다.
