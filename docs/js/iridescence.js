/**
 * Iridescence WebGL Background
 * Vanilla JS adaptation using OGL (loaded via CDN as ES module)
 * Renders an animated iridescent shader behind the hero section
 */
import { Renderer, Program, Mesh, Color, Triangle } from 'https://cdn.jsdelivr.net/npm/ogl/+esm';

const vertexShader = `
attribute vec2 uv;
attribute vec2 position;

varying vec2 vUv;

void main() {
  vUv = uv;
  gl_Position = vec4(position, 0, 1);
}
`;

const fragmentShader = `
precision highp float;

uniform float uTime;
uniform vec3 uColor;
uniform float uIsLight;
uniform vec3 uResolution;
uniform vec2 uMouse;
uniform float uAmplitude;
uniform float uSpeed;

varying vec2 vUv;

void main() {
  float mr = min(uResolution.x, uResolution.y);
  vec2 uv = (vUv.xy * 2.0 - 1.0) * uResolution.xy / mr;

  uv += (uMouse - vec2(0.5)) * uAmplitude;

  float d = -uTime * 0.5 * uSpeed;
  float a = 0.0;
  for (float i = 0.0; i < 8.0; ++i) {
    a += cos(i - d - a * uv.x);
    d += sin(uv.y * i + a);
  }
  d += uTime * 0.5 * uSpeed;
  vec3 col = vec3(cos(uv * vec2(d, a)) * 0.6 + 0.4, cos(a + d) * 0.5 + 0.5);
  vec3 darkCol = cos(col * cos(vec3(d, a, 2.5)) * 0.5 + 0.5) * uColor;
  
  if (uIsLight > 0.5) {
      // Light Mode: mix pastel white with the dark iridescent colors
      vec3 lightBlend = mix(vec3(0.96, 0.98, 1.0), darkCol, 0.4);
      gl_FragColor = vec4(lightBlend, 1.0);
  } else {
      gl_FragColor = vec4(darkCol, 1.0);
  }
}
`;

(function initIridescence() {
    const container = document.getElementById('iridescence-bg');
    if (!container) return;

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const config = {
        colorDark: [0, 0.9, 1],
        colorLight: [0.1, 0.5, 1.0], // Vibrant light blue for light mode
        speed: prefersReducedMotion ? 0 : 1.0,
        amplitude: 0.1,
        mouseReact: false,
    };

    let renderer, program, mesh, animateId;

    try {
        renderer = new Renderer({ alpha: false, antialias: true });
    } catch (e) {
        // WebGL not available — CSS fallback gradient will show
        console.warn('WebGL not available, falling back to CSS gradient.');
        container.classList.add('iridescence-fallback');
        return;
    }

    const gl = renderer.gl;

    function updateThemeColors() {
        const isLight = document.body && document.body.classList.contains('light-theme');
        if (isLight) {
            gl.clearColor(0.94, 0.96, 0.98, 1); // matches light var(--bg-main)
            if (program) {
                program.uniforms.uColor.value.set(config.colorLight);
                program.uniforms.uIsLight.value = 1.0;
            }
        } else {
            gl.clearColor(0.18, 0.2, 0.25, 1); // matches var(--bg-main) #2e3440
            if (program) {
                program.uniforms.uColor.value.set(config.colorDark);
                program.uniforms.uIsLight.value = 0.0;
            }
        }
    }

    updateThemeColors();

    function resize() {
        const scale = window.devicePixelRatio > 1 ? 0.75 : 1; // Reduce resolution on HiDPI for performance
        renderer.setSize(container.offsetWidth * scale, container.offsetHeight * scale);
        gl.canvas.style.width = container.offsetWidth + 'px';
        gl.canvas.style.height = container.offsetHeight + 'px';
        if (program) {
            program.uniforms.uResolution.value = new Color(
                gl.canvas.width,
                gl.canvas.height,
                gl.canvas.width / gl.canvas.height
            );
        }
    }

    window.addEventListener('resize', resize, false);

    const geometry = new Triangle(gl);
    program = new Program(gl, {
        vertex: vertexShader,
        fragment: fragmentShader,
        uniforms: {
            uTime: { value: 0 },
            uColor: { value: new Color(...(document.body && document.body.classList.contains('light-theme') ? config.colorLight : config.colorDark)) },
            uIsLight: { value: (document.body && document.body.classList.contains('light-theme')) ? 1.0 : 0.0 },
            uResolution: {
                value: new Color(gl.canvas.width, gl.canvas.height, gl.canvas.width / gl.canvas.height),
            },
            uMouse: { value: new Float32Array([0.5, 0.5]) },
            uAmplitude: { value: config.amplitude },
            uSpeed: { value: config.speed },
        },
    });

    mesh = new Mesh(gl, { geometry, program });

    // Initial resize
    resize();

    // Animation loop
    function update(t) {
        animateId = requestAnimationFrame(update);
        program.uniforms.uTime.value = t * 0.001;
        renderer.render({ scene: mesh });
    }

    animateId = requestAnimationFrame(update);
    container.appendChild(gl.canvas);

    // Listen for reduced motion changes at runtime
    window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
        program.uniforms.uSpeed.value = e.matches ? 0 : 1.0;
    });

    if (document.body) {
        const observer = new MutationObserver(() => updateThemeColors());
        observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        cancelAnimationFrame(animateId);
        window.removeEventListener('resize', resize);
        gl.getExtension('WEBGL_lose_context')?.loseContext();
    });
})();
