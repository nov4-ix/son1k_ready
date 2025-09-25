import React, { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

/**
 * SON1KVERS3 — Prototipo navegable (frontend de inmersión)
 * - Single-file React para validar estética y flujo narrativo.
 * - Estilo: terminal hacker + glitch (matrix rain + consola).
 * - Stack: Tailwind + Framer Motion (sin dependencias externas).
 *
 * Contiene 5 vistas:
 *  1) Onboarding (Despertar en la Resistencia)
 *  2) La Terminal (dashboard)
 *  3) Misiones de la Grieta
 *  4) Estudio NOV4-IX
 *  5) Archivos Vivientes
 *
 * Nota: Todo mockeado en front para demo. Listo para conectar a FastAPI.
 */

// ------------------------------ Utilidades UI ------------------------------
const Neon = ({ children, className = "" }) => (
  <span className={`text-neon drop-shadow-[0_0_10px_rgba(0,255,149,0.45)] ${className}`}>{children}</span>
);
const Cyan = ({ children, className = "" }) => (
  <span className={`text-cyan drop-shadow-[0_0_10px_rgba(0,246,255,0.35)] ${className}`}>{children}</span>
);
const Pink = ({ children, className = "" }) => (
  <span className={`text-pink drop-shadow-[0_0_12px_rgba(255,73,195,0.35)] ${className}`}>{children}</span>
);

const Button = ({ variant = "primary", children, className = "", ...props }) => {
  const styles =
    variant === "primary"
      ? "border-neon text-neon bg-gradient-to-b from-neon/15 to-neon/10"
      : variant === "warn"
      ? "border-pink/40 text-pink bg-gradient-to-b from-pink/15 to-pink/10"
      : "border-cyan/40 text-cyan bg-transparent";
  return (
    <button
      {...props}
      className={`inline-flex items-center justify-center gap-2 border rounded-md px-3 py-2 shadow-[0_0_20px_rgba(0,255,149,.08)_inset] ${styles} ${className}`}
    />
  );
};

const TerminalWindow = ({ title, children }) => (
  <section className="w-[min(1100px,92vw)] mx-auto my-4 border border-[#0f3e34] rounded-xl bg-gradient-to-b from-[#06110e] to-[#040908] shadow-[0_0_24px_rgba(0,255,149,.08),_inset_0_0_18px_rgba(0,255,149,.05)]">
    <div className="flex items-center gap-2 px-3 py-2 border-b border-[#0d2f27] bg-[#05120f] text-fg-dim rounded-t-xl">
      <div className="flex gap-1.5 mr-1">
        <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" />
        <span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
        <span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
      </div>
      <div className="truncate">{title}</div>
    </div>
    <div className="p-4">{children}</div>
  </section>
);

const GlitchText = ({ text, as: Tag = "span", className = "" }) => (
  <Tag className={`relative ${className}`} style={{ textShadow: "0 0 10px rgba(0,255,149,.5)" }}>
    {text}
    <span aria-hidden className="absolute left-0 top-0 w-full h-full text-pink/70 pointer-events-none" style={{ mixBlendMode: "screen", transform: "translate(1px,-1px)" }}>{text}</span>
    <span aria-hidden className="absolute left-0 top-0 w-full h-full text-cyan/70 pointer-events-none" style={{ mixBlendMode: "screen", transform: "translate(-1px,1px)" }}>{text}</span>
  </Tag>
);

const AsciiBox = ({ children }) => (
  <div className="border border-dashed border-[#135345] rounded-lg p-3 text-fg leading-relaxed">
    {children}
  </div>
);

// ------------------------------ Matrix Rain BG ------------------------------
const MatrixRain = () => {
  const canvasRef = useRef(null);
  useEffect(() => {
    const c = canvasRef.current;
    const ctx = c.getContext("2d");
    let w = (c.width = window.innerWidth);
    let h = (c.height = window.innerHeight);
    const fontSize = 14;
    const columns = Math.floor(w / fontSize);
    const drops = new Array(columns).fill(1);

    const letters = "アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズヅブプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポ0123456789";

    const draw = () => {
      ctx.fillStyle = "rgba(2,3,4,0.08)"; // trail
      ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = "#00ff95";
      ctx.font = `${fontSize}px ui-monospace, monospace`;
      for (let i = 0; i < drops.length; i++) {
        const text = letters[Math.floor(Math.random() * letters.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        if (drops[i] * fontSize > h && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
      }
      anim = requestAnimationFrame(draw);
    };

    let anim = requestAnimationFrame(draw);
    const onResize = () => {
      w = c.width = window.innerWidth;
      h = c.height = window.innerHeight;
    };
    window.addEventListener("resize", onResize);
    return () => { cancelAnimationFrame(anim); window.removeEventListener("resize", onResize); };
  }, []);
  return <canvas ref={canvasRef} className="fixed inset-0 -z-10" aria-hidden />;
};

// ------------------------------ Estado global simple ------------------------------
const useStory = () => {
  const [view, setView] = useState("onboarding");
  const [soul, setSoul] = useState(null); // alma híbrida
  const [demoUploaded, setDemoUploaded] = useState(false);
  const [feedLine, setFeedLine] = useState("> waiting for submissions …");
  const lines = useMemo(
    () => [
      "> @nova submit --mission 001 --file voz_nova.wav",
      "> @cipher vote --submission 3 --value +1",
      "> @pixel submit --mission 002 --prompt 'cumbia glitch 92bpm'",
    ],
    []
  );
  useEffect(() => {
    const id = setInterval(() => {
      setFeedLine((prev) => lines[(lines.indexOf(prev) + 1) % lines.length]);
    }, 1600);
    return () => clearInterval(id);
  }, [lines]);
  return { view, setView, soul, setSoul, demoUploaded, setDemoUploaded, feedLine };
};

// ------------------------------ Vistas ------------------------------
const Onboarding = ({ story }) => {
  const { setView, setSoul, demoUploaded, setDemoUploaded } = story;
  const [typing, setTyping] = useState("");
  useEffect(() => {
    const full = ""Tu glitch es la chispa de la Liga del No Silencio."";
    let i = 0;
    const id = setInterval(() => {
      setTyping(full.slice(0, ++i));
      if (i >= full.length) clearInterval(id);
    }, 18);
    return () => clearInterval(id);
  }, []);

  return (
    <TerminalWindow title="/boot/resistencia">
      <div className="text-neon">[BOOTING] Accessing NODE // RESISTENCIA …</div>
      <div className="mt-1">{"> Mensaje entrante: "}<Cyan>BELLA.exe</Cyan></div>
      <div className="mt-1"><GlitchText text={typing} /></div>

      <div className="my-3 h-px bg-cyan/20" />
      <div>[UPLOAD REQUIRED] La puerta solo se abre con una <span className="px-1.5 py-0.5 border border-cyan/30 rounded text-cyan">demo real</span>.</div>
      <AsciiBox>
        ┌──────── DROP YOUR RAW DEMO (.wav) ────────┐<br/>
        │  [ arrastra aquí ]  ó  <Button variant="warn" onClick={() => setDemoUploaded(true)}>grabar .wav</Button>  │<br/>
        └───────────────────────────────────────────┘
        <div className="mt-2 text-fg-dim">Estado: {demoUploaded ? <Neon>DEMO CAPTURADA ✔</Neon> : "esperando…"}</div>
      </AsciiBox>

      <div className="mt-3">{"> ALMA_HIBRIDA — elige un arquetipo:"}</div>
      <div className="flex flex-wrap gap-2 mt-2">
        {["PIXEL","BELLA","NOVA","CIPHER"].map(a => (
          <Button key={a} onClick={() => setSoul(a)}>{`[ ${a} ]`}</Button>
        ))}
      </div>

      <div className="my-3 h-px bg-cyan/20" />
      <div className="text-gold">"Lo imperfecto también es sagrado."</div>
      <div className="mt-3 flex items-center gap-3">
        <Button
          variant="primary"
          onClick={() => (demoUploaded ? setView("terminal") : alert("Sube una demo primero (ritual de acceso)"))}
        >
          ◯⚡ DESPERTAR
        </Button>
        <span className="text-fg-dim animate-blink">▌</span>
      </div>
    </TerminalWindow>
  );
};

const Dashboard = ({ story }) => {
  const { setView, soul } = story;
  return (
    <TerminalWindow title="/terminal">
      <div>
        <Neon>Bienvenido a La Terminal</Neon>{" "}
        <span className="text-fg-dim">— nodo seguro de la Resistencia</span>
      </div>
      <div className="text-fg-dim mt-1">Perfil: {soul ? <Cyan>{soul}</Cyan> : "anónimo"}</div>

      <div className="grid gap-3 sm:grid-cols-2 mt-4">
        <div className="border border-[#0f3e34] bg-[#06110e] rounded-lg p-3">
          <div className="text-cyan">> commands</div>
          <div className="mt-2 flex flex-wrap gap-2">
            <Button onClick={() => setView("misiones")}>missions</Button>
            <Button onClick={() => setView("studio")}>studio</Button>
            <Button onClick={() => setView("archivo")}>archive</Button>
          </div>
        </div>
        <div className="border border-[#0f3e34] bg-[#06110e] rounded-lg p-3">
          <div className="text-cyan">> mantra</div>
          <GlitchText className="block mt-2" text="Lo imperfecto también es sagrado." />
        </div>
      </div>
    </TerminalWindow>
  );
};

const Misiones = ({ story }) => {
  const { feedLine } = story;
  const missions = [
    { id: 1, title: "Amplifica el eco de Nikolay", brief: "mezcla identidades · beats del este · cumbia" },
    { id: 2, title: "Fusión cumbia + beats rusos", brief: "ritmo híbrido · colaboración en vivo" },
    { id: 3, title: "Rescata voces del Estudio Fantasma", brief: "reliquias · rescate glitch · curaduría" },
  ];
  return (
    <TerminalWindow title="/grieta/misiones">
      <div className="text-cyan">> FETCHING ACTIVE MISSIONS …</div>
      <div className="grid gap-3 grid-cols-[repeat(auto-fit,minmax(260px,1fr))] mt-3">
        {missions.map((m) => (
          <article key={m.id} className="border border-[#0f3e34] p-3 rounded bg-[#06110e]">
            <h4 className="m-0 text-cyan">{String(m.id).padStart(3, "0")} · {m.title}</h4>
            <div className="text-fg-dim text-sm">{m.brief}</div>
            <div className="flex gap-2 mt-2">
              <Button variant="ghost">submit --mission {m.id}</Button>
              <Button variant="ghost">open --feed {m.id}</Button>
            </div>
          </article>
        ))}
      </div>
      <div className="my-3 h-px bg-cyan/20" />
      <div>> LIVE FEED</div>
      <AsciiBox>{feedLine}</AsciiBox>
    </TerminalWindow>
  );
};

const Studio = () => {
  const [out, setOut] = useState("awaiting…");
  const [params, setParams] = useState({ memoria: 0.72, distorsion: 0.38, variacion: 0.88 });

  const Knob = ({ label, vKey }) => (
    <div className="grid grid-cols-[220px_1fr_60px] items-center gap-3 my-2">
      <label className="text-cyan">{label}</label>
      <div className="relative h-2 bg-[#0b1f1a] border border-[#0f3e34] rounded-full overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-pink/40 to-cyan/40" />
        <input
          type="range"
          min={0}
          max={1}
          step={0.01}
          value={params[vKey]}
          onChange={(e) => setParams((p) => ({ ...p, [vKey]: Number(e.target.value) }))}
          className="absolute w-full h-2 opacity-0 cursor-ew-resize"
        />
        <div
          className="absolute -top-1.5 h-5 w-5 rounded-full bg-gold"
          style={{ left: `calc(${Math.round(params[vKey] * 100)}% - 10px)` }}
        />
      </div>
      <code>{params[vKey].toFixed(2)}</code>
    </div>
  );

  const generate = () => {
    setOut("[ ... grietas iluminándose ... ]");
    setTimeout(() => {
      const seed = Math.floor(1000 + Math.random() * 9000);
      setOut(`TRACK_GENERATED.wav · duration=00:28 · seed=${seed}`);
    }, 1200);
  };

  return (
    <TerminalWindow title="/studio/nov4-ix">
      <div>> STUDIO_MODE: NOV4-IX <span className="text-ok">[ON]</span></div>
      <div className="border border-dashed border-[#135345] rounded-lg p-3 mt-2">
        <Knob label="MEMORIA_GLITCH" vKey="memoria" />
        <Knob label="DISTORSION_EMOC" vKey="distorsion" />
        <Knob label="VARIACION_SAGRADA" vKey="variacion" />
      </div>
      <div className="flex gap-2 mt-3">
        <Button variant="primary" onClick={generate}>EXECUTE generate --preset nov4ix</Button>
        <Button variant="warn">toggle --nov4ix OFF</Button>
      </div>
      <div className="my-3 h-px bg-cyan/20" />
      <div>Output:</div>
      <AsciiBox>{out}</AsciiBox>
    </TerminalWindow>
  );
};

const Archivo = () => (
  <TerminalWindow title="/archivo/viviente">
    <div>> ARCHIVO_VIVIENTE ACCESS — reliquias</div>
    <div className="flex gap-2 mt-2">
      <div className="border border-dashed border-[#135345] rounded-lg p-3 grow">
        UPLOAD: relic_demo.wav <Button variant="warn">subir</Button>
      </div>
      <Button variant="ghost">run RESCATE_GLITCH</Button>
    </div>
    <div className="my-3 h-px bg-cyan/20" />
    <div>> JOB:</div>
    <AsciiBox>███▒▒▒▒▒▒▒▒▒ 28%</AsciiBox>
    <div className="flex gap-2 mt-2">
      <Button variant="primary">[ RESCATAR ◯⚡ ]</Button>
      <Button variant="ghost">[ ARCHIVAR X ]</Button>
    </div>
  </TerminalWindow>
);

// ------------------------------ Navigation Shell ------------------------------
const Topbar = ({ current, go }) => (
  <header className="sticky top-0 z-10 flex items-center justify-between px-3 py-2 border-b border-[#07241e] bg-[#030908] shadow-[0_0_24px_rgba(0,255,149,.08)]">
    <div className="flex items-center gap-3">
      <span className="text-cyan font-bold">△◯ SON1KVERS3</span>
      <span className="text-gold/95">ALT + CTRL + Humanity</span>
    </div>
    <nav className="flex gap-2">
      {[
        { k: "onboarding", label: "Onboarding" },
        { k: "terminal", label: "Terminal" },
        { k: "misiones", label: "Grieta" },
        { k: "studio", label: "NOV4-IX" },
        { k: "archivo", label: "Archivo" },
      ].map((t) => (
        <button
          key={t.k}
          onClick={() => go(t.k)}
          className={`border border-[#0d3c31] bg-[#071412] rounded px-2 py-1 hover:border-neon hover:text-neon ${current === t.k ? "border-neon text-neon" : ""}`}
        >
          {t.label}
        </button>
      ))}
    </nav>
  </header>
);

// ------------------------------ App principal ------------------------------
export default function App() {
  const story = useStory();
  const { view, setView } = story;

  return (
    <div className="min-h-screen">
      <MatrixRain />
      <Topbar current={view} go={setView} />

      <main>
        <AnimatePresence mode="wait">
          <motion.div
            key={view}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25 }}
          >
            {view === "onboarding" && <Onboarding story={story} />}
            {view === "terminal" && <Dashboard story={story} />}
            {view === "misiones" && <Misiones story={story} />}
            {view === "studio" && <Studio />}
            {view === "archivo" && <Archivo />}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* scanlines sutiles */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 mix-blend-overlay opacity-25 scanlines"
      />
    </div>
  );
}

