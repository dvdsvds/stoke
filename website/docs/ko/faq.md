# 자주 묻는 질문

## 일반

### stoke가 뭔가요?

Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript의 워크플로우를 하나로 통일하는 빌드 도구입니다. 프로젝트마다 `stoke.toml` 하나, 모든 언어에 하나의 명령어 세트.

### 왜 언어별 도구를 안 쓰나요?

pip, Maven, Make, Cargo 같은 언어별 도구들은 훌륭합니다. 하지만 여러 언어를 넘나들며 작업하면, 어떤 명령어가 뭘 빌드하는지 기억하고, 각 생태계를 따로 설정하고, IDE 셋업을 맞추는 게 마찰이 됩니다.

stoke는 기존 도구를 대체하지 않으면서 일관된 인터페이스를 제공합니다. 내부적으로 stoke는 pip, javac, Maven, gcc/clang, vcpkg, `go build`, npm을 그대로 씁니다 — 그냥 일관되게 감싸는 것뿐입니다.

### stoke가 CMake / Meson / Make를 대체하나요?

딱히 아닙니다. stoke는 빌드 시스템이라기보다 프로젝트 러너에 가깝습니다. 특정 관점을 가지고 있고 흔한 케이스에서는 바로 동작합니다. 이미 `CMakeLists.txt`가 있는 C/C++ 타깃은 `build_system = "cmake"`로 설정하면 stoke가 직접 컴파일러를 다루는 대신 `cmake`에 위임합니다 — [stoke.toml 레퍼런스](configuration/stoke-toml.md#cmake-for-cc) 참고. CMake 자체가 잘 다루지 못하는 빌드 시나리오나 Meson은 알아서 하셔야 합니다.

### stoke가 지원하는 언어는?

현재:

- Python
- Java (JDK 17+)
- C
- C++
- Go
- Rust
- Kotlin (Gradle 경유)
- C# (.NET SDK 경유)
- Ruby
- PHP
- JavaScript
- TypeScript

앞으로 더 추가될 수 있습니다.

### 어떤 플랫폼을 지원하나요?

- Windows (네이티브 인스톨러)
- Linux (네이티브 타볼)
- macOS (네이티브 타볼)

Windows(MSYS2/MinGW64)에서 주로 개발되고 있습니다.

## 설치

### stoke는 어떻게 업데이트하나요?

Windows 인스톨러 사용자: 새 인스톨러를 다운로드해서 실행하세요. 기존 버전을 대체합니다.

macOS/Linux 타볼 사용자: [Releases](https://github.com/dvdsvds/stoke/releases/latest)에서 새 타볼을 받아서 기존 것 위에 압축을 풀어주세요.

### stoke는 어떻게 제거하나요?

Windows 인스톨러: Windows "프로그램 추가/제거"를 사용하거나 설치 디렉토리의 언인스톨러를 실행하세요.

macOS/Linux: 압축을 푼 `stoke` 폴더를 삭제하고 `PATH`에서 제거하세요.

## 설정

### 한 프로젝트에 여러 타깃을 둘 수 있나요?

네. `[targets.<name>]` 섹션을 원하는 만큼:

```toml
[targets.server]
language = "python"
entry = "server/main.py"

[targets.client]
language = "cpp"
sources = ["client/**/*.cpp"]
```

전체 빌드: `stoke build`
하나만 빌드: `stoke build server`

### 타깃마다 다른 언어를 쓸 수 있나요?

네. 각 타깃이 자기만의 `language`를 가집니다.

### 한 타깃이 다른 타깃에 의존할 수 있나요?

네, `depends_on`으로:

```toml
[targets.backend]
language = "python"
depends_on = ["shared_lib"]
```

`stoke build backend`는 `shared_lib`을 먼저 빌드합니다. `stoke build --all`은 독립적인 타깃들을 병렬로 빌드하지만 각 타깃의 의존성이 먼저 끝날 때까지 기다리고, 의존 대상이 실패하면 그 타깃은 건너뜁니다. 순환 참조와 알 수 없는 타깃 참조는 `stoke.toml`을 불러올 때 거부됩니다.

### 타깃 간에 코드를 공유할 수 있나요?

네. `sources` glob 패턴을 조정해서 공유 코드를 포함시키세요:

```toml
[targets.server]
language = "python"
sources = ["server/**/*.py", "shared/**/*.py"]

[targets.worker]
language = "python"
sources = ["worker/**/*.py", "shared/**/*.py"]
```

### 빌드 결과물은 어디에 있나요?

`.stoke/{language}/{target}/{profile}/`. [`stoke build`](commands/build.md#output-structure) 참고.

### 커스텀 빌드 단계를 추가할 수 있나요?

네 — 어떤 타깃이든 `pre_build`/`post_build`로 빌드 전후에 셸 명령을 실행할 수 있습니다. [stoke.toml 레퍼런스](configuration/stoke-toml.md#build-hooks) 참고. 사용자 권한으로 셸을 통해 실행되므로, 신뢰하는 `stoke.toml`만 빌드하세요.

## 언어별

### Python: stoke가 pip / venv를 대체하나요?

아니요. stoke는 내부적으로 venv와 pip을 사용합니다. venv 생성, 의존성 설치, PYTHONPATH 설정을 자동화할 뿐입니다.

### Java: stoke가 Maven을 사용하나요?

stoke는 의존성 다운로드에 Maven Central을 사용합니다. Maven의 빌드 시스템은 사용하지 않고 — `javac`를 직접 호출합니다.

생성되는 `pom.xml`은 IDE 연동 용도일 뿐입니다.

### C/C++: stoke는 어떤 컴파일러를 쓰나요?

- Linux 기본값: gcc
- macOS 기본값: clang
- Windows 기본값: gcc (MSYS2/MinGW)

빌드 프로파일로 오버라이드할 수 있습니다. MSVC(`cl.exe`)는 현재 지원하지 않습니다.

### C/C++: CMake를 쓸 수 있나요?

네 — 타깃에 `build_system = "cmake"`를 설정하고 `source_dir`이 `CMakeLists.txt`가 있는 폴더를 가리키게 하세요. 그러면 stoke가 자체 컴파일 모델 대신 `cmake` configure/build를 실행합니다; `c_standard`/`cpp_standard`와 프로파일 컴파일 플래그는 이 경로에서는 `CMakeLists.txt`가 담당하므로 무시됩니다. [stoke.toml 레퍼런스](configuration/stoke-toml.md#cmake-for-cc) 참고.

### Rust, Kotlin, C#, Ruby, PHP: stoke가 Cargo / Gradle / dotnet / Bundler / Composer를 대체하나요?

아니요. stoke는 각 생태계 자체 도구에 직접 위임합니다 — Rust는 `cargo build`/`cargo run`, Kotlin은 `gradlew build`/`gradlew run`, C#은 `dotnet build`/`dotnet run`, Ruby는 `bundle install` + `ruby`/`bundle exec ruby`, PHP는 `composer install` + `php`. stoke는 다른 언어들과 나란히 일관된 `stoke build`/`stoke run` 인터페이스를 제공할 뿐입니다.

### 왜 Rails와 Laravel은 `stoke init` 스캐폴드가 없나요?

둘 다 진입 스크립트를 직접 실행하는 게 아니라 CLI 서브커맨드(`bin/rails server`, `php artisan serve`)로 시작하는데, 이는 stoke의 현재 실행 모델(`stoke run`이 스크립트/바이너리 하나를 실행)에 맞지 않습니다. 대신 이 모델에 맞는 Sinatra(Ruby)와 Slim(PHP)이 추가됐습니다 — 자세한 내용은 [Ruby](languages/ruby.md)와 [PHP](languages/php.md) 언어 페이지를 참고하세요.

## 동작 방식

### 왜 빌드가 캐시를 안 쓰나요?

흔한 이유:

- 헤더가 변경됨 (C/C++는 헤더를 자동으로 추적)
- 소스 파일의 타임스탬프가 변경됨
- 컴파일 플래그가 변경됨 (다른 프로파일)
- `--force`를 사용함

verbose 모드로 디버깅할 수 있습니다:

```bash
stoke build -v
```

### 왜 `stoke build`가 매번 IDE 파일을 다시 생성하나요?

v0.7.2부터는 그렇지 않습니다. IDE 파일은 내용이 바뀔 때만 다시 써집니다.

`IDE files updated: X, Y`가 보인다면 실제로 바뀐 것만입니다.

### 왜 `Lock file saved`가 매번 뜨나요?

v0.7.2에서 수정됐습니다. 최신 버전으로 업데이트하세요.

## 연동

### stoke가 CI에서 동작하나요?

네. 컨테이너나 CI 러너에서 `stoke build`는 로컬과 똑같이 동작합니다. 이후 빌드를 빠르게 하려면 `.stoke/` 디렉토리를 캐시하세요.

권장: 재현 가능한 빌드를 위해 CI에서는 `lock_mode = "strict"`를 사용하세요.

### stoke가 Docker와 함께 동작하나요?

네. Dockerfile에서 stoke를 설치하세요:

```dockerfile
RUN curl -fsSL -o stoke.tar.gz \
      https://github.com/dvdsvds/stoke/releases/latest/download/stoke-X.Y.Z-linux-x86_64.tar.gz \
    && tar xzf stoke.tar.gz -C /opt \
    && ln -s /opt/stoke/stoke /usr/local/bin/stoke
```

그 다음 평소처럼 `stoke build`.

### 다른 도구에서 stoke를 서브프로세스로 쓸 수 있나요?

네. 종료 코드가 의미 있게 반환됩니다:

- 0: 성공
- 0이 아님: 실패

출력은 표준 방식대로 stdout/stderr로 나갑니다.

## 기여

### 어떻게 기여할 수 있나요?

- 버그 리포트나 기능 요청: [github.com/dvdsvds/stoke/issues](https://github.com/dvdsvds/stoke/issues)
- GitHub에서 Pull Request 환영합니다

### 소스 코드는 어디에 있나요?

[github.com/dvdsvds/stoke](https://github.com/dvdsvds/stoke)

MIT 라이선스입니다.

## 관련 문서

- [문제 해결](troubleshooting.md)
- [시작하기](getting-started/installation.md)
