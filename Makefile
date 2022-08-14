NAME=workoutdb
BIN=bin/
MAIN=src/main.py

FLAGS=--onefile --distpath $(BIN) --name=$(NAME)

clean:
	rm -rf $(BIN) build/ $(NAME).spec src/__pycache__/

build: $(MAIN)
	mkdir -p $(BIN)
	pyinstaller $(FLAGS) $(MAIN)

install: $(BIN)/$(NAME)
	sudo cp $(BIN)/$(NAME) /bin

uninstall: /bin/$(NAME)
	sudo rm /bin/$(NAME)