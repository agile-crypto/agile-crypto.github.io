import re, sys
import os
tpl = open(os.environ.get('VIEWER_TEMPLATE', os.path.expanduser('~/.agents/skills/algorithmic-art/templates/viewer.html'))).read()
core = open(sys.argv[1]).read()
out = sys.argv[2]
s = tpl
s = s.replace('<title>Generative Art Viewer</title>', '<title>Graceful Exchange: Citius hero art</title>')
s = s.replace('<h1>TITLE - EDIT</h1>', '<h1>Graceful Exchange</h1>')
s = s.replace('<div class="subtitle">SUBHEADER - EDIT</div>', '<div class="subtitle">Strands that trade places and change colour without breaking. Choose a seed for the Citius hero.</div>')
s = s.replace('value="12345" onchange="updateSeed()"', 'value="7" onchange="updateSeed()"')
def slider(pid, label, mn, mx, step, val):
    return f'''                <div class="control-group">
                    <label>{label}</label>
                    <div class="slider-container">
                        <input type="range" id="{pid}" min="{mn}" max="{mx}" step="{step}" value="{val}" oninput="updateParam('{pid}', this.value)">
                        <span class="value-display" id="{pid}-value">{val}</span>
                    </div>
                </div>
'''
params_html = ('            <div class="control-section">\n                <h3>Parameters</h3>\n'
  + slider('speed', 'Speed (px per second)', 0, 120, 1, 22)
  + slider('lines', 'Line count', 6, 90, 1, 34)
  + slider('swap', 'Exchange density', 0.05, 0.9, 0.01, 0.42)
  + slider('migrate', 'Colour change rate', 0, 0.15, 0.005, 0.035)
  + slider('stage', 'Stage spacing (px)', 70, 320, 5, 150)
  + slider('weight', 'Line weight (px)', 0.5, 4, 0.25, 1.25)
  + slider('opacity', 'Opacity', 0.15, 1, 0.05, 0.55)
  + '            </div>\n')
a = s.index('            <!-- Parameters Section (CUSTOMIZE THIS FOR YOUR ART) -->')
b = s.index('            <!-- Colors Section (OPTIONAL - CUSTOMIZE OR REMOVE) -->')
s = s[:a] + '            <!-- Parameters Section (CUSTOMIZE THIS FOR YOUR ART) -->\n' + params_html + '\n' + s[b:]
def color(cid, label, val):
    return f'''                <div class="color-group">
                    <label>{label}</label>
                    <div class="color-picker-container">
                        <input type="color" id="{cid}" value="{val}" oninput="updateColor('{cid}', this.value)">
                        <span class="color-value" id="{cid}-value">{val}</span>
                    </div>
                </div>
'''
colors_html = ('            <div class="control-section">\n                <h3>Colors</h3>\n'
  + color('color1', 'Before the exchange', '#a8a8a8')
  + color('color2', 'After the exchange', '#0f62fe')
  + color('color3', 'Second generation', '#009d9a')
  + color('background', 'Ground', '#ffffff')
  + '            </div>\n')
a = s.index('            <!-- Colors Section (OPTIONAL - CUSTOMIZE OR REMOVE) -->')
b = s.index('            <!-- Actions Section (ALWAYS KEEP THIS) -->')
s = s[:a] + '            <!-- Colors Section (OPTIONAL - CUSTOMIZE OR REMOVE) -->\n' + colors_html + '\n' + s[b:]
s = s.replace('''                <div class="button-row">
                    <button class="button" onclick="resetParameters()">Reset</button>
                </div>''', '''                <div class="button-row">
                    <button class="button" onclick="regenerate()">Regenerate</button>
                    <button class="button" onclick="resetParameters()">Reset</button>
                </div>
                <div class="button-row" style="margin-top: 8px;">
                    <button class="button secondary" id="pause" onclick="togglePause()">Pause</button>
                    <button class="button tertiary" onclick="saveCanvas('graceful-exchange-' + params.seed, 'png')">Download PNG</button>
                </div>''')
# script: replace from params block to SEED CONTROL FUNCTIONS
a = s.index('        let params = {')
b = s.index('        // ═══════════════════════════════════════════════════════════════════════\n        // SEED CONTROL FUNCTIONS - ALWAYS KEEP THESE')
algo = '''        let params = {
            seed: 7,
            speed: 22,
            lines: 34,
            swap: 0.42,
            migrate: 0.035,
            stage: 150,
            weight: 1.25,
            opacity: 0.55,
            colorPalette: ['#a8a8a8', '#0f62fe', '#009d9a'],
            background: '#ffffff'
        };

        let defaultParams = JSON.parse(JSON.stringify(params)); // Store defaults for reset

        // ═══════════════════════════════════════════════════════════════════════
        // P5.JS GENERATIVE ART ALGORITHM - GRACEFUL EXCHANGE
        // The core lives in assets/exchange.js on the website and is inlined here
        // unchanged, so the viewer and the hero draw the same artwork.
        // ═══════════════════════════════════════════════════════════════════════

''' + '\n'.join('        ' + l if l.strip() else '' for l in core.splitlines()) + '''

        let art, offset = 0, paused = false;

        function artParams() {
            return { seed: params.seed, lines: params.lines, speed: params.speed, swap: params.swap,
                     migrate: params.migrate, stage: params.stage, weight: params.weight, opacity: params.opacity,
                     colors: params.colorPalette.slice(), background: params.background };
        }

        function setup() {
            let canvas = createCanvas(1440, 720);   // the hero's 2:1 frame
            canvas.parent('canvas-container');
            initializeSystem();
            document.querySelector('.loading').style.display = 'none';
        }

        function initializeSystem() {
            randomSeed(params.seed);   // p5's own generators are seeded too; the art uses its seeded hash
            noiseSeed(params.seed);
            art = new GracefulExchange(artParams());
            offset = 0;
            if (paused) redraw();
        }

        function draw() {
            if (!paused) offset += (deltaTime / 1000) * params.speed;
            art.draw(drawingContext, width, height, offset);
        }

        function regenerate() { initializeSystem(); }

        function togglePause() {
            paused = !paused;
            document.getElementById('pause').textContent = paused ? 'Play' : 'Pause';
        }

        // ═══════════════════════════════════════════════════════════════════════
        // UI CONTROL HANDLERS
        // ═══════════════════════════════════════════════════════════════════════

        function updateParam(paramName, value) {
            params[paramName] = parseFloat(value);
            document.getElementById(paramName + '-value').textContent = value;
            if (paramName === 'speed') { art.p.speed = params.speed; return; }   // speed changes the drift only
            if (['weight', 'opacity'].includes(paramName)) { art.p[paramName] = params[paramName]; return; }
            const keep = offset;
            art = new GracefulExchange(artParams());
            offset = keep;
        }

        function updateColor(colorId, value) {
            if (colorId === 'background') params.background = value;
            else params.colorPalette[{ color1: 0, color2: 1, color3: 2 }[colorId]] = value;
            document.getElementById(colorId + '-value').textContent = value;
            art.set({ colors: params.colorPalette.slice(), background: params.background });
        }

'''
s = s[:a] + algo + s[b:]
# reset: rewrite to our controls
a = s.index('        function resetParameters() {')
b = s.index('        // Initialize UI on load')
reset = '''        function resetParameters() {
            const seed = params.seed;
            params = JSON.parse(JSON.stringify(defaultParams));
            params.seed = seed;
            ['speed', 'lines', 'swap', 'migrate', 'stage', 'weight', 'opacity'].forEach(function (k) {
                document.getElementById(k).value = params[k];
                document.getElementById(k + '-value').textContent = params[k];
            });
            ['color1', 'color2', 'color3'].forEach(function (k, i) {
                document.getElementById(k).value = params.colorPalette[i];
                document.getElementById(k + '-value').textContent = params.colorPalette[i];
            });
            document.getElementById('background').value = params.background;
            document.getElementById('background-value').textContent = params.background;
            updateSeedDisplay();
            initializeSystem();
        }

'''
s = s[:a] + reset + s[b:]
s = s.replace('max-width: 1000px;', 'max-width: 1200px;')
open(out, 'w').write(s)
print('ok', len(s))
