UV ?= uv

.PHONY: install lint format typecheck test test-integration test-attack up down migrate seed check

install:
	$(UV) sync --all-groups

lint:
	$(UV) run poe lint

format:
	$(UV) run poe format

typecheck:
	$(UV) run poe typecheck

test:
	$(UV) run poe test

test-integration:
	$(UV) run poe test-integration

test-attack:
	$(UV) run poe test-attack

up:
	$(UV) run poe up

down:
	$(UV) run poe down

migrate:
	$(UV) run poe migrate

seed:
	$(UV) run poe seed

check:
	$(UV) run poe check
