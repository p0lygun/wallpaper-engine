void main(){
    //Clear base color.
    fragColor-=fragColor;

    //Iterate though 400 points and add them to the output color.
    for (float i=-1.; i<1.; i+=6e-3)
    {
        vec2 r = iResolution.xy, //A shortened resolution variable, because we use it twice.
        p = cos(i*4e2+iTime+vec2(0, 11))*sqrt(1.-i*i);//Rotate and scale xy coordinates.
        fragColor += (cos(i+vec4(0, 2, 4, 6))+1.)*(1.-p.y) / //Color and brightness.
        dot(p=(fragCoord+fragCoord-r)/r.y+vec2(p.x, i)/(p.y+2.), p)/3e4;

    }
}
