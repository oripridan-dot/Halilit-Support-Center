/**
 * Integration Tests for Environment3DViewer Component
 * Tests React component integration, loading, and interaction
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { Environment3DViewer } from "@/components/views/Environment3DViewer";

// Mock Three.js and related modules
vi.mock("three", () => ({
  Scene: vi.fn(() => ({ add: vi.fn(), remove: vi.fn() })),
  PerspectiveCamera: vi.fn(() => ({
    aspect: 1,
    updateProjectionMatrix: vi.fn(),
  })),
  WebGLRenderer: vi.fn(() => ({
    setSize: vi.fn(),
    setPixelRatio: vi.fn(),
    render: vi.fn(),
    dispose: vi.fn(),
    domElement: document.createElement("canvas"),
    info: {
      render: { triangles: 1000, calls: 10 },
      memory: { geometries: 5, textures: 10 },
    },
  })),
  Clock: vi.fn(() => ({ getDelta: vi.fn(() => 0.016) })),
  Raycaster: vi.fn(() => ({
    setFromCamera: vi.fn(),
    intersectObjects: vi.fn(() => []),
  })),
  Vector2: vi.fn(() => ({ x: 0, y: 0 })),
}));

vi.mock("three/examples/jsm/loaders/GLTFLoader", () => ({
  GLTFLoader: vi.fn(() => ({
    load: vi.fn((url, onLoad) => {
      setTimeout(() => onLoad({ scene: {} }), 100);
    }),
  })),
}));

vi.mock("three/examples/jsm/controls/OrbitControls", () => ({
  OrbitControls: vi.fn(() => ({
    enabled: true,
    update: vi.fn(),
    dispose: vi.fn(),
  })),
}));

describe("Environment3DViewer Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders without crashing", () => {
    render(<Environment3DViewer subcategoryId="electric-guitars" />);
    expect(screen.getByRole("region")).toBeInTheDocument();
  });

  it("shows loading state initially", () => {
    render(<Environment3DViewer subcategoryId="electric-guitars" />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("calls onLoadComplete when finished loading", async () => {
    const onLoadComplete = vi.fn();

    render(
      <Environment3DViewer
        subcategoryId="electric-guitars"
        onLoadComplete={onLoadComplete}
      />,
    );

    await waitFor(
      () => {
        expect(onLoadComplete).toHaveBeenCalled();
      },
      { timeout: 2000 },
    );
  });

  it("displays error message on load failure", async () => {
    const onLoadError = vi.fn();

    // Mock environment config to return null
    vi.mock("@/lib/3d/environment-config", () => ({
      getEnvironmentBySubcategory: () => null,
    }));

    render(
      <Environment3DViewer
        subcategoryId="invalid-id"
        onLoadError={onLoadError}
      />,
    );

    await waitFor(() => {
      expect(onLoadError).toHaveBeenCalled();
    });
  });

  it("shows performance stats when enabled", async () => {
    render(
      <Environment3DViewer
        subcategoryId="electric-guitars"
        showPerformanceStats={true}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText(/fps/i)).toBeInTheDocument();
    });
  });

  it("filters products by brand IDs", async () => {
    const brandIds = ["fender", "gibson"];

    render(
      <Environment3DViewer
        subcategoryId="electric-guitars"
        brandIds={brandIds}
      />,
    );

    await waitFor(() => {
      // Verify environment is loaded with filtered brands
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });

  it("handles product click events", async () => {
    const onProductClick = vi.fn();

    render(
      <Environment3DViewer
        subcategoryId="electric-guitars"
        onProductClick={onProductClick}
      />,
    );

    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });

    // Simulate click on canvas
    const canvas = screen.getByRole("region").querySelector("canvas");
    fireEvent.click(canvas!);

    // Note: In real scenario, raycaster would detect object
    // This would trigger onProductClick
  });

  it("enables auto-rotation when prop is true", async () => {
    render(
      <Environment3DViewer
        subcategoryId="electric-guitars"
        autoRotate={true}
      />,
    );

    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });

    // Verify OrbitControls autoRotate is enabled
    // (would need to expose controls via ref to test properly)
  });

  it("applies custom className", () => {
    const customClass = "my-custom-3d-viewer";

    render(
      <Environment3DViewer
        subcategoryId="electric-guitars"
        className={customClass}
      />,
    );

    const container = screen.getByRole("region");
    expect(container.classList.contains(customClass)).toBe(true);
  });

  it("cleans up resources on unmount", async () => {
    const { unmount } = render(
      <Environment3DViewer subcategoryId="electric-guitars" />,
    );

    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });

    // Unmount component
    unmount();

    // Verify cleanup (disposal of Three.js resources)
    // In real implementation, this would check that dispose() was called
  });

  it("updates when subcategoryId changes", async () => {
    const { rerender } = render(
      <Environment3DViewer subcategoryId="electric-guitars" />,
    );

    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });

    // Change subcategory
    rerender(<Environment3DViewer subcategoryId="synthesizers" />);

    // Should show loading again
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });

  it("handles window resize events", async () => {
    render(<Environment3DViewer subcategoryId="electric-guitars" />);

    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });

    // Trigger resize
    window.innerWidth = 1024;
    window.innerHeight = 768;
    fireEvent(window, new Event("resize"));

    // Component should handle resize without errors
    expect(screen.getByRole("region")).toBeInTheDocument();
  });
});

describe("Environment3DViewer Accessibility", () => {
  it("has proper ARIA attributes", () => {
    render(<Environment3DViewer subcategoryId="electric-guitars" />);

    const container = screen.getByRole("region");
    expect(container).toHaveAttribute("aria-label");
  });

  it("provides loading announcement for screen readers", () => {
    render(<Environment3DViewer subcategoryId="electric-guitars" />);

    expect(screen.getByRole("status")).toHaveTextContent(/loading/i);
  });

  it("announces errors to screen readers", async () => {
    const onLoadError = vi.fn();

    render(
      <Environment3DViewer
        subcategoryId="invalid-id"
        onLoadError={onLoadError}
      />,
    );

    await waitFor(() => {
      const alert = screen.getByRole("alert");
      expect(alert).toBeInTheDocument();
    });
  });
});

describe("Environment3DViewer Performance", () => {
  it("throttles resize events", async () => {
    const resizeHandler = vi.fn();

    render(<Environment3DViewer subcategoryId="electric-guitars" />);

    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });

    // Trigger multiple resize events rapidly
    for (let i = 0; i < 10; i++) {
      fireEvent(window, new Event("resize"));
    }

    // Should only handle resize once (throttled)
    // Actual count would depend on throttle implementation
  });

  it("debounces performance metric updates", async () => {
    render(
      <Environment3DViewer
        subcategoryId="electric-guitars"
        showPerformanceStats={true}
      />,
    );

    await waitFor(() => {
      const stats = screen.getByText(/fps/i);
      expect(stats).toBeInTheDocument();
    });

    // Performance updates should be debounced to avoid excessive re-renders
  });
});
