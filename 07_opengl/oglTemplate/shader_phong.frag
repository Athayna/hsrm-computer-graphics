#version 330 core

in vec3 frag_position;
in vec3 frag_normal;
in vec3 light_direction;

out vec4 frag_color;

void main()
{
    // Material properties
    vec3 ambient_color = vec3(0.2, 0.2, 0.2); // ambient color of the material
    vec3 diffuse_color = vec3(0.8, 0.8, 0.8); // diffuse color of the material
    vec3 specular_color = vec3(1.0, 1.0, 1.0); // specular color of the material
    float shininess = 32.0; // shininess of the material

    // normalize the fragment normal vector
    vec3 normal = normalize(frag_normal);
    
    // normalize the light direction vector
    vec3 light_dir = normalize(light_direction);
    
    // calculate the view direction (opposite direction of the fragment position)
    vec3 view_dir = normalize(-frag_position);

    // ambient component 
    vec3 ambient = ambient_color;

    // diffuse component (Lambertian shading)
    float diffuse_intensity = max(dot(normal, light_dir), 0.0);
    vec3 diffuse = diffuse_color * diffuse_intensity;

    // specular component (Blinn-Phong shading)
    vec3 reflect_dir = reflect(-light_dir, normal);
    float specular_intensity = pow(max(dot(view_dir, reflect_dir), 0.0), shininess);
    vec3 specular = specular_color * specular_intensity;

    // final color by combining all components and setting alpha to 1 (full opacity)
    vec3 final_color = ambient + diffuse + specular;
    frag_color = vec4(final_color, 1.0);
}
