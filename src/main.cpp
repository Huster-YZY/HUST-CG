#include<iostream>
#include<glad.h>
#include<GLFW/glfw3.h>
#include<cmath>
#include<fstream>
#include"shader.h"

const unsigned int SCR_WIDTH=800;
const unsigned int SCR_HEIGHT=600;
unsigned int VAO,VBO,EBO,shaderProgram;
float vertices[]={
    0.5f,0.5f,0.0f,
    0.5f,-0.5f,0.0f,
    -0.5f,-0.5f,0.0f,
    -0.5f,0.5f,0.0f
    }; 
unsigned int indices[]={
    0,1,3,
    1,2,3
};


const char* vertex_shader_source=
    "#version 330 core\n"
    "layout (location=0) in vec3 aPos;\n"
    "out vec4 vertexColor;\n"
    "uniform vec4 ourColor;\n"
    "void main()\n"
    "{\n"
    "  gl_Position=vec4(aPos.x,aPos.y+ourColor.g,aPos.z,1.0);\n"
    "  vertexColor=vec4(0.5,0.0,0.0,1.0);\n"
    "}\n\0";

const char* fragment_shader_source=
    "#version 330 core\n"
    "out vec4 FragColor;\n"
    "in vec4 vertexColor;\n"
    "uniform vec4 ourColor;\n"
    "void main()\n"
    "{\n"
    "  FragColor=ourColor;\n"
    "}\n\0";

void framebuffer_size_callback(GLFWwindow* window,int width,int height){
    glViewport(0,0,width,height);
}

void clear(){
    glClearColor(0.2f,0.3f,0.3f,1.0f);
    glClear(GL_COLOR_BUFFER_BIT);
}

void init(){
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3);
    glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE);
}

void generate_shader_program(){
    unsigned int vertexShader;
    vertexShader=glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vertexShader,1,&vertex_shader_source,NULL);
    glCompileShader(vertexShader);
    int success;
    char info[512];
    glGetShaderiv(vertexShader,GL_COMPILE_STATUS,&success);
    if(!success){
        glGetShaderInfoLog(vertexShader,512,NULL,info);
        std::cout<<"ERROR::SHADER::VERTEX::COMPILATION_FAILED\n"<<info<<std::endl;
    }

    unsigned int fragmentShader;
    fragmentShader=glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fragmentShader,1,&fragment_shader_source,NULL);
    glCompileShader(fragmentShader);
    glGetShaderiv(fragmentShader,GL_COMPILE_STATUS,&success);
    if(!success){
        glGetShaderInfoLog(fragmentShader,512,NULL,info);
        std::cout<<"ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n"<<info<<std::endl;
    }


    shaderProgram=glCreateProgram();
    glAttachShader(shaderProgram,vertexShader);
    glAttachShader(shaderProgram,fragmentShader);
    glLinkProgram(shaderProgram);
    glUseProgram(shaderProgram);
    
    glGenVertexArrays(1,&VAO);
    glGenBuffers(1,&VBO);
    glGenBuffers(1,&EBO);
    glBindVertexArray(VAO);
    glBindBuffer(GL_ARRAY_BUFFER,VBO);
    glBufferData(GL_ARRAY_BUFFER,sizeof(vertices),vertices,GL_STATIC_DRAW);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,sizeof(indices),indices,GL_STATIC_DRAW);

    glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,3*sizeof(float),(void*)0);
    glEnableVertexAttribArray(0);

    glBindBuffer(GL_ARRAY_BUFFER,0);
    glBindVertexArray(0);
}

void prepare_VAO(){
    glGenVertexArrays(1,&VAO);
    glGenBuffers(1,&VBO);
    glGenBuffers(1,&EBO);

    glBindVertexArray(VAO);
    glBindBuffer(GL_ARRAY_BUFFER,VBO);
    glBufferData(GL_ARRAY_BUFFER,sizeof(vertices),vertices,GL_STATIC_DRAW);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,sizeof(indices),indices,GL_STATIC_DRAW);

    glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,3*sizeof(float),(void*)0);
    glEnableVertexAttribArray(0);

    glBindBuffer(GL_ARRAY_BUFFER,0);
    glBindVertexArray(0);
}

void draw(Shader& ourShader){
    float timeValue=glfwGetTime();
    float greenValue=(sin(timeValue)/2.0f)+0.5f;

    // int vertexColorLocation=glGetUniformLocation(shaderProgram,"ourColor");
    // glUseProgram(shaderProgram);
    // glUniform4f(vertexColorLocation,0.0f,greenValue,0.0f,1.0f);

    ourShader.use();
    ourShader.setVec4("ourColor",glm::vec4(.0f,greenValue,.0f,.0f));
    
    glBindVertexArray(VAO);
    // glDrawArrays(GL_TRIANGLES,0,3);
    glDrawElements(GL_TRIANGLES,6,GL_UNSIGNED_INT,0);
    glBindVertexArray(0);
}

void cleanup(){
    glDeleteVertexArrays(1,&VAO);
    glDeleteBuffers(1,&VBO);
    glDeleteProgram(shaderProgram);
}

int main(){
    
    init();
 
    GLFWwindow * window=glfwCreateWindow(SCR_WIDTH,SCR_HEIGHT,"SOLAR",NULL,NULL);
    if (window==NULL){
        std::cout<<"Failed to create GLFW window"<<std::endl;
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);
    glfwSetFramebufferSizeCallback(window,framebuffer_size_callback);
    
    //Load OpenGL function opinters by using GLAD
    if(!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)){
        std::cout<<"Failed to initialize GLAD"<< std::endl;
        return -1;
    }

    Shader ourShader("/home/zhenya/hust_cg/src/shaders/a.vs","/home/zhenya/hust_cg/src/shaders/a.fs");
    prepare_VAO();
    
    // generate_shader_program();

    while(!glfwWindowShouldClose(window)){
        clear();
        draw(ourShader);
        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    cleanup();

    glfwTerminate();
    return 0;    
}