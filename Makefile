GIT_TAG=$(shell git describe --abbrev=0 --tags)
DOCKER_NAMESPACE?="kiennt26"
DOCKER_IMAGE?="ansitheus"

.PHONY: clean
clean:
	@echo "+ $@"
	@docker rmi ${DOCKER_NAMESPACE}/${DOCKER_IMAGE}:latest || true
	@docker rmi ${DOCKER_NAMESPACE}/${DOCKER_IMAGE}:${GIT_TAG} || true

.PHONY: build
build:
	@echo "+ $@"
	@docker build -t ${DOCKER_NAMESPACE}/${DOCKER_IMAGE}:${GIT_TAG} .
	@docker tag ${DOCKER_NAMESPACE}/${DOCKER_IMAGE}:${GIT_TAG} ${DOCKER_NAMESPACE}/${DOCKER_IMAGE}:latest
	@echo 'Done.'

.PHONY: push
push: build
	@echo "+ $@"
	@docker push ${DOCKER_NAMESPACE}/${DOCKER_IMAGE}:${GIT_TAG}
	@docker push ${DOCKER_NAMESPACE}/${DOCKER_IMAGE}:latest
