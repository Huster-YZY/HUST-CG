#include<iostream>
#include<glad.h>
#include<GLFW/glfw3.h>
#include<cmath>
#include<fstream>
#include"shader.h"

const unsigned int SCR_WIDTH=800;
const unsigned int SCR_HEIGHT=600;
unsigned int VAO,VBO,EBO;
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