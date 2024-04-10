##############################################################################
# upbge
##############################################################################

UPBGE_VERSION=upbge-0.36.1-linux-x86_64
UPBGE_TARBALL=$(UPBGE_VERSION).tar.xz
UPBGE_URL=https://github.com/UPBGE/upbge/releases/download/v0.36.1/$(UPBGE_TARBALL)
UPBGE_DONWLOAD_FOLDER?=$(MXMAKE_FOLDER)/downloads

UPBGE_DOWNLOAD_TARGET:=$(SENTINEL_FOLDER)/upbge-download.sentinel
$(UPBGE_DOWNLOAD_TARGET): $(SENTINEL)
	@echo "Download upbge tarball"
	@mkdir -p $(UPBGE_DONWLOAD_FOLDER)
	@pushd $(UPBGE_DONWLOAD_FOLDER)
	@wget $(UPBGE_URL)
	@popd
	@touch $(UPBGE_DOWNLOAD_TARGET)

UPBGE_EXTRACT_TARGET:=$(SENTINEL_FOLDER)/upbge-extract.sentinel
$(UPBGE_EXTRACT_TARGET): $(UPBGE_DOWNLOAD_TARGET)
	@tar xf $(UPBGE_DONWLOAD_FOLDER)/$(UPBGE_TARBALL) -C .
	@mv $(UPBGE_VERSION) bin
	@touch $(UPBGE_EXTRACT_TARGET)

UPBGE_TEST_TARGET:=$(SENTINEL_FOLDER)/upbge-test.sentinel
$(UPBGE_TEST_TARGET):
	@./bin/blender -b ./tests/bin/test.blend -P ./tests/bin/build.py
	@touch $(UPBGE_TEST_TARGET)

.PHONY: upbge-install
upbge-install: $(UPBGE_EXTRACT_TARGET)

.PHONY: upbge-test-clean
upbge-test-clean:
	@rm -rf ./tests/bin/3.6
	@rm -rf ./tests/bin/engine.license
	@rm -f ./tests/bin/test
	@rm -f ./tests/bin/test.blend1
	@rm -rf ./tests/bin/lib/
	@rm -f $(UPBGE_TEST_TARGET)

.PHONY: upbge-clean
upbge-clean: upbge-test-clean
	@rm -rf $(UPBGE_DONWLOAD_FOLDER)/$(UPBGE_TARBALL)
	@rm -f $(UPBGE_DOWNLOAD_TARGET)
	@rm -rf bin
	@rm -f $(UPBGE_EXTRACT_TARGET)

##############################################################################
# default targets
##############################################################################

INSTALL_TARGETS:=upbge-install $(INSTALL_TARGETS) $(UPBGE_TEST_TARGET)
CLEAN_TARGETS+=upbge-clean build-clean