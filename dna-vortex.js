document.addEventListener('DOMContentLoaded', () => {
  const hero = document.querySelector('.hero');
  const background = document.getElementById('dnaVortexBackground');
  const canvas = document.getElementById('dnaVortexCanvas');

  if (!hero || !background || !canvas) return;

  const ctx = canvas.getContext('2d', { alpha: true });
  if (!ctx) return;

  let animationFrameId = null;
  let time = 0;
  let isActive = false;
  let width = window.innerWidth;
  let height = window.innerHeight;
  const dust = [];
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const pointer = {
    targetX: 0,
    targetY: 0,
    x: 0,
    y: 0,
    pixelX: width / 2,
    pixelY: height / 2,
    isPresent: false
  };

  const makeDust = () => {
    dust.length = 0;
    const count = width < 768 ? 48 : 120;

    for (let i = 0; i < count; i += 1) {
      dust.push({
        x: Math.random() * 2000 - 1000,
        y: Math.random() * 1000 - 500,
        z: Math.random() * 800 - 400,
        size: Math.random() * 1.7 + 0.45,
        offset: Math.random() * Math.PI * 2,
        speedY: (Math.random() - 0.5) * 0.34,
        hue: Math.random() * 60 + 190
      });
    }
  };

  const resize = () => {
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    width = window.innerWidth;
    height = window.innerHeight;
    pointer.pixelX = Math.min(pointer.pixelX, width);
    pointer.pixelY = Math.min(pointer.pixelY, height);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    makeDust();
  };

  const rotate3D = (x, y, z, pitch, yaw, roll) => {
    const x1 = x * Math.cos(roll) - y * Math.sin(roll);
    const y1 = x * Math.sin(roll) + y * Math.cos(roll);
    const y2 = y1 * Math.cos(pitch) - z * Math.sin(pitch);
    const z2 = y1 * Math.sin(pitch) + z * Math.cos(pitch);
    const x3 = x1 * Math.cos(yaw) + z2 * Math.sin(yaw);
    const z3 = -x1 * Math.sin(yaw) + z2 * Math.cos(yaw);
    return { x: x3, y: y2, z: z3 };
  };

  const draw = () => {
    if (!isActive) {
      animationFrameId = null;
      return;
    }

    ctx.clearRect(0, 0, width, height);

    const isMobile = width < 768;
    pointer.x += (pointer.targetX - pointer.x) * 0.05;
    pointer.y += (pointer.targetY - pointer.y) * 0.05;

    const centerX = width / 2 + pointer.x * (isMobile ? 16 : 76);
    const centerY = height / 2 + pointer.y * (isMobile ? 11 : 50);
    const fov = isMobile ? width * 2.5 : 800;
    const totalWidth = width * 2.5;
    const startX = -totalWidth / 2;
    const helixRadius = isMobile
      ? Math.min(width, height) * 0.4
      : Math.min(width, height) * 0.28;
    const frequency = isMobile ? 0.009 : 0.007;
    const movementSpeed = 0.9;
    const numSegments = isMobile ? 38 : 84;
    const segmentSpacing = totalWidth / numSegments;
    const offsetX = (time * movementSpeed) % segmentSpacing;
    const pitch = 0.1 + Math.sin(time * 0.008) * 0.04 - pointer.y * 0.17;
    const yaw = -0.3 + pointer.x * 0.27;
    const barrelRoll = time * 0.0024 + pointer.x * 0.025;
    const baseNodeScale = isMobile ? 4.5 : 8.5;
    const rungLineWidth = isMobile ? 2 : 3;
    const backboneLineWidth = isMobile ? 2.5 : 4.5;
    const backboneHighlightWidth = isMobile ? 0.8 : 1.4;
    const elements = [];

    if (pointer.isPresent && !isMobile) {
      const pointerGlow = ctx.createRadialGradient(
        pointer.pixelX,
        pointer.pixelY,
        0,
        pointer.pixelX,
        pointer.pixelY,
        270
      );
      pointerGlow.addColorStop(0, 'rgba(34, 211, 238, 0.14)');
      pointerGlow.addColorStop(0.38, 'rgba(59, 130, 246, 0.055)');
      pointerGlow.addColorStop(1, 'rgba(34, 211, 238, 0)');
      ctx.fillStyle = pointerGlow;
      ctx.fillRect(0, 0, width, height);
    }

    for (let i = 0; i <= numSegments + 1; i += 1) {
      const cx = startX + i * segmentSpacing - offsetX;
      const phase = cx * frequency;
      const pointA = rotate3D(
        cx,
        Math.sin(phase) * helixRadius,
        Math.cos(phase) * helixRadius,
        pitch,
        yaw,
        barrelRoll
      );
      const pointB = rotate3D(
        cx,
        Math.sin(phase + Math.PI) * helixRadius,
        Math.cos(phase + Math.PI) * helixRadius,
        pitch,
        yaw,
        barrelRoll
      );
      const baseHue = 210 + Math.sin(cx * 0.003 + time * 0.012) * 50;

      elements.push({ type: 'sphere', point: pointA, size: baseNodeScale, hue: baseHue });
      elements.push({ type: 'sphere', point: pointB, size: baseNodeScale, hue: baseHue + 40 });

      if (i % 2 === 0) {
        elements.push({
          type: 'rung',
          pointA,
          pointB,
          z: (pointA.z + pointB.z) / 2,
          hue: baseHue + 20
        });
      }

      if (i > 0) {
        const previousX = startX + (i - 1) * segmentSpacing - offsetX;
        const previousPhase = previousX * frequency;
        const previousA = rotate3D(
          previousX,
          Math.sin(previousPhase) * helixRadius,
          Math.cos(previousPhase) * helixRadius,
          pitch,
          yaw,
          barrelRoll
        );
        const previousB = rotate3D(
          previousX,
          Math.sin(previousPhase + Math.PI) * helixRadius,
          Math.cos(previousPhase + Math.PI) * helixRadius,
          pitch,
          yaw,
          barrelRoll
        );

        elements.push({
          type: 'backbone',
          pointA: previousA,
          pointB: pointA,
          z: (previousA.z + pointA.z) / 2,
          hue: baseHue
        });
        elements.push({
          type: 'backbone',
          pointA: previousB,
          pointB,
          z: (previousB.z + pointB.z) / 2,
          hue: baseHue + 40
        });
      }
    }

    dust.forEach((particle) => {
      particle.x -= movementSpeed * 0.38;
      particle.y += particle.speedY;
      particle.x += Math.cos(time * 0.014 + particle.offset) * 0.9;

      if (particle.x < startX) {
        particle.x = startX + totalWidth;
        particle.y = Math.random() * 1000 - 500;
      }

      elements.push({
        type: 'dust',
        point: rotate3D(particle.x, particle.y, particle.z, pitch, yaw, barrelRoll),
        size: particle.size,
        hue: particle.hue
      });
    });

    elements.sort((a, b) => {
      const zA = a.point ? a.point.z : a.z;
      const zB = b.point ? b.point.z : b.z;
      return zB - zA;
    });

    const getAlpha = (z) => Math.max(0.1, 1 - Math.abs(z) / 1000);

    elements.forEach((element) => {
      if (element.type === 'sphere') {
        const scale = Math.min(fov / (fov + element.point.z), 2.5);
        if (scale <= 0) return;

        const x = centerX + element.point.x * scale;
        const y = centerY + element.point.y * scale;
        const distanceToPointer = Math.hypot(x - pointer.pixelX, y - pointer.pixelY);
        const proximity = pointer.isPresent
          ? Math.max(0, 1 - distanceToPointer / 270)
          : 0;
        const size = element.size * scale * (1 + proximity * 0.28);
        const alpha = getAlpha(element.point.z);

        ctx.beginPath();
        ctx.arc(x, y, size * 2.35, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${element.hue}, 90%, 60%, ${alpha * (0.17 + proximity * 0.18)})`;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        const gradient = ctx.createRadialGradient(
          x - size * 0.3,
          y - size * 0.3,
          0,
          x,
          y,
          size
        );
        gradient.addColorStop(0, `hsla(${element.hue}, 100%, 90%, ${alpha})`);
        gradient.addColorStop(0.6, `hsla(${element.hue}, 90%, 50%, ${alpha})`);
        gradient.addColorStop(1, `hsla(${element.hue}, 80%, 20%, ${alpha})`);
        ctx.fillStyle = gradient;
        ctx.fill();
        return;
      }

      if (element.type === 'rung' || element.type === 'backbone') {
        const scaleA = Math.min(fov / (fov + element.pointA.z), 2.5);
        const scaleB = Math.min(fov / (fov + element.pointB.z), 2.5);
        if (scaleA <= 0 || scaleB <= 0) return;

        const xA = centerX + element.pointA.x * scaleA;
        const yA = centerY + element.pointA.y * scaleA;
        const xB = centerX + element.pointB.x * scaleB;
        const yB = centerY + element.pointB.y * scaleB;
        const averageScale = (scaleA + scaleB) / 2;
        const alpha = getAlpha(element.z);

        ctx.beginPath();
        ctx.moveTo(xA, yA);
        ctx.lineTo(xB, yB);
        ctx.lineWidth = (
          element.type === 'backbone' ? backboneLineWidth : rungLineWidth
        ) * averageScale;
        ctx.strokeStyle = `hsla(${element.hue}, 80%, 42%, ${alpha * 0.8})`;
        ctx.lineCap = 'round';
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(xA, yA);
        ctx.lineTo(xB, yB);
        ctx.lineWidth = (
          element.type === 'backbone' ? backboneHighlightWidth : 0.8
        ) * averageScale;
        ctx.strokeStyle = `hsla(${element.hue}, 100%, 82%, ${alpha})`;
        ctx.stroke();
        return;
      }

      const scale = Math.min(fov / (fov + element.point.z), 2.5);
      if (scale <= 0) return;

      const x = centerX + element.point.x * scale;
      const y = centerY + element.point.y * scale;
      const distanceToPointer = Math.hypot(x - pointer.pixelX, y - pointer.pixelY);
      const proximity = pointer.isPresent && !isMobile
        ? Math.max(0, 1 - distanceToPointer / 175)
        : 0;

      if (proximity > 0) {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(pointer.pixelX, pointer.pixelY);
        ctx.lineWidth = 0.65;
        ctx.strokeStyle = `hsla(${element.hue}, 95%, 72%, ${proximity * 0.2})`;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.arc(
        x,
        y,
        element.size * scale * (1 + proximity * 1.15),
        0,
        Math.PI * 2
      );
      ctx.fillStyle = `hsla(${element.hue}, 80%, 70%, ${getAlpha(element.point.z) * 0.76})`;
      ctx.fill();
    });

    if (!reduceMotion.matches) time += 1;
    animationFrameId = reduceMotion.matches ? null : requestAnimationFrame(draw);
  };

  const updateVisibility = () => {
    const shouldBeActive = hero.getBoundingClientRect().bottom <= 1;
    if (shouldBeActive === isActive) return;

    isActive = shouldBeActive;
    background.classList.toggle('is-active', isActive);

    if (isActive && animationFrameId === null) {
      draw();
    } else if (!isActive && animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
  };

  const updatePointer = (event) => {
    pointer.pixelX = event.clientX;
    pointer.pixelY = event.clientY;
    pointer.targetX = (event.clientX / width - 0.5) * 2;
    pointer.targetY = (event.clientY / height - 0.5) * 2;
    pointer.isPresent = true;
  };

  const resetPointer = () => {
    pointer.targetX = 0;
    pointer.targetY = 0;
    pointer.isPresent = false;
  };

  window.addEventListener('resize', resize, { passive: true });
  window.addEventListener('scroll', updateVisibility, { passive: true });
  window.addEventListener('pointermove', updatePointer, { passive: true });
  document.documentElement.addEventListener('pointerleave', resetPointer);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    } else if (!document.hidden && isActive && animationFrameId === null) {
      draw();
    }
  });

  resize();
  updateVisibility();
});
