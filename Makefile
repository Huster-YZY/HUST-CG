PROGRAME_NAME=solar

CC=gcc
CXX =g++

COMPILE_FLAGS= -Wall -O3
LINK_FALGS= -lglfw3 -lGL -lX11 -lXi -lXrandr -ldl -lpthread

glfw_inc= /usr/local/include/GLFW
glfw_lib=/usr/local/lib/libglfw3.a

glad_inc=$(CURDIR)/include/glad
glad_src=$(CURDIR)/src/glad.c

local_inc=$(CURDIR)/include

INCLUDES = -I $(glfw_inc) -I$(glad_inc) -I$(local_inc) 
LIBRARIES =-L$(glfw_lib)

cpp_files =$(CURDIR)/src/main.cpp
objects = $(cpp_files:.cpp=.o)
headers = $(local_inc)/shader.h

all:$(PROGRAME_NAME)

$(PROGRAME_NAME): $(objects) glad.o 
		$(CXX) $(LIBRARIES) -o $(PROGRAME_NAME) $(objects) glad.o $(LINK_FALGS)

$(objects): %.o: %.cpp $(headers) 
		$(CXX) $(COMPILE_FLAGS) $(INCLUDES) -c -o $@ $<

glad.o: $(glad_src)
		$(CC) $(COMPILE_FLAGS) $(INCLUDES) -c $(glad_src) -o glad.o 

run:$(PROGRAME_NAME)
		./$(PROGRAME_NAME)

clean:
		rm -f $(objects) glad.o
