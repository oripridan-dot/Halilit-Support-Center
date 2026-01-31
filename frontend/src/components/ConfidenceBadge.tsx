import React from "react";
import {
  Check,
  AlertCircle,
  Zap,
  Star,
  Shield,
  Flame,
  TrendingUp,
} from "lucide-react";

interface ConfidenceBadgeProps {
  score?: number;
  badges?: string[];
  sourcesOfTruth?: Array<{ name: string; type: string; verified?: boolean }>;
  className?: string;
  showDetailed?: boolean;
}

/**
 * ConfidenceBadge Component
 * Displays the trust/verification status with visual confidence indicators
 * and source attribution
 */
export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  score = 0,
  badges = [],
  sourcesOfTruth = [],
  className = "",
  showDetailed = false,
}) => {
  const getBadgeConfig = (badge: string) => {
    const configs: Record<
      string,
      {
        icon: React.ReactNode;
        color: string;
        label: string;
        description: string;
      }
    > = {
      DIAMOND: {
        icon: <Flame className="w-4 h-4" />,
        color: "bg-blue-50 border-blue-200 text-blue-700",
        label: "Diamond Verified",
        description: "Complete official + commercial + verified reviews",
      },
      GOLD: {
        icon: <Star className="w-4 h-4" />,
        color: "bg-amber-50 border-amber-200 text-amber-700",
        label: "Gold Verified",
        description: "Most data verified from manufacturer",
      },
      SILVER: {
        icon: <Shield className="w-4 h-4" />,
        color: "bg-slate-50 border-slate-200 text-slate-700",
        label: "Silver Verified",
        description: "Partial verification available",
      },
      "Community Verified": {
        icon: <Check className="w-4 h-4" />,
        color: "bg-green-50 border-green-200 text-green-700",
        label: "Community Verified",
        description: "Verified by community experts",
      },
      "Community Unverified": {
        icon: <AlertCircle className="w-4 h-4" />,
        color: "bg-orange-50 border-orange-200 text-orange-700",
        label: "Unverified",
        description: "Pending community validation",
      },
    };
    return configs[badge] || null;
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 85) return "from-blue-600 to-blue-500";
    if (score >= 70) return "from-green-600 to-emerald-500";
    if (score >= 50) return "from-amber-600 to-yellow-500";
    return "from-orange-600 to-red-500";
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 85) return "Excellent";
    if (score >= 70) return "Good";
    if (score >= 50) return "Fair";
    return "Limited";
  };

  if (!showDetailed && badges.length === 0 && score === 0) {
    return null;
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Confidence Score */}
      {score > 0 && (
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-slate-600" />
              <span className="text-sm font-medium text-slate-700">
                Data Confidence
              </span>
            </div>
            <span className="text-sm font-bold text-slate-900">{score}%</span>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full bg-gradient-to-r ${getConfidenceColor(score)} rounded-full transition-all duration-300`}
              style={{ width: `${score}%` }}
            />
          </div>

          <p className="text-xs text-slate-500 mt-2">
            {getConfidenceLabel(score)} data quality across all sources
          </p>
        </div>
      )}

      {/* Verification Badges */}
      {badges.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
            Verification Status
          </p>
          <div className="flex flex-wrap gap-2">
            {badges.map((badge, idx) => {
              const config = getBadgeConfig(badge);
              if (!config) return null;
              return (
                <div
                  key={idx}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-medium ${config.color}`}
                  title={config.description}
                >
                  {config.icon}
                  <span>{config.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Sources of Truth */}
      {sourcesOfTruth.length > 0 && (
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3">
          <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            Sources of Truth
          </p>
          <ul className="space-y-1">
            {sourcesOfTruth.map((source, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs">
                <Check className="w-3 h-3 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="font-medium text-slate-900">
                    {source.name}
                  </span>
                  {source.verified && (
                    <span className="ml-1 inline-block px-1.5 py-0.5 bg-green-100 text-green-700 rounded text-[10px] font-semibold">
                      Verified
                    </span>
                  )}
                  <p className="text-slate-500">{source.type}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ConfidenceBadge;
