#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;

uniform mat4 modelview_projection_matrix;
uniform vec3 light_position;

out vec3 frag_normal;
out vec3 frag_light_direction;

void main()
{
    // Transform the vertex position using the modelview_projection_matrix
    gl_Position = modelview_projection_matrix * vec4(position, 1.0);
    
    // Pass normalized normals to fragment shader for later lighting calculations
    frag_normal = normalize(normal);

    // Calculate the light direction by subtracting the vertex position from the light position
    frag_light_direction = normalize(light_position - position);
}
