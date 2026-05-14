"use client";

import { useRef, useEffect, useMemo } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Sphere, Stars } from "@react-three/drei";
import * as THREE from "three";

// Fraud event particles on globe surface
function FraudEvents({ count = 40 }: { count?: number }) {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  const positions = useMemo(() => {
    return Array.from({ length: count }, () => {
      const phi = Math.acos(2 * Math.random() - 1);
      const theta = Math.random() * Math.PI * 2;
      const r = 1.02;
      return {
        x: r * Math.sin(phi) * Math.cos(theta),
        y: r * Math.sin(phi) * Math.sin(theta),
        z: r * Math.cos(phi),
        isFraud: Math.random() < 0.15,
        scale: Math.random() * 0.02 + 0.008,
        phase: Math.random() * Math.PI * 2,
      };
    });
  }, [count]);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const t = clock.getElapsedTime();
    positions.forEach((pos, i) => {
      const pulse = 1 + 0.3 * Math.sin(t * 2 + pos.phase);
      dummy.position.set(pos.x, pos.y, pos.z);
      dummy.scale.setScalar(pos.scale * pulse);
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
      <sphereGeometry args={[1, 6, 6]} />
      <meshBasicMaterial color="#FF2D55" />
    </instancedMesh>
  );
}

// Animated globe with wireframe + glow
function GlobeCore() {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = clock.getElapsedTime() * 0.08;
    }
    if (glowRef.current) {
      const pulse = 0.95 + 0.05 * Math.sin(clock.getElapsedTime() * 1.5);
      glowRef.current.scale.setScalar(pulse);
    }
  });

  return (
    <group>
      {/* Core sphere */}
      <mesh ref={meshRef}>
        <sphereGeometry args={[1, 64, 64]} />
        <meshPhongMaterial
          color="#050813"
          emissive="#00F5FF"
          emissiveIntensity={0.02}
          wireframe={false}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Wireframe overlay */}
      <mesh ref={meshRef}>
        <sphereGeometry args={[1.001, 24, 24]} />
        <meshBasicMaterial
          color="#00F5FF"
          wireframe
          transparent
          opacity={0.06}
        />
      </mesh>

      {/* Glow sphere */}
      <mesh ref={glowRef}>
        <sphereGeometry args={[1.08, 32, 32]} />
        <meshBasicMaterial
          color="#00F5FF"
          transparent
          opacity={0.04}
          side={THREE.BackSide}
        />
      </mesh>

      {/* Equatorial ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[1.05, 0.003, 8, 128]} />
        <meshBasicMaterial color="#00F5FF" transparent opacity={0.3} />
      </mesh>

      <FraudEvents count={50} />
    </group>
  );
}

export default function CyberGlobe() {
  return (
    <Canvas
      camera={{ position: [0, 0, 2.8], fov: 45 }}
      style={{ background: "transparent" }}
      gl={{ antialias: true, alpha: true }}
    >
      <ambientLight intensity={0.3} />
      <pointLight position={[5, 5, 5]} intensity={0.8} color="#00F5FF" />
      <pointLight position={[-5, -5, -5]} intensity={0.4} color="#7C3AED" />

      <Stars
        radius={10}
        depth={20}
        count={800}
        factor={0.4}
        saturation={0}
        fade
        speed={0.5}
      />

      <GlobeCore />

      <OrbitControls
        enablePan={false}
        enableZoom={false}
        autoRotate
        autoRotateSpeed={0.4}
        minPolarAngle={Math.PI / 4}
        maxPolarAngle={(3 * Math.PI) / 4}
      />
    </Canvas>
  );
}
