// "ShaderToy Tutorial - Hexagonal Tiling"
// by Martijn Steinrucken aka BigWings/CountFrolic - 2019
// License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
//
// This shader is part of a tutorial on YouTube
// https://youtu.be/VmrIDyYiJBA

float HexDist(vec2 p) {
	p = abs(p);

    float c = dot(p, normalize(vec2(1,1.73)));
    c = max(c, p.x);

    return c;
}

vec4 HexCoords(vec2 uv) {
	vec2 r = vec2(1, 1.73);
    vec2 h = r*.5;

    vec2 a = mod(uv, r)-h;
    vec2 b = mod(uv-h, r)-h;

    vec2 gv = dot(a, a) < dot(b,b) ? a : b;

    float x = atan(gv.x, gv.y);
    float y = .5-HexDist(gv);
    vec2 id = uv-gv;
    return vec4(x, y, id.x,id.y);
}

void main()
{
    vec2 uv = (fragCoord-.5*iResolution.xy)/iResolution.y;

    vec3 col = vec3(0);

    uv *= 10.;

    vec4 hc = HexCoords(uv+100.);

    float c = smoothstep(.01, .03, hc.y*sin(hc.z*hc.w+iTime));

    col += c;

    fragColor = vec4(col,1.0);
}
