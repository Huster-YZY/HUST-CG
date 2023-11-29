CC=gcc
CXX =g++

COMPILE_FLAGS= -Wall -O3
LINK_FALGS= -lglfw3 -IGL -ldl -lpthread

glfw_inc= /usr/local/include/GLFW
glfw_lib=/usr/local/lib/libglfw3.a

glad_inc=$(CURDIR)/include/glad
glad_src=$(CURDIR)/src/glad.c

INCLUDES = -I $(glfw_inc) -I$(glad_inc)
LIBRARIES =-L$(glfw_lib)

cpp_files =$(CURDIR)/src/main.cpp
objects = $(cpp_files:.cpp=.o)
headers =

all:a.out

a.out: $(objects) glad.o
		$(CXX) $(LIBRARIES) -o a.out $(objects) glad.o $(LINK_FALGS)

$(objects): %.o: %.cpp $(headers)
		$(CXX) $(COMPILE_FLAGS) $(INCLUDES) -c -o $@ $<

glad.o: $(glad_src)
		$(CC) $(COMPILE_FLAGS) $(INCLUDES) -c $(glad_src) -o glad.o 

clean:
		rm -f $(objects) glad.o
