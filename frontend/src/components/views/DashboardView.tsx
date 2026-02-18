/**
 * Dashboard View (Operator Console) — Overview / Galaxy dashboard.
 * Reuses GalaxyDashboard for category browser and quick navigation.
 */
import React from "react";
import { GalaxyDashboard } from "./GalaxyDashboard";

export const DashboardView: React.FC = () => {
  return <GalaxyDashboard />;
};

export default DashboardView;
