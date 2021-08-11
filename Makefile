# Makefile
BINDIR := bin

CC := g++
CFLAGS := -std=c++17 -Wall -ggdb

VPATH := main:src:$(BINDIR)

SRC := $(wildcard src/*.cpp)
OBJ := $(patsubst %.cpp, $(BINDIR)/%.o, $(notdir $(SRC)))
INC := $(wildcard src/*.h)

all: main

main: $(OBJ)
	$(CC) $(CFLAGS) $? -o $(BINDIR)/$@

$(OBJ): $(INC)

$(BINDIR)/%.o: %.cpp
	@mkdir -p bin
	$(CC) $(CFLAGS) -I src -c $< -o $@

clean:
	rm -f bin/*