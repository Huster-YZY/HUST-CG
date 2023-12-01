#version 330 core
layout (location=0) in vec3 aPos;
out vec4 vertexColor;
uniform vec4 ourColor;
void main()
{
  gl_Position=vec4(aPos.x+ourColor.g,aPos.y+ourColor.g,aPos.z+ourColor.g,1.0);
  vertexColor=vec4(0.5,0.0,0.0,1.0);
}