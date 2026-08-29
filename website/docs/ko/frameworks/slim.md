# Slim Framework

Slim Framework 프로젝트 생성:

```bash
stoke init slim
```

Slim은 PHP용 경량 PSR-7 마이크로 프레임워크입니다.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름

## 생성 파일

    myapp/
    ├── stoke.toml
    ├── composer.json
    └── public/
        └── index.php          # Slim 진입점

## 의존성

- `slim/slim` `^4.0`
- `slim/psr7` `^1.6` (PSR-7 구현체)

## 기본 설정

- **Endpoints**:
  - `GET /` → `Hello from Slim + stoke!`
  - `GET /hello/{name}` → `Hello, {name}!`

## 실행

Slim은 Sinatra처럼 스스로 서버를 띄우는 구조가 아니라서, PHP 내장 개발 서버가 필요합니다 — `stoke run`만으로는 부족합니다:

```bash
cd myapp
composer install               # 스캐폴딩 중 이미 실행됐으면 생략 가능
php -S localhost:8000 -t public
```

브라우저: `http://localhost:8000/`

!!! note
    `stoke build`(composer install)와 `stoke run`은 그대로 동작하지만, `stoke run`은 앞단에 HTTP 서버 없이 `public/index.php`를 CLI SAPI로 한 번 실행하고 끝나는 거라 라우팅할 요청 자체가 없습니다. 실제 개발에는 위의 `php -S`를 사용하세요.

## 커스터마이징

- 라우트 추가: `public/index.php`에 `$app->get(...)` / `$app->post(...)` 호출 추가
- 미들웨어 추가: `$app->add(...)` 사용
- 프로젝트가 커지면 라우트를 별도 파일로 분리 (Slim 관례: `index.php`에서 require하는 `routes/` 디렉토리)
