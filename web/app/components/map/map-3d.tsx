"use client";

import { Canvas, type ThreeEvent, useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

import type { MapColumn } from "@/lib/map-3d-view";
import { ARCHIPELAGOS, OUTLINE, project } from "@/lib/vietnam-geo";

/**
 * Cảnh 3D của màn Bản đồ (#314, FR-33): Việt Nam là mặt phẳng đùn từ viền geoBoundaries, Hoàng Sa và Trường Sa vẽ bằng
 * điểm đảo kèm nhãn, ba cột cao theo tỷ trọng. Kéo để xoay và nghiêng (OrbitControls, không lật xuống dưới mặt đất,
 * không kéo ngang). Trỏ hay chạm một cột thì báo lên `onSelect`; khung thông tin nằm ngoài canvas.
 *
 * Màu lấy từ token của `globals.css` (canvas WebGL không đọc biến CSS). File này chỉ được tải khi mở lối 3D.
 */

const LAND_DEPTH = 0.3;
/** Tâm nhìn lệch về phía nam một chút để Trường Sa không sát mép dưới. */
const TARGET = { x: 0.6, z: 1.2 };
const COLOR = {
  land: "#1c2a36",
  landEdge: "#2e4456",
  island: "#62d9ee",
  column: "#62d9ee",
  columnSelected: "#e6edf3",
  label: "#e6edf3",
  labelMuted: "#9fb0c2",
};

interface Map3DProps {
  columns: MapColumn[];
  selected: string | null;
  onSelect: (city: string) => void;
  /** Mất context WebGL sau khi đã vẽ: màn chuyển sang 2D. */
  onContextLost: () => void;
}

function Controls() {
  const { camera, gl } = useThree();
  const controls = useMemo(() => {
    const c = new OrbitControls(camera, gl.domElement);
    c.enablePan = false;
    c.enableDamping = true;
    c.minPolarAngle = 0.15;
    c.maxPolarAngle = Math.PI * 0.42;
    // Xoay ngang tối đa 60° mỗi phía: bắc luôn ở nửa trên, người xem không mất phương hướng.
    c.minAzimuthAngle = -Math.PI / 3;
    c.maxAzimuthAngle = Math.PI / 3;
    c.minDistance = 10;
    c.maxDistance = 45;
    c.target.set(TARGET.x, 0, TARGET.z);
    return c;
  }, [camera, gl]);
  useEffect(() => () => controls.dispose(), [controls]);
  useFrame(() => controls.update());
  return null;
}

/** Mặt đất: mỗi vòng viền là một Shape trong mặt XY (y = bắc), đùn lên rồi xoay nằm xuống mặt XZ. */
function Land() {
  const geometry = useMemo(() => {
    const shapes = OUTLINE.rings.map((ring) => {
      const shape = new THREE.Shape();
      ring.forEach(([lon, lat], i) => {
        const { x, z } = project({ lon, lat });
        if (i === 0) shape.moveTo(x, -z);
        else shape.lineTo(x, -z);
      });
      return shape;
    });
    return new THREE.ExtrudeGeometry(shapes, { depth: LAND_DEPTH, bevelEnabled: false });
  }, []);
  useEffect(() => () => geometry.dispose(), [geometry]);
  return (
    <mesh geometry={geometry} rotation={[-Math.PI / 2, 0, 0]}>
      <meshStandardMaterial color={COLOR.land} emissive={COLOR.landEdge} emissiveIntensity={0.35} />
    </mesh>
  );
}

/** Nhãn chữ là sprite từ canvas 2D: luôn quay về phía máy quay, không cần gói font. */
function Label({ text, position, color = COLOR.label, size = 1 }: {
  text: string;
  position: [number, number, number];
  color?: string;
  size?: number;
}) {
  const texture = useMemo(() => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const font = 48;
    canvas.width = 1024;
    canvas.height = 96;
    if (ctx) {
      ctx.font = `600 ${font}px "Be Vietnam Pro", system-ui, sans-serif`;
      ctx.fillStyle = color;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(text, canvas.width / 2, canvas.height / 2);
    }
    const t = new THREE.CanvasTexture(canvas);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }, [text, color]);
  useEffect(() => () => texture.dispose(), [texture]);
  return (
    <sprite position={position} scale={[10.6 * size, 1 * size, 1]}>
      <spriteMaterial map={texture} transparent depthWrite={false} />
    </sprite>
  );
}

function Archipelagos() {
  return (
    <>
      {ARCHIPELAGOS.map((group) => {
        const at = project(group.labelAt);
        return (
          <group key={group.id}>
            {group.islands.map((island) => {
              const { x, z } = project(island);
              return (
                <mesh key={island.name} position={[x, 0.08, z]}>
                  <cylinderGeometry args={[0.12, 0.12, 0.16, 12]} />
                  <meshStandardMaterial color={COLOR.island} emissive={COLOR.island} emissiveIntensity={0.4} />
                </mesh>
              );
            })}
            <Label text={group.label} position={[at.x, 0.9, at.z]} color={COLOR.labelMuted} size={0.75} />
          </group>
        );
      })}
    </>
  );
}

function Column({ column, selected, onSelect }: { column: MapColumn; selected: boolean; onSelect: (city: string) => void }) {
  const height = Math.max(column.height, 0.02);
  const pick = (event: ThreeEvent<PointerEvent | MouseEvent>) => {
    event.stopPropagation();
    onSelect(column.city);
  };
  const color = selected ? COLOR.columnSelected : COLOR.column;
  return (
    <group position={[column.position.x, LAND_DEPTH, column.position.z]}>
      <mesh position={[0, height / 2, 0]} onPointerOver={pick} onClick={pick}>
        <cylinderGeometry args={[0.38, 0.38, height, 24]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={selected ? 0.5 : 0.25}
          transparent={column.faded}
          opacity={column.faded ? 0.4 : 1}
        />
      </mesh>
      <Label text={column.label} position={[0, height + 0.8, 0]} size={0.8} />
    </group>
  );
}

export default function Map3D({ columns, selected, onSelect, onContextLost }: Map3DProps) {
  const lostRef = useRef(onContextLost);
  useEffect(() => {
    lostRef.current = onContextLost;
  }, [onContextLost]);
  return (
    <Canvas
      dpr={[1, 2]}
      camera={{ position: [TARGET.x, 23, TARGET.z + 19], fov: 40, near: 0.1, far: 200 }}
      onCreated={({ gl }) => {
        gl.domElement.addEventListener("webglcontextlost", () => lostRef.current(), { once: true });
      }}
      aria-hidden="true"
    >
      <ambientLight intensity={0.7} />
      <directionalLight position={[8, 20, 10]} intensity={1.1} />
      <Land />
      <Archipelagos />
      {columns.map((column) => (
        <Column key={column.city} column={column} selected={selected === column.city} onSelect={onSelect} />
      ))}
      <Controls />
    </Canvas>
  );
}
