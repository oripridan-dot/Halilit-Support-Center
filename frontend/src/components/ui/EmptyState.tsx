import React from "react";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

/**
 * EmptyState — used when a view has no content to display.
 * Provides a visual placeholder with an optional call-to-action.
 */
export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
}) => (
  <div className="flex flex-col items-center justify-center py-20 px-6 text-center animate-fade-in">
    {icon && <div className="text-zinc-600 mb-4">{icon}</div>}
    <h3 className="text-lg font-semibold text-zinc-300 mb-2">{title}</h3>
    <p className="text-sm text-zinc-500 max-w-md mb-6">{description}</p>
    {action && (
      <button
        onClick={action.onClick}
        className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium 
                   rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50
                   hover:shadow-lg hover:shadow-blue-500/20 active:scale-[0.98]"
      >
        {action.label}
      </button>
    )}
  </div>
);

/**
 * ErrorState — shown when data loading fails.
 * Displays the error message and an optional retry button.
 */
export const ErrorState: React.FC<{
  error: Error | string;
  onRetry?: () => void;
}> = ({ error, onRetry }) => (
  <EmptyState
    icon={
      <svg
        className="w-16 h-16"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
        />
      </svg>
    }
    title="Something went wrong"
    description={
      typeof error === "string"
        ? error
        : error.message || "An unexpected error occurred while loading data."
    }
    action={onRetry ? { label: "Try Again", onClick: onRetry } : undefined}
  />
);
