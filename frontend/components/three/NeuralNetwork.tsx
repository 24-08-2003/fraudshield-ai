"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

interface NeuralNetworkProps {
  layers?: number[];
}

function NeuralNodes({ layers }: { layers: number[] }) {
  const linesRef = useRef<THREE.LineSegments>(null);

  const { nodes, edges } = useMemo(() => {
    const allNodes: THREE.Vector3[] = [];
    const layerIndices: number[][] = [];

    layers.forEach((count, layerIdx) => {
      const indices: number[] = [];
      const xOffset = (layerIdx - (layers.length - 1) / 2) * 1.2;

      for (let i = 0; i < count; i++) {
        const y = (i - (count - 1) / 2) * 0.5;
        allNodes.push(new THREE.Vector3(xOffset, y, 0));
        indices.push(allNodes.length - 1);
      }
      layerIndices.push(indices);
    });

    // Build edges between adjacent layers
    const edgePositions: number[] = [];
    for (let l = 0; l < layerIndices.length - 1; l++) {
      for (const fromIdx of layerIndices[l]) {
        for (const toIdx of layerIndices[l + 1]) {
          const from = allNodes[fromIdx];
          const to = allNodes[toIdx];
          edgePositions.push(from.x, from.y, from.z, to.x, to.y, to.z);
        }
      }
    }

    return { nodes: allNodes, edges: edgePositions, layerIndices };
  }, [layers]);

  const lineGeometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.Float32BufferAttribute(edges, 3));
    return geo;
  }, [edges]);

  useFrame(({ clock }) => {
    if (linesRef.current) {
      const mat = linesRef.current.material as THREE.LineBasicMaterial;
      mat.opacity = 0.1 + 0.05 * Math.sin(clock.getElapsedTime() * 2);
    }
  });

  return (
    <>
      {/* Edges */}
      <lineSegments ref={linesRef} geometry={lineGeometry}>
        <lineBasicMaterial
          color="#00F5FF"
          transparent
          opacity={0.12}
        />
      </lineSegments>

      {/* Nodes */}
      {nodes.map((pos, i) => (
        <mesh key={i} position={pos}>
          <sphereGeometry args={[0.06, 8, 8]} />
          <meshBasicMaterial
            color={i < layers[0] ? "#7C3AED" : i >= nodes.length - layers[layers.length - 1] ? "#FF2D55" : "#00F5FF"}
          />
        </mesh>
      ))}
    </>
  );
}

export default function NeuralNetwork({ layers = [4, 6, 6, 4, 1] }: NeuralNetworkProps) {
  return (
    <NeuralNodes layers={layers} />
  );
}
