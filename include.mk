##############################################################################
# upbge
##############################################################################

ifeq ("$(OS)", "Windows_NT")
UPBGE_VERSION=upbge-0.36.1-windows-x86_64
UPBGE_TARBALL=$(UPBGE_VERSION).7z
else
UPBGE_VERSION=upbge-0.36.1-linux-x86_64
UPBGE_TARBALL=$(UPBGE_VERSION).tar.xz
endif
UPBGE_URL=https://github.com/UPBGE/upbge/releases/download/v0.36.1/$(UPBGE_TARBALL)
UPBGE_DONWLOAD_FOLDER?=$(MXMAKE_FOLDER)/downloads

UPBGE_DOWNLOAD_TARGET:=$(SENTINEL_FOLDER)/upbge-download.sentinel
$(UPBGE_DOWNLOAD_TARGET): $(SENTINEL)
	@echo "Download upbge tarball"
	@mkdir -p $(UPBGE_DONWLOAD_FOLDER)
	@wget -P $(UPBGE_DONWLOAD_FOLDER) $(UPBGE_URL)
	@touch $(UPBGE_DOWNLOAD_TARGET)

UPBGE_EXTRACT_TARGET:=$(SENTINEL_FOLDER)/upbge-extract.sentinel
$(UPBGE_EXTRACT_TARGET): $(UPBGE_DOWNLOAD_TARGET)
ifeq ("$(OS)", "Windows_NT")
	@7z x $(UPBGE_DONWLOAD_FOLDER)/$(UPBGE_TARBALL)
else
	@tar xf $(UPBGE_DONWLOAD_FOLDER)/$(UPBGE_TARBALL) -C .
endif
	@mv $(UPBGE_VERSION) bin
	@touch $(UPBGE_EXTRACT_TARGET)

UPBGE_RUN_TARGET:=$(SENTINEL_FOLDER)/upbge-run.sentinel
$(UPBGE_RUN_TARGET):
	@./bin/blender -b ./utils/run.blend -P ./utils/build.py
	@touch $(UPBGE_RUN_TARGET)

.PHONY: upbge-install
upbge-install: $(UPBGE_EXTRACT_TARGET)

.PHONY: upbge-run-clean
upbge-run-clean:
	@rm -rf ./utils/3.6
	@rm -rf ./utils/engine.license
	@rm -f ./utils/run
	@rm -f ./utils/run.blend1
	@rm -rf ./utils/lib/
	@rm -f $(UPBGE_RUN_TARGET)

.PHONY: upbge-clean
upbge-clean: upbge-run-clean
	@rm -rf $(UPBGE_DONWLOAD_FOLDER)/$(UPBGE_TARBALL)
	@rm -f $(UPBGE_DOWNLOAD_TARGET)
	@rm -rf bin
	@rm -f $(UPBGE_EXTRACT_TARGET)

##############################################################################
# default targets
##############################################################################

SPHINX_BIN:=./utils/run sphinx
INSTALL_TARGETS:=upbge-install $(INSTALL_TARGETS) $(UPBGE_RUN_TARGET)
CLEAN_TARGETS+=upbge-clean
