import { motion } from "framer-motion";
import { useState } from "react";

export interface SlotScene {
  themeColors: [string, string];
  sceneType: "STAGE" | "STUDIO" | "WALL" | "BOOTH" | "VOID";
  vibe: string;
  floorMat: string;
  bgMat: string;
}

interface CategorySlotProps {
  id: string;
  name: string;
  image: string;
  scene: SlotScene;
  onClick: () => void;
}

export const CategorySlot = ({ id, name, image, scene, onClick }: CategorySlotProps) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="flex flex-col w-full">
    <motion.div
      className="relative aspect-square rounded-xl bg-[#020202] border border-white/5 overflow-hidden group cursor-pointer w-full shadow-2xl"
      style={{ perspective: "800px" }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      {/* -----------------------------------------------------------
          ROOM GEOMETRY (3D Stage)
          ----------------------------------------------------------- */}
      
      {/* Back Wall - Deep Plane */}
      <div 
        className="absolute inset-x-0 top-0 h-[72%] z-0 transition-all duration-700" 
        style={{ 
          background: scene.bgMat,
          boxShadow: "inset 0 -40px 60px -10px #000000"
        }} 
      />

      {/* Side Wall - Left */}
      <div 
        className="absolute left-0 top-0 w-[12%] h-[72%] z-1 transition-all duration-700"
        style={{
          background: "linear-gradient(90deg, #000000 0%, rgba(0,0,0,0.3) 100%)",
          boxShadow: "inset 3px 0 12px rgba(0,0,0,0.9)"
        }}
      />

      {/* Side Wall - Right */}
      <div 
        className="absolute right-0 top-0 w-[12%] h-[72%] z-1 transition-all duration-700"
        style={{
          background: "linear-gradient(270deg, #000000 0%, rgba(0,0,0,0.3) 100%)",
          boxShadow: "inset -3px 0 12px rgba(0,0,0,0.9)"
        }}
      />

      {/* Stage Floor - Geometric Perspective Plane */}
      <div 
        className="absolute bottom-0 inset-x-[-15%] h-[42%] z-10 origin-bottom transition-transform duration-700"
        style={{ 
            background: "#000000",
            transform: isHovered 
              ? "rotateX(58deg) translateY(2%) scaleY(0.95)" 
              : "rotateX(55deg) translateY(5%) scaleY(1.0)",
            transformStyle: "preserve-3d",
            boxShadow: "inset 0 0 20px rgba(0,0,0,0.9)"
        }} 
      >
        {/* Floor Material - Base */}
        <div className="absolute inset-0 opacity-60" style={{ background: scene.floorMat }} />
        
        {/* Floor Grid - Enhanced */}
        <div className="absolute inset-0 opacity-[0.18] bg-[linear-gradient(to_right,#444_1px,transparent_1px),linear-gradient(to_bottom,#444_1px,transparent_1px)] bg-[size:40px_40px]" />

        {/* Floor edge highlight */}
        <div className="absolute bottom-0 inset-x-0 h-[4px] bg-gradient-to-b from-black/50 to-transparent" />

        {/* Floor shadow edge */}
        <div className="absolute top-0 inset-x-0 h-[3px] bg-gradient-to-b from-black/90 to-transparent" />
      </div>

      {/* Horizon Line / Wall-Floor Seam - REMOVED */}

      {/* Ambient Depth Vignette - Enhanced */}
      <div className="absolute inset-0 z-10 bg-[radial-gradient(circle_at_center,transparent_0%,#000000_80%)] opacity-75 pointer-events-none" />
      
      {/* Additional Side Shadow for Depth */}
      <div className="absolute inset-0 z-12 bg-[linear-gradient(90deg,#00000050_0%,transparent_15%,transparent_85%,#00000050_100%)] pointer-events-none" />

      {/* Stage Fog/Haze - Light Medium */}
      <div className="absolute inset-0 z-18 transition-opacity duration-700" style={{
        background: "radial-gradient(ellipse at 50% 40%, rgba(30,30,30,0.02) 0%, transparent 50%)",
        opacity: isHovered ? 0.1 : 0.02
      }} />

      {/* -----------------------------------------------------------
          LIGHTING RIG - "GOD'S BEAMS" FROM ABOVE
          Sharp, distinct beams - no intentional color blending
          ----------------------------------------------------------- */}
      
      {/* Volumetric Stage Beams (Behind Product) */}
      <div className="absolute inset-0 z-20 pointer-events-none overflow-hidden mix-blend-screen">
          
          {/* PRIMARY BEAM 1 - Brand Color 0 (Left from upper left) */}
          <div 
             className="absolute top-[-25%] left-[8%] w-[200%] h-[280%] transition-all duration-700 ease-out origin-top-left pointer-events-none"
             style={{ 
                 background: `linear-gradient(
                    175deg,
                    ${scene.themeColors[0]}100 0%,
                    ${scene.themeColors[0]}98 1%,
                    ${scene.themeColors[0]}85 4%,
                    ${scene.themeColors[0]}60 12%,
                    ${scene.themeColors[0]}30 32%,
                    transparent 52%
                  ),
                  conic-gradient(
                    from 175deg at 0% 0%,
                    transparent -2deg,
                    ${scene.themeColors[0]}100 2deg,
                    ${scene.themeColors[0]}95 5deg,
                    ${scene.themeColors[0]}60 11deg,
                    transparent 18deg
                  )`,
                 opacity: isHovered ? 0.95 : 0.55,
                 transform: `translateX(5px) ${isHovered ? 'scaleY(1.25)' : 'scaleY(1.0)'}`,
                 filter: isHovered ? `blur(0.8px) drop-shadow(0 0 35px ${scene.themeColors[0]})` : 'blur(1.2px)',
             }}
          />

          {/* PRIMARY BEAM 2 - Brand Color 1 (Right from upper right) */}
          <div 
             className="absolute top-[-25%] right-[8%] w-[200%] h-[280%] transition-all duration-700 ease-out origin-top-right scale-x-[-1] pointer-events-none"
             style={{ 
                 background: `linear-gradient(
                    175deg,
                    ${scene.themeColors[1]}100 0%,
                    ${scene.themeColors[1]}98 1%,
                    ${scene.themeColors[1]}85 4%,
                    ${scene.themeColors[1]}60 12%,
                    ${scene.themeColors[1]}30 32%,
                    transparent 52%
                  ),
                  conic-gradient(
                    from 175deg at 0% 0%,
                    transparent -2deg,
                    ${scene.themeColors[1]}100 2deg,
                    ${scene.themeColors[1]}95 5deg,
                    ${scene.themeColors[1]}60 11deg,
                    transparent 18deg
                  )`,
                 opacity: isHovered ? 0.95 : 0.55,
                 transform: `translateX(5px) ${isHovered ? 'scaleY(1.25)' : 'scaleY(1.0)'}`,
                 filter: isHovered ? `blur(0.8px) drop-shadow(0 0 35px ${scene.themeColors[1]})` : 'blur(1.2px)',
             }}
          />

          {/* Left Beam Glow - SHARP */}
          <div 
             className="absolute top-0 left-[18%] w-[60%] h-[120%] rounded-full transition-all duration-700 ease-out pointer-events-none"
             style={{ 
                 background: `radial-gradient(ellipse 70% 140% at 50% 0%, ${scene.themeColors[0]}60 0%, ${scene.themeColors[0]}25 20%, ${scene.themeColors[0]}5 50%, transparent 80%)`,
                 opacity: isHovered ? 0.35 : 0.08,
                 filter: 'blur(8px)',
             }}
          />

          {/* Right Beam Glow - SHARP */}
          <div 
             className="absolute top-0 right-[18%] w-[60%] h-[120%] rounded-full transition-all duration-700 ease-out pointer-events-none"
             style={{ 
                 background: `radial-gradient(ellipse 70% 140% at 50% 0%, ${scene.themeColors[1]}60 0%, ${scene.themeColors[1]}25 20%, ${scene.themeColors[1]}5 50%, transparent 80%)`,
                 opacity: isHovered ? 0.35 : 0.08,
                 filter: 'blur(8px)',
             }}
          />

          {/* Floor Spot - Left (Brand Color 0 only) */}
          <div 
              className="absolute bottom-[24%] left-[23%] w-[20%] h-[6%] rounded-[100%] transition-all duration-700 pointer-events-none"
              style={{ 
                background: `radial-gradient(ellipse 100% 50% at 50% 30%, ${scene.themeColors[0]}, transparent)`, 
                boxShadow: `0 0 15px 4px ${scene.themeColors[0]}`, 
                opacity: isHovered ? 0.25 : 0.06,
                transform: isHovered ? 'scale(1.3)' : 'scale(1)',
                filter: 'blur(0.5px)'
              }}
          />

          {/* Floor Spot - Right (Brand Color 1 only) */}
          <div 
              className="absolute bottom-[24%] right-[23%] w-[20%] h-[6%] rounded-[100%] transition-all duration-700 pointer-events-none"
              style={{ 
                background: `radial-gradient(ellipse 100% 50% at 50% 30%, ${scene.themeColors[1]}, transparent)`, 
                boxShadow: `0 0 15px 4px ${scene.themeColors[1]}`, 
                opacity: isHovered ? 0.25 : 0.06,
                transform: isHovered ? 'scale(1.3)' : 'scale(1)',
                filter: 'blur(0.5px)'
              }}
          />

      </div>

      {/* -----------------------------------------------------------
          CONTENT (Flagship Product)
          ----------------------------------------------------------- */}
          
      {/* Layer 4: Object (The Product) */}
      <div className="absolute inset-0 z-30 flex items-center justify-center p-8 pb-10 perspective-[1000px]">
        <motion.img 
          src={image}
          alt={name}
          className="w-full h-full object-contain drop-shadow-[0_4px_8px_rgba(0,0,0,0.8)] will-change-transform"
          animate={
            isHovered 
              ? { y: -10, scale: 1.15, rotateX: 5 } 
              : { y: 0, scale: 1, rotateX: 0 }
          }
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          style={{
            filter: isHovered 
              ? `drop-shadow(0 15px 30px ${scene.themeColors[0]}40) brightness(1.1)` 
              : "drop-shadow(0 4px 10px rgba(0,0,0,0.8)) brightness(0.9)"
          }}
          onError={(e) => { e.currentTarget.style.display = 'none'; }}
        />
      </div>

      {/* Border Glow on Hover */}
      <div 
        className="absolute inset-0 rounded-xl border border-transparent transition-all duration-500 z-50 pointer-events-none"
        style={{ 
          borderColor: isHovered ? `${scene.themeColors[0]}30` : 'transparent',
          boxShadow: isHovered ? `inset 0 0 20px ${scene.themeColors[0]}10` : 'none'
        }}
      />

    </motion.div>

    {/* Title Label - Below Slot */}
    <div className="w-full text-center py-2 px-2 group">
      <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-400 group-hover:text-white transition-colors duration-300 leading-tight">
        {name}
      </h3>
    </div>
    </div>
  );
};
