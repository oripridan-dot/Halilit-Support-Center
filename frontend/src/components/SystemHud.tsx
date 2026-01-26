import { Activity, Database } from "lucide-react";
import { useEffect, useState } from "react";

interface SystemManifest {
  system_status: string;
  last_update: string;
  total_products: number;
  motd: string;
}

export const SystemHud = () => {
  const [manifest, setManifest] = useState<SystemManifest | null>(null);

  useEffect(() => {
    fetch("/data/system_manifest.json")
      .then((res) => res.json())
      .then(setManifest)
      .catch(() => {});
  }, []);

  if (!manifest) return null;

  const lastUpdate = new Date(manifest.last_update);
  const hoursAgo = Math.floor(
    (new Date().getTime() - lastUpdate.getTime()) / (1000 * 60 * 60),
  );
  const timeDisplay = hoursAgo === 0 ? "JUST NOW" : `${hoursAgo}H AGO`;

  return (
    <div className="fixed bottom-0 w-full bg-black/90 border-t border-zinc-800 backdrop-blur-md py-1 px-4 z-50 flex justify-between items-center text-[10px] font-mono tracking-widest text-zinc-500">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-emerald-500">
          <Activity className="w-3 h-3 animate-pulse" />
          <span>SYSTEM {manifest.system_status}</span>
        </div>
        <span className="hidden md:inline">|</span>
        <div className="hidden md:flex items-center gap-2">
          <span>SYNC:</span>
          <span className="text-zinc-300">{timeDisplay}</span>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Database className="w-3 h-3" />
          <span className="text-zinc-300">
            {manifest.total_products.toLocaleString()} SKUs
          </span>
        </div>
      </div>
    </div>
  );
};
