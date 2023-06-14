#version 330 core

uniform mat4 modelview_projection_matrix;
uniform vec3 light_position;

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

out vec3 frag_position;
out vec3 frag_normal;
out vec3 light_direction;

void main()
{
    // transform the vertex position using the modelview_projection_matrix
    gl_Position = modelview_projection_matrix * vec4(position, 1.0);

    // pass the position, normal, and light direction to the fragment shader
    frag_position = position;
    frag_normal = normal;

    // calculate the light direction by subtracting the vertex position from the light position
    light_direction = normalize(light_position - position);
}
