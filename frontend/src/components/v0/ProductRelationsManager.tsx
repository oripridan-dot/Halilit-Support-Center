/**
 * Product Relations Manager - Interactive component for managing product relationships
 * 
 * Allows viewing, adding, editing, and removing product relationships
 */

import React, { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plus,
  X,
  Search,
  Link2,
  Unlink,
  CheckCircle,
  AlertCircle,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { useNavigationStore } from "../../store/navigationStore";

interface Relation {
  id: string;
  type: "accessory_for" | "compatible_with" | "related_to" | "alternative_to" | "variant_of";
  targetId: string;
  targetName: string;
  targetImage?: string;
  verified: boolean;
  confidence?: number;
}

interface ProductRelationsManagerProps {
  productId: string;
  relations: Relation[];
  onRelationAdd?: (targetId: string, type: string) => void;
  onRelationRemove?: (relationId: string) => void;
  onRelationVerify?: (relationId: string) => void;
}

export const ProductRelationsManager: React.FC<ProductRelationsManagerProps> = ({
  productId,
  relations,
  onRelationAdd,
  onRelationRemove,
  onRelationVerify,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const { products } = useConductorCatalog();
  const { openProductPage } = useNavigationStore();

  const relationTypeLabels: Record<string, string> = {
    accessory_for: "Accessory",
    compatible_with: "Compatible",
    related_to: "Related",
    alternative_to: "Alternative",
    variant_of: "Variant",
  };

  const relationTypeColors: Record<string, string> = {
    accessory_for: "blue",
    compatible_with: "green",
    related_to: "purple",
    alternative_to: "orange",
    variant_of: "zinc",
  };

  // Group relations by type
  const groupedRelations = useMemo(() => {
    const groups: Record<string, Relation[]> = {};
    relations.forEach((rel) => {
      if (!groups[rel.type]) {
        groups[rel.type] = [];
      }
      groups[rel.type].push(rel);
    });
    return groups;
  }, [relations]);

  // Search products for adding relations
  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const query = searchQuery.toLowerCase();
    return products
      .filter(
        (p) =>
          p.id !== productId &&
          (p.name?.toLowerCase().includes(query) ||
            p.brand?.toLowerCase().includes(query))
      )
      .slice(0, 10);
  }, [searchQuery, products, productId]);

  const totalRelations = relations.length;
  const verifiedCount = relations.filter((r) => r.verified).length;
  const needsVerification = totalRelations > 0 && verifiedCount < totalRelations;

  return (
    <>
      {/* Relations Summary Card */}
      <div className="bg-zinc-900 rounded-lg border border-zinc-800">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full p-4 flex items-center justify-between hover:bg-zinc-800/50 transition-colors"
        >
          <div className="flex items-center gap-3 flex-1 text-left">
            <div className="flex items-center gap-2">
              <Link2 className="w-4 h-4 text-zinc-400" />
              <span className="text-sm font-medium text-white">Relations</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              <span>{totalRelations} total</span>
              {needsVerification && (
                <>
                  <span>•</span>
                  <span className="text-yellow-400">
                    {totalRelations - verifiedCount} need verification
                  </span>
                </>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {needsVerification ? (
              <AlertCircle className="w-4 h-4 text-yellow-400" />
            ) : totalRelations > 0 ? (
              <CheckCircle className="w-4 h-4 text-green-400" />
            ) : null}
            {isExpanded ? (
              <ChevronUp className="w-4 h-4 text-zinc-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-zinc-400" />
            )}
          </div>
        </button>

        {/* Expanded Relations List */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="px-4 pb-4 space-y-4 border-t border-zinc-800">
                {/* Add Relation Button */}
                <button
                  onClick={() => setShowAddModal(true)}
                  className="w-full px-3 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm font-medium text-white flex items-center justify-center gap-2 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Add Relation
                </button>

                {/* Relations by Type */}
                {Object.entries(groupedRelations).map(([type, rels]) => (
                  <div key={type}>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
                        {relationTypeLabels[type]}
                      </h4>
                      <span className="text-xs text-zinc-600">{rels.length}</span>
                    </div>
                    <div className="space-y-2">
                      {rels.map((rel) => {
                        const targetProduct = products.find((p) => p.id === rel.targetId);
                        return (
                          <div
                            key={rel.id}
                            className="flex items-center gap-3 p-2 bg-zinc-800/50 rounded-lg hover:bg-zinc-800 transition-colors"
                          >
                            {targetProduct?.image_url && (
                              <img
                                src={targetProduct.image_url}
                                alt={rel.targetName}
                                className="w-10 h-10 rounded object-cover"
                              />
                            )}
                            <button
                              onClick={() => openProductPage(rel.targetId)}
                              className="flex-1 text-left min-w-0"
                            >
                              <div className="text-sm font-medium text-white truncate">
                                {rel.targetName}
                              </div>
                              {rel.confidence !== undefined && (
                                <div className="text-xs text-zinc-500">
                                  {Math.round(rel.confidence * 100)}% confidence
                                </div>
                              )}
                            </button>
                            <div className="flex items-center gap-2">
                              {rel.verified ? (
                                <CheckCircle className="w-4 h-4 text-green-400" />
                              ) : (
                                <button
                                  onClick={() => onRelationVerify?.(rel.id)}
                                  className="p-1 hover:bg-zinc-700 rounded transition-colors"
                                  title="Mark as verified"
                                >
                                  <AlertCircle className="w-4 h-4 text-yellow-400" />
                                </button>
                              )}
                              <button
                                onClick={() => onRelationRemove?.(rel.id)}
                                className="p-1 hover:bg-zinc-700 rounded transition-colors"
                                title="Remove relation"
                              >
                                <Unlink className="w-4 h-4 text-zinc-500 hover:text-red-400" />
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}

                {totalRelations === 0 && (
                  <div className="text-center py-8 text-sm text-zinc-500">
                    No relations found. Click "Add Relation" to link products.
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Add Relation Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
            onClick={() => setShowAddModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-zinc-900 rounded-xl border border-zinc-800 w-full max-w-md max-h-[80vh] flex flex-col"
            >
              <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Add Product Relation</h3>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="p-1 hover:bg-zinc-800 rounded transition-colors"
                >
                  <X className="w-5 h-5 text-zinc-400" />
                </button>
              </div>

              <div className="p-4 flex-1 overflow-y-auto">
                <div className="relative mb-4">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search products..."
                    className="w-full pl-10 pr-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                </div>

                <div className="space-y-2">
                  {searchResults.map((product) => (
                    <button
                      key={product.id}
                      onClick={() => {
                        // For now, add as "related_to" - could expand to select type
                        onRelationAdd?.(product.id, "related_to");
                        setShowAddModal(false);
                        setSearchQuery("");
                      }}
                      className="w-full p-3 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-left flex items-center gap-3 transition-colors"
                    >
                      {product.image_url && (
                        <img
                          src={product.image_url}
                          alt={product.name}
                          className="w-12 h-12 rounded object-cover"
                        />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-white truncate">
                          {product.name}
                        </div>
                        <div className="text-xs text-zinc-500">{product.brand}</div>
                      </div>
                      <Plus className="w-4 h-4 text-zinc-400" />
                    </button>
                  ))}
                  {searchQuery && searchResults.length === 0 && (
                    <div className="text-center py-8 text-sm text-zinc-500">
                      No products found matching "{searchQuery}"
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
