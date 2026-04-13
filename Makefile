.PHONY: build dev dev-verify venv

build:
	./scripts/build_full.sh

dev:
	./scripts/dev_full.sh

dev-verify:
	./scripts/dev_verify_full.sh

venv:
	./scripts/setup_venv.sh
