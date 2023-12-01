#include<iostream>
#include<glad.h>
#include<GLFW/glfw3.h>
#include<cmath>
#include<fstream>
#include<vector>
#include"shader.h"

const unsigned int SCR_WIDTH=800;
const unsigned int SCR_HEIGHT=600;
unsigned int VAO,VBO,EBO;
std::vector<float> vertices;
std::vector<int> indices;
const float Radio=2.0;
const GLfloat PI=3.14159265358979323846f;

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

void sphere_generation(int X_SEGMENTS,int Y_SEGMENTS){
    for(int y=0;y<=Y_SEGMENTS;y++)
    for(int x=0;x<=X_SEGMENTS;x++){
        float xn=x*1.0/X_SEGMENTS;
        float yn=y*1.0/Y_SEGMENTS;
        float xp=cos(xn*Radio*PI)*sin(yn*PI);
        float yp=cos(yn*PI);
        float zp=sin(xn*Radio*PI)*sin(yn*PI);

        vertices.push_back(xp);
        vertices.push_back(yp);
        vertices.push_back(zp);
    }

    for(int i=0;i<Y_SEGMENTS;i++)
    for(int j=0;j<X_SEGMENTS;j++){
        indices.push_back(i*(X_SEGMENTS+1)+j);
        indices.push_back((i+1)*(X_SEGMENTS+1)+j);
        indices.push_back((i+1)*(X_SEGMENTS+1)+j+1);

        indices.push_back(i*(X_SEGMENTS+1)+j);
        indices.push_back((i+1)*(X_SEGMENTS+1)+j+1);
        indices.push_back(i*(X_SEGMENTS+1)+j+1);
    }
}
void prepare_VAO(){
    glGenVertexArrays(1,&VAO);
    glGenBuffers(1,&VBO);
    glGenBuffers(1,&EBO);

    glBindVertexArray(VAO);
    glBindBuffer(GL_ARRAY_BUFFER,VBO);
    glBufferData(GL_ARRAY_BUFFER,sizeof(float)*vertices.size(),&vertices[0],GL_STATIC_DRAW);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,sizeof(int)*indices.size(),&indices[0],GL_STATIC_DRAW);

    //VAO pointer index, num of elements, data type, use normalization,stride,start offset
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

void cleanup(Shader& ourShader){
    glUseProgram(0);
    ourShader.del();
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
    sphere_generation(10,10);
    prepare_VAO();

    while(!glfwWindowShouldClose(window)){
        clear();
        draw(ourShader);
        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    cleanup(ourShader);

    glfwTerminate();
    return 0;    
}