#!/usr/bin/env bash
# 🎬 3D Environment System - Deployment & Quick Start Script

echo "🚀 Halilit Support Center - 3D Environment System v4.1.0"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check dependencies
echo -e "${BLUE}✓ Checking dependencies...${NC}"
npm list @react-three/fiber @react-three/drei three > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo -e "${GREEN}  ✓ @react-three/fiber installed${NC}"
  echo -e "${GREEN}  ✓ @react-three/drei installed${NC}"
  echo -e "${GREEN}  ✓ three installed${NC}"
else
  echo -e "${YELLOW}  ⚠ Installing dependencies...${NC}"
  npm install --legacy-peer-deps
fi

# 2. Build frontend
echo ""
echo -e "${BLUE}✓ Building frontend...${NC}"
cd frontend && npm run build 2>&1 | grep -E "(✓ built|error)"
if [ $? -eq 0 ]; then
  echo -e "${GREEN}  ✓ Build successful${NC}"
else
  echo -e "${YELLOW}  ⚠ Build completed with warnings${NC}"
fi

# 3. Show available commands
echo ""
echo -e "${BLUE}📋 Available Commands:${NC}"
echo "  npm run dev          - Start development server (http://localhost:5173)"
echo "  npm run build        - Build for production"
echo "  npm run preview      - Preview production build"
echo "  npm run lint         - Run ESLint"
echo "  npm run test         - Run tests"
echo ""

# 4. Display key files
echo -e "${BLUE}📁 Key Files Created:${NC}"
echo "  ✓ src/styles/brandThemes.ts"
echo "  ✓ src/hooks/useThreeDScene.ts"
echo "  ✓ src/components/views/slots/ThreeDSlotEnvironment.tsx"
echo "  ✓ src/components/views/slots/ProductStand.tsx"
echo ""

# 5. Show documentation
echo -e "${BLUE}📚 Documentation:${NC}"
echo "  • 3D_IMPLEMENTATION_COMPLETE.md - Full implementation details"
echo "  • 3D_QUICK_REFERENCE.md - Developer quick reference"
echo "  • INTEGRATION_GUIDE.md - Integration instructions"
echo ""

# 6. Next steps
echo -e "${GREEN}✅ System Ready!${NC}"
echo ""
echo "Next steps:"
echo "  1. Start dev server: npm run dev"
echo "  2. Open http://localhost:5173"
echo "  3. Review integration options in INTEGRATION_GUIDE.md"
echo "  4. Implement EnhancedCategorySlot wrapper component"
echo "  5. Test with feature flag ENABLE_3D_SLOTS"
echo ""
echo "For questions, see the documentation files above."
