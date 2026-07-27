# PHP

stoke는 PHP 인터프리터와 Composer를 사용해 PHP 프로젝트를 지원합니다.

## 요구사항

- PHP ([php.net/downloads](https://www.php.net/downloads))
- 프로젝트에 `composer.json`이 있으면 Composer 필요 ([getcomposer.org](https://getcomposer.org/download/))

## 설정

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "php"
entry = "src/main.php"
```

## 동작 방식

- `stoke build`는 프로젝트 루트에 `composer.json`이 있으면 `composer install` 실행 (없으면 스킵)
- `stoke run`은 `php <entry>` 실행
- 의존성은 `composer.json` / `composer.lock`으로 관리

## 예시

새 PHP 프로젝트 생성:

```bash
mkdir myapp
cd myapp
stoke init
```

언어 메뉴에서 `PHP` 선택. stoke가:

- `stoke.toml` 생성
- Hello World가 있는 `src/main.php` 생성

그 다음:

```bash
stoke build
stoke run
```

## 프레임워크 스캐폴딩

```bash
stoke init slim      # Slim Framework — 경량 PSR-7 마이크로 프레임워크
```

자세한 내용은 [Frameworks](../../frameworks/ko/overview.md) 참조.

## 참고

- stoke는 `stoke.toml`의 `entry` 필드를 읽어서 `php`로 실행
- `.stoke/`와 함께 `vendor/`도 `.gitignore`에 자동 추가됨
- Laravel은 프레임워크 스캐폴딩으로 제공 안 함 — entry 파일을 직접 실행하는 게 아니라 `php artisan serve`로 띄우는 구조라 지금 stoke의 실행 모델에 안 맞음. Slim의 `public/index.php`도 실제로 요청을 처리하려면 PHP 내장 개발 서버(`php -S`)가 필요함 — 수동 실행 단계는 [Slim 프레임워크 페이지](../../frameworks/ko/slim.md) 참조.
