#version 330 core

in vec3 frag_normal;
in vec3 frag_light_direction;

out vec4 fragment_color;

void main()
{
    vec3 ambient_color = vec3(0.2, 0.2, 0.2); // minimum amount of light (darker grey)
    vec3 diffuse_color = vec3(0.8, 0.8, 0.8); // color on surface under direct light (lighter grey)
    
    // calculate intensity of diffuse color
    float diffuse_intensity = max(dot(frag_normal, frag_light_direction), 0.0);
    
    // combine ambient and diffuse color
    vec3 final_color = ambient_color + diffuse_intensity * diffuse_color;
    
    // output fragment color with alpha set to 1 (full opacity)
    fragment_color = vec4(final_color, 1.0);
}
