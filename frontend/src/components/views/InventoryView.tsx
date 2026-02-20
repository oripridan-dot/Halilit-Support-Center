import React, { useState, useEffect } from "react";
import { useDebounceThrottle } from "../../hooks/useDebounceThrottle";
import { useNavigationStore } from "../../store/navigationStore";
import { Loader2 } from "lucide-react";

interface InventoryItem {
  id: string;
  name: string;
  sku: string;
  description: string;
  price: number;
  // ... other inventory item properties
}

interface InventoryViewProps {
  // Define any props if needed
}

const InventoryView: React.FC<InventoryViewProps> = () => {
  const [filterText, setFilterText] = useState("");
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { searchQuery: initialCfpFilter, setSearchQuery } =
    useNavigationStore();
  const debouncedSetFilterText = useDebounceThrottle(
    (value: string) => {
      setFilterText(value);
    },
    150,
    0,
  );

  useEffect(() => {
    if (initialCfpFilter) {
      debouncedSetFilterText(initialCfpFilter);
    }
  }, [initialCfpFilter, debouncedSetFilterText]);

  useEffect(() => {
    const fetchInventory = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Simulate API call with a delay
        await new Promise((resolve) => setTimeout(resolve, 500));
        // Replace with actual API call
        const searchTerm = filterText.toLowerCase();
        const mockInventory: InventoryItem[] = [
          {
            id: "1",
            name: "Fender Stratocaster",
            sku: "FS001",
            description: "Electric guitar",
            price: 1000,
          },
          {
            id: "2",
            name: "Gibson Les Paul",
            sku: "GLP001",
            description: "Electric guitar",
            price: 1200,
          },
          {
            id: "3",
            name: "Roland Juno-106",
            sku: "RJ001",
            description: "Synthesizer",
            price: 800,
          },
          {
            id: "4",
            name: "Yamaha P-125",
            sku: "YP001",
            description: "Digital Piano",
            price: 600,
          },
          {
            id: "5",
            name: "Fender Precision Bass",
            sku: "FPB001",
            description: "Bass Guitar",
            price: 900,
          },
        ];
        const filteredInventory = mockInventory.filter(
          (item) =>
            item.name.toLowerCase().includes(searchTerm) ||
            item.sku.toLowerCase().includes(searchTerm) ||
            item.description.toLowerCase().includes(searchTerm),
        );
        setInventory(filteredInventory);

        if (initialCfpFilter && !filterText) {
          setFilterText(initialCfpFilter);
          setSearchQuery(initialCfpFilter);
        }
      } catch (err: any) {
        setError(err.message || "Failed to fetch inventory.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchInventory();
  }, [filterText, initialCfpFilter, setSearchQuery]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const searchTerm = event.target.value;
    debouncedSetFilterText(searchTerm);
    setSearchQuery(searchTerm);
  };

  return (
    <div className="dark:bg-zinc-900 min-h-screen p-4">
      <input
        type="text"
        placeholder="Search inventory..."
        onChange={handleInputChange}
        className="dark:bg-zinc-800 dark:text-zinc-100 placeholder-zinc-400 w-full rounded-md py-2 px-4 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={filterText}
      />

      {isLoading && (
        <div className="flex items-center justify-center">
          <Loader2 className="animate-spin h-6 w-6 text-blue-500" />
          <span className="ml-2 dark:text-zinc-300">Loading...</span>
        </div>
      )}

      {error && <div className="text-red-500 mb-4">Error: {error}</div>}

      {!isLoading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {inventory.map((item) => (
            <div
              key={item.id}
              className="dark:bg-zinc-800 rounded-md p-4 shadow-md"
            >
              <h3 className="dark:text-zinc-100 text-lg font-semibold mb-2">
                {item.name}
              </h3>
              <p className="dark:text-zinc-400 text-sm mb-2">
                {item.description}
              </p>
              <p className="dark:text-zinc-300 text-sm">SKU: {item.sku}</p>
              <p className="dark:text-zinc-300 text-sm">
                Price: ${item.price.toFixed(2)}
              </p>
            </div>
          ))}
          {inventory.length === 0 && !isLoading && !error && (
            <div className="dark:text-zinc-400">No items found.</div>
          )}
        </div>
      )}
    </div>
  );
};

export default InventoryView;
