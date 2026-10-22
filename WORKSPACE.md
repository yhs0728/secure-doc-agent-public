# 세 버전 작업 공간

```text
C:\llm-study\secure-doc-agent\
├─ local\         로컬 서비스 + 로컬 Ollama
├─ hybrid\        로컬 서비스 + AWS Bedrock
└─ multicloud\    OCI 업무 서비스 + AWS Bedrock·S3·OpenSearch
```

세 폴더는 각각 `.git`과 독립 원격 저장소를 가집니다. 상위 기준 저장소는 하위 폴더를
Git에서 제외합니다. 기준 코드와 기존 실행 데이터는 상위에 보존하며 앞으로 버전별 작업은
하위 저장소에서 진행합니다. 한 저장소의 커밋·푸시는 다른 저장소에 자동 반영되지 않습니다.

| 폴더 | 저장소 | 앱 | 프런트 개발 서버 | 검증 앱 |
|---|---|---|---|---|
| `local` | [로컬](https://github.com/yhs0728/secure-doc-agent-local) | `http://127.0.0.1:18081` | `http://127.0.0.1:15171` | `http://127.0.0.1:18181` |
| `hybrid` | [로컬 + AWS](https://github.com/yhs0728/secure-doc-agent-hybrid) | `http://127.0.0.1:18082` | `http://127.0.0.1:15172` | `http://127.0.0.1:18182` |
| `multicloud` | [OCI + AWS](https://github.com/yhs0728/secure-doc-agent-multicloud) | `http://127.0.0.1:18083` | `http://127.0.0.1:15173` | `http://127.0.0.1:18183` |

로컬 포트는 사전 개발·검증용입니다. OCI 배포의 실제 주소는 배포 환경에서 정합니다.
포트 분리는 세 버전을 모두 켜라는 뜻이 아닙니다. 모델·검색 엔진 메모리는 실행 수만큼 필요합니다.

## 편집과 실행

`secure-doc-agent.code-workspace`를 VS Code에서 열면 세 저장소만 별도 작업 폴더로 표시합니다.
기존 상위 `.venv`를 기본 Python 도구로 사용할 수 있으며, 서비스 배포 의존성은 각 Docker 이미지로 분리합니다.

현재 Windows 환경은 Ubuntu WSL의 Docker를 사용하므로 상위 폴더에서 다음처럼 실행할 수 있습니다.

```powershell
python tools/compose_variant.py --wsl local config --quiet
python tools/compose_variant.py --wsl local up -d --build
python tools/compose_variant.py --wsl hybrid ps
python tools/compose_variant.py --wsl multicloud --validation config --quiet
```

각 폴더의 `tools/compose.py`는 `.env.microservices`, Bedrock 설정, 프로젝트 이름과 Compose 파일을
절대 경로로 선택합니다. 클라우드 버전에는 해당 폴더의 `.env.bedrock` 또는 환경 변수로 실제
Bedrock API key를 준비해야 합니다. 키를 상위 `.env`나 다른 버전과 자동 공유하지 않습니다.

하위 저장소 안에서도 `python tools/compose.py up -d --build`를 사용할 수 있습니다.
WSL에서는 `python3 tools/compose.py`로 실행합니다. `.env.microservices`가 없으면 해당 폴더에서
`python tools/prepare_microservices_env.py`를 먼저 실행합니다.

## 새 컴퓨터에서 복원

상위 기준 저장소를 복제한 뒤 `python tools/setup_workspace.py`를 실행합니다.
없는 하위 저장소만 복제하며 기존 폴더를 덮어쓰거나 자동으로 pull하지 않습니다.
Python 의존성과 실제 환경 파일은 별도로 준비합니다. Git 이력에 런타임 비밀 값·볼륨 데이터는 없습니다.

## 이동에 따른 보완

- 기존 `secure-doc-agent-local/hybrid/multicloud` Docker 프로젝트 이름을 고정해 폴더명에 따른 볼륨 이름 변경을 방지했습니다.
- 앱·DB·객체 저장소·검색·모니터링·검증 포트를 버전별로 분리했습니다. 기존에 실행 중인 상위 서비스는 재생성하지 않았습니다.
- 프런트 개발 프록시와 E2E·벤치마크 기본 주소를 각 버전의 앱에 맞췄습니다.
- 상위 pytest가 독립 저장소의 동일 이름 테스트를 중복 수집하지 않도록 제외했습니다.
- VS Code 작업 공간과 상대 경로 기반 복원·실행 도구를 추가했습니다.

프런트 의존성은 각 폴더의 `frontend`에서 `npm ci`로 준비합니다.
일반 셸에서 Python 도구를 실행할 때는 상위 `.venv`를 활성화하거나 각 저장소에 별도 가상 환경을 준비합니다.
공통 Python 환경은 개발 편의용이며 Docker 배포 의존성은 서비스별로 유지합니다.
