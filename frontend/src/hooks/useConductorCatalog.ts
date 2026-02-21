import React, { useState, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { useConductorCatalog } from '@/hooks/useConductorCatalog';
import { Search } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
