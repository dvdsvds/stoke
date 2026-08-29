# Java

stoke는 JDK 감지, 증분 컴파일, Maven 의존성 관리를 통해 Java 프로젝트를 관리합니다.

## `stoke.toml` 예시

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "java"
java_version = "25"
sources = ["src/main/java/**/*.java"]
main_class = "com.example.Main"

[targets.myapp.deps]
"com.google.code.gson:gson" = "2.10.1"
"org.slf4j:slf4j-api" = "2.0.9"
```

## Target 필드

| 필드 | 필수 | 설명 |
|-------|----------|-------------|
| `language` | 예 | `"java"` |
| `java_version` | 아니오 | 필요한 JDK 메이저 버전 (예: `"25"`) |
| `sources` | 예 | `.java` 파일 glob 패턴 |
| `main_class` | `run`에 필요 | Fully qualified main 클래스 |
| `deps` | 아니오 | Maven 좌표 → 버전 |

## JDK 감지

특정 메이저 버전을 요구하려면 `java_version` 설정:

```toml
java_version = "25"        # JDK 25 요구 (마이너 버전 무관)
java_version = "17.0.13"   # 정확히 17.0.13 요구
```

stoke가 JDK를 찾는 순서:

1. `JAVA_HOME` 환경 변수
2. `PATH` (`javac`)
3. 표준 설치 경로:
   - Windows: `C:\Program Files\Eclipse Adoptium`, `C:\Program Files\Java`, `Zulu`, `Amazon Corretto`, `Microsoft`
   - macOS: `/Library/Java/JavaVirtualMachines`
   - Linux: `/usr/lib/jvm`, `/opt/java`

감지된 JDK 확인:

```bash
stoke java list
```

## 컴파일

`stoke build`는 `sources`에 매칭되는 모든 파일에 `javac` 실행.

출력: `.stoke/java/{target}/{profile}/classes/`

증분 컴파일: 변경된 `.java` 파일만 재컴파일.

## 의존성 (Maven)

Maven 좌표 (`groupId:artifactId`)로 의존성 선언:

```toml
[targets.myapp.deps]
"com.google.code.gson:gson" = "2.10.1"
"org.junit.jupiter:junit-jupiter" = "5.10.0"
```

stoke가 Maven Central에서 JAR을 다운로드하고 로컬 캐싱.
잠긴 버전과 SHA1 해시가 `.stoke/lock.toml`에 저장됩니다.

## 실행

```bash
stoke run
```

`java -cp <classpath> <main_class>` 실행. classpath 포함:

- `.stoke/java/{target}/{profile}/classes/`
- 모든 Maven 의존성 JAR

## 소스 레이아웃

표준 Maven 규칙:

    myapp/
    ├── stoke.toml
    └── src/
        └── main/
            └── java/
                └── com/
                    └── example/
                        ├── Main.java
                        └── Utils.java

어떤 레이아웃이든 사용 가능; `sources` glob을 맞게 조정:

```toml
sources = ["src/**/*.java"]              # src/ 하위 아무 위치
sources = ["src/main/java/**/*.java"]    # Maven 규칙
```

## IDE 통합

`stoke build`가 자동 생성:

- `.classpath` — Eclipse 프로젝트 포맷
- `.project` — Eclipse 프로젝트 descriptor
- `.vscode/settings.json` — VSCode Java 확장 설정
- `pom.xml` — IntelliJ / Maven 기반 도구용 Maven POM

Eclipse, VSCode (Java Extension Pack), IntelliJ 어디서든 별도 설정 없이 사용 가능.

## UTF-8 인코딩

stoke가 `javac -encoding UTF-8` 자동 설정. 비 ASCII 문자 (한글, 일본어, 이모지 등)를 포함한 소스 파일도 문제없이 컴파일됩니다.

## 관련 문서

- [`stoke build`](../../commands/build.md)
- [`stoke run`](../../commands/run.md)