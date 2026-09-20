# Example: build a stoke project inside Docker.
# Copy into your project (not stoke itself) and adjust the final image's base/entrypoint
# for your target language.
FROM debian:bookworm-slim AS build

ARG STOKE_VERSION=2.3.0
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# stoke ships as a standalone binary with Python bundled in — no separate
# interpreter/runtime needs installing here.
RUN curl -fsSL -o /tmp/stoke.tar.gz \
      "https://github.com/dvdsvds/stoke/releases/download/v${STOKE_VERSION}/stoke-${STOKE_VERSION}-linux-x86_64.tar.gz" \
    && tar xzf /tmp/stoke.tar.gz -C /opt \
    && ln -s /opt/stoke/stoke /usr/local/bin/stoke \
    && rm /tmp/stoke.tar.gz

WORKDIR /app
COPY . .

# Fetch the toolchain your stoke.toml pins, matching go_version/python_version/etc.
# (`stoke build` also auto-detects an already-installed system toolchain, but this
# container starts empty, so install explicitly here.) This example is a Go target
# named "myapp" -- swap the language/version and target name for your project.
ARG STOKE_LANGUAGE=go
ARG STOKE_LANGUAGE_VERSION=1.22
RUN stoke install "${STOKE_LANGUAGE}" --version="${STOKE_LANGUAGE_VERSION}" \
    && stoke build --release

# ---- runtime stage: copy only the compiled binary, not the toolchain ----
FROM debian:bookworm-slim AS runtime
WORKDIR /app
# stoke's build output lives at .stoke/<language>/<target-name>/<binary-name>
# (here: .stoke/go/myapp/myapp) -- adjust for your language/target.
COPY --from=build /app/.stoke/go/myapp/myapp ./myapp
ENTRYPOINT ["./myapp"]
