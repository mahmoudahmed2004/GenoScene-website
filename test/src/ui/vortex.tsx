"use client";
import React, { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

interface VortexProps {
  children?: React.ReactNode;
  className?: string;
  containerClassName?: string;
  backgroundColor?: string;
}

export const Vortex = ({
  children,
  className,
  containerClassName,
  backgroundColor = "transparent",
}: VortexProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d", { alpha: true });
    if (!ctx) return;

    let animationFrameId: number;
    let time = 0;

    const resize = () => {
      if (!containerRef.current) return;
      // High DPI screens support for ultra crisp rendering
      const dpr = window.devicePixelRatio || 1;
      canvas.width = containerRef.current.offsetWidth * dpr;
      canvas.height = containerRef.current.offsetHeight * dpr;
      ctx.scale(dpr, dpr);
    };
    window.addEventListener("resize", resize);
    resize();

    // Floating micro-particles (Energy Dust)
    const dust: any[] = [];
    const numDust = typeof window !== "undefined" && window.innerWidth < 768 ? 60 : 180;
    for(let i=0; i<numDust; i++) {
        dust.push({
            x: Math.random() * 2000 - 1000,
            y: Math.random() * 1000 - 500,
            z: Math.random() * 800 - 400,
            size: Math.random() * 2 + 0.5,
            offset: Math.random() * Math.PI * 2,
            speedY: (Math.random() - 0.5) * 0.5,
            hue: Math.random() * 60 + 190
        });
    }

    function rotate3D(x: number, y: number, z: number, pitch: number, yaw: number, roll: number) {
      // Roll (Z)
      let x1 = x * Math.cos(roll) - y * Math.sin(roll);
      let y1 = x * Math.sin(roll) + y * Math.cos(roll);
      // Pitch (X)
      let y2 = y1 * Math.cos(pitch) - z * Math.sin(pitch);
      let z2 = y1 * Math.sin(pitch) + z * Math.cos(pitch);
      // Yaw (Y)
      let x3 = x1 * Math.cos(yaw) + z2 * Math.sin(yaw);
      let z3 = -x1 * Math.sin(yaw) + z2 * Math.cos(yaw);
      return { x: x3, y: y2, z: z3 };
    }

    const draw = () => {
      const w = canvas.width / (window.devicePixelRatio || 1);
      const h = canvas.height / (window.devicePixelRatio || 1);

      if (backgroundColor === "transparent") {
          ctx.clearRect(0, 0, w, h);
      } else {
          ctx.fillStyle = backgroundColor;
          ctx.fillRect(0, 0, w, h);
      }
      
      const isMobile = w < 768;

      const centerX = w / 2;
      const centerY = h / 2;
      
      // Dynamic camera perspective that scales on mobile
      const fov = isMobile ? w * 2.5 : 800; 
      
      let elements: any[] = [];
      const totalWidth = w * 2.5; 
      const startX = -totalWidth / 2;

      // DNA Aesthetics Parameters
      // Mobile DNA should be proportionally wider relative to screen width
      const helixRadius = isMobile ? Math.min(w, h) * 0.40 : Math.min(w, h) * 0.28; 
      const frequency = isMobile ? 0.009 : 0.007; // Tighter twist on small screen
      const movementSpeed = 1.5;

      // Generate Structural Sequence
      const numSegments = isMobile ? 40 : 100;
      const segmentSpacing = totalWidth / numSegments;
      const offsetX = (time * movementSpeed) % segmentSpacing;

      // Dynamic Rotation
      const pitch = 0.1 + Math.sin(time * 0.01) * 0.05; 
      const yaw = -0.3; 
      const barrelRoll = time * 0.005; 

      // Adjusted Sizes for Mobile
      const baseNodeScale = isMobile ? 5 : 10;
      const rungLineWidth = isMobile ? 2.5 : 4;
      const backboneLineWidth = isMobile ? 3 : 6;
      const backboneHighlightWidth = isMobile ? 1 : 2;

      for (let i = 0; i <= numSegments + 1; i++) {
          let cx = startX + (i * segmentSpacing) - offsetX;
          const phase = cx * frequency;
          
          let yA = Math.sin(phase) * helixRadius;
          let zA = Math.cos(phase) * helixRadius;
          let yB = Math.sin(phase + Math.PI) * helixRadius;
          let zB = Math.cos(phase + Math.PI) * helixRadius;

          let pA = rotate3D(cx, yA, zA, pitch, yaw, barrelRoll);
          let pB = rotate3D(cx, yB, zB, pitch, yaw, barrelRoll);

          // Iridescent holographic color mapping
          let baseHue = 210 + Math.sin(cx * 0.003 + time * 0.02) * 50; 

          // Nucleotides (Spheres)
          elements.push({ type: 'sphere', point: pA, size: baseNodeScale, hue: baseHue });
          elements.push({ type: 'sphere', point: pB, size: baseNodeScale, hue: baseHue + 40 });

          // Rungs
          if (i % 2 === 0) { 
              elements.push({
                  type: 'rung',
                  pA: pA,
                  pB: pB,
                  z: (pA.z + pB.z) / 2,
                  hue: baseHue + 20
              });
          }

          // Backbone
          if (i > 0) {
             let prevCx = startX + ((i-1) * segmentSpacing) - offsetX;
             let prevPhase = prevCx * frequency;
             let prevYA = Math.sin(prevPhase) * helixRadius;
             let prevZA = Math.cos(prevPhase) * helixRadius;
             let prevYB = Math.sin(prevPhase + Math.PI) * helixRadius;
             let prevZB = Math.cos(prevPhase + Math.PI) * helixRadius;

             let prevPA = rotate3D(prevCx, prevYA, prevZA, pitch, yaw, barrelRoll);
             let prevPB = rotate3D(prevCx, prevYB, prevZB, pitch, yaw, barrelRoll);

             elements.push({ type: 'backbone', pA: prevPA, pB: pA, z: (prevPA.z + pA.z)/2, hue: baseHue });
             elements.push({ type: 'backbone', pA: prevPB, pB: pB, z: (prevPB.z + pB.z)/2, hue: baseHue + 40 });
          }
      }

      // Process Dust
      dust.forEach(d => {
          d.x -= movementSpeed * 0.5; 
          d.y += d.speedY;
          d.x += Math.cos(time * 0.02 + d.offset) * 1.5;
          if (d.x < startX) { d.x = startX + totalWidth; d.y = Math.random() * 1000 - 500; }
          
          let p = rotate3D(d.x, d.y, d.z, pitch, yaw, barrelRoll);
          elements.push({ type: 'dust', point: p, size: d.size, hue: d.hue });
      });

      // Z-Sort (Painter's algorithm)
      elements.sort((a, b) => {
          let zA = (a.type === 'sphere' || a.type === 'dust') ? a.point.z : a.z;
          let zB = (b.type === 'sphere' || b.type === 'dust') ? b.point.z : b.z;
          return zB - zA;
      });

      // Render
      elements.forEach(el => {
          // Compute Alpha based on Depth (DoF) for absolute 3D realism
          const getAlpha = (z: number) => Math.max(0.1, 1 - Math.abs(z) / 1000);

          if (el.type === 'sphere') {
             const scale = fov / (fov + el.point.z);
             if (scale <= 0) return;
             const sx = centerX + el.point.x * scale;
             const sy = centerY + el.point.y * scale;
             const sSize = el.size * scale;
             const alpha = getAlpha(el.point.z);

             // Outer Glow
             ctx.beginPath();
             ctx.arc(sx, sy, sSize * 2.5, 0, Math.PI * 2);
             ctx.fillStyle = `hsla(${el.hue}, 90%, 60%, ${alpha * 0.2})`;
             ctx.fill();

             // Solid Body
             ctx.beginPath();
             ctx.arc(sx, sy, sSize, 0, Math.PI * 2);
             const gradient = ctx.createRadialGradient(sx - sSize*0.3, sy - sSize*0.3, 0, sx, sy, sSize);
             gradient.addColorStop(0, `hsla(${el.hue}, 100%, 90%, ${alpha})`);
             gradient.addColorStop(0.6, `hsla(${el.hue}, 90%, 50%, ${alpha})`);
             gradient.addColorStop(1, `hsla(${el.hue}, 80%, 20%, ${alpha})`);
             ctx.fillStyle = gradient;
             ctx.fill();

          } else if (el.type === 'rung' || el.type === 'backbone') {
             const scaleA = fov / (fov + el.pA.z);
             const scaleB = fov / (fov + el.pB.z);
             if (scaleA <= 0 || scaleB <= 0) return;
             
             const sxA = centerX + el.pA.x * scaleA;
             const syA = centerY + el.pA.y * scaleA;
             const sxB = centerX + el.pB.x * scaleB;
             const syB = centerY + el.pB.y * scaleB;

             const avgScale = (scaleA + scaleB) / 2;
             const alpha = getAlpha(el.z);
             
             // Base Tube
             ctx.beginPath();
             ctx.moveTo(sxA, syA);
             ctx.lineTo(sxB, syB);
             ctx.lineWidth = (el.type === 'backbone' ? backboneLineWidth : rungLineWidth) * avgScale;
             ctx.strokeStyle = `hsla(${el.hue}, 80%, 40%, ${alpha * 0.8})`;
             ctx.lineCap = "round";
             ctx.stroke();

             // Inner Highlight
             ctx.beginPath();
             ctx.moveTo(sxA, syA);
             ctx.lineTo(sxB, syB);
             ctx.lineWidth = (el.type === 'backbone' ? backboneHighlightWidth : 1) * avgScale;
             ctx.strokeStyle = `hsla(${el.hue}, 100%, 80%, ${alpha})`;
             ctx.stroke();

          } else if (el.type === 'dust') {
             const scale = fov / (fov + el.point.z);
             if (scale <= 0) return;
             const sx = centerX + el.point.x * scale;
             const sy = centerY + el.point.y * scale;
             const alpha = getAlpha(el.point.z);
             
             ctx.beginPath();
             ctx.arc(sx, sy, el.size * scale, 0, Math.PI * 2);
             ctx.fillStyle = `hsla(${el.hue}, 80%, 70%, ${alpha * 0.8})`;
             ctx.fill();
          }
      });

      time++;
      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [backgroundColor]);

  return (
    <div ref={containerRef} className={cn("relative w-full h-full", containerClassName)}>
      <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none" />
      <div className={cn("relative z-10 h-full w-full", className)}>
        {children}
      </div>
    </div>
  );
};
