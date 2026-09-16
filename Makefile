# Executable name

EXE := patterns

# Compiler flags

CXX := clang++
CPPFLAGS := -MMD
CXXFLAGS := -std=c++23 -Werror -pedantic-errors -Weverything -Wno-c++98-compat -Wno-poison-system-directories -Wno-unsafe-buffer-usage
OPT := -O3 -DNDEBUG

# Directory structure

SRC_DIR := ./native
BUILD_DIR := ./build

# Gather all expected .cpp files

CPP := $(wildcard $(SRC_DIR)/*.cpp)

# Map .cpp files to their respective .o files

OBJS := $(CPP:$(SRC_DIR)/%.cpp=$(BUILD_DIR)/%.o)

# Build release executable

.PHONY: release
release: $(BUILD_DIR)/$(EXE)

# Link .o object files

$(BUILD_DIR)/$(EXE): $(OBJS)
	$(CXX) $(CXXFLAGS) $(OPT) $^ -o $@

# Compile .cpp sources

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(OPT) -c $< -o $@

# Create build directory

$(BUILD_DIR):
	mkdir -p $@

# Delete build directory

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)

# Include .d dependencies

DEPS := $(CPP:$(SRC_DIR)/%.cpp=$(BUILD_DIR)/%.d)

-include $(DEPS)
