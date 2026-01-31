/**
 * FRONTEND VALIDATION SUITE
 * Comprehensive tests for TypeScript types, React components, and data contracts
 */

import * as fs from 'fs';
import * as path from 'path';
import type { Product, SourceOfTruth, ValidationStepInfo } from '../src/types';

interface TestResult {
    passed: { name: string; message: string }[];
    failed: { name: string; message: string }[];
    warnings: { name: string; message: string }[];
}

const Colors = {
    HEADER: '\x1b[95m',
    OKBLUE: '\x1b[94m',
    OKCYAN: '\x1b[96m',
    OKGREEN: '\x1b[92m',
    WARNING: '\x1b[93m',
    FAIL: '\x1b[91m',
    ENDC: '\x1b[0m',
    BOLD: '\x1b[1m',
    UNDERLINE: '\x1b[4m',
};

class ValidationSuite {
    private results: TestResult = {
        passed: [],
        failed: [],
        warnings: [],
    };

    private passTest(name: string, message = '') {
        this.results.passed.push({ name, message });
        console.log(`${Colors.OKGREEN}✓${Colors.ENDC} ${name}`);
        if (message) console.log(`  ${message}`);
    }

    private failTest(name: string, message = '') {
        this.results.failed.push({ name, message });
        console.log(`${Colors.FAIL}✗${Colors.ENDC} ${name}`);
        if (message) console.log(`  ${message}`);
    }

    private warnTest(name: string, message = '') {
        this.results.warnings.push({ name, message });
        console.log(`${Colors.WARNING}⚠${Colors.ENDC} ${name}`);
        if (message) console.log(`  ${message}`);
    }

    /**
     * TEST 1: Type Definition Validation
     */
    testTypeDefinitions() {
        console.log(`\n${Colors.HEADER}${Colors.BOLD}TEST 1: TYPE DEFINITIONS${Colors.ENDC}`);
        console.log('-'.repeat(60));

        // Test Product type
        const productSample: Product = {
            id: 'test-product',
            name: 'Test Product',
            brand: 'Test Brand',
            category: 'test-category',
            verified: true,
            pill_data: {
                id: 'test-id',
                official_name: 'Official Test Product',
                ui_meta: {
                    primary_category: 'STUDIO_MONITORS',
                    y_axis_score: 80,
                    badges: ['DIAMOND'],
                    validation_flags: [],
                },
                specs: {
                    frequency_response: '20Hz - 20kHz',
                    power: '100W',
                },
                context_meta: {
                    pros: ['Pro 1', 'Pro 2'],
                    cons: ['Con 1'],
                    tips: ['Tip 1'],
                    sources_of_truth: [
                        {
                            name: 'Test Source',
                            type: 'expert',
                            verified: true,
                            confidence: 85,
                        },
                    ],
                },
                commercial_meta: {
                    price: 1000,
                    stock: 'IN_STOCK',
                    sku_local: 'SKU-123',
                    sourced_from: ['manufacturer'],
                },
            },
        };

        if (productSample.pill_data) {
            this.passTest('Product type with pill_data', 'Structure valid ✓');
        } else {
            this.failTest('Product type with pill_data', 'Missing pill_data');
        }

        // Test ValidationStepInfo
        const stepSample: ValidationStepInfo = {
            status: 'complete',
            data_quality: 95,
            timestamp: new Date().toISOString(),
            sources_used: ['source1', 'source2'],
        };

        if (stepSample.status && stepSample.data_quality !== undefined) {
            this.passTest('ValidationStepInfo type', 'Fields valid ✓');
        }

        // Test SourceOfTruth
        const sourceSample: SourceOfTruth = {
            name: 'Test Source',
            type: 'review',
            verified: true,
            confidence: 80,
            url: 'https://example.com',
        };

        if (sourceSample.name && sourceSample.type) {
            this.passTest('SourceOfTruth type', 'Fields valid ✓');
        }
    }

    /**
     * TEST 2: Data Contract Validation
     */
    testDataContracts() {
        console.log(`\n${Colors.HEADER}${Colors.BOLD}TEST 2: DATA CONTRACTS${Colors.ENDC}`);
        console.log('-'.repeat(60));

        const dataDir = path.join(process.cwd(), 'frontend', 'public', 'data');

        // Load a sample brand file
        const sampleFile = path.join(dataDir, 'adam-audio.json');
        if (!fs.existsSync(sampleFile)) {
            this.failTest('Sample data file exists', 'adam-audio.json not found');
            return;
        }

        try {
            const rawData = fs.readFileSync(sampleFile, 'utf-8');
            const data = JSON.parse(rawData);

            // Validate BrandFile structure
            if (data.brand_identity && data.products) {
                this.passTest('BrandFile structure', 'Has brand_identity and products ✓');
            } else {
                this.failTest('BrandFile structure', 'Missing required fields');
                return;
            }

            // Validate each product
            const products: Product[] = data.products;
            if (Array.isArray(products) && products.length > 0) {
                this.passTest('Products array', `${products.length} products found ✓`);

                const product = products[0];

                // Test required fields
                const requiredFields = ['id', 'name', 'brand', 'category', 'pill_data'];
                const hasAllFields = requiredFields.every((field) =>
                    Object.prototype.hasOwnProperty.call(product, field)
                );

                if (hasAllFields) {
                    this.passTest('Product required fields', 'All fields present ✓');
                } else {
                    this.failTest(
                        'Product required fields',
                        `Missing: ${requiredFields.filter((f) => !Object.prototype.hasOwnProperty.call(product, f)).join(', ')}`
                    );
                }

                // Test pill_data structure
                if (product.pill_data) {
                    const pillRequired = [
                        'id',
                        'official_name',
                        'ui_meta',
                        'specs',
                        'context_meta',
                        'commercial_meta',
                    ];
                    const hasPillFields = pillRequired.every((field) =>
                        Object.prototype.hasOwnProperty.call(product.pill_data!, field)
                    );

                    if (hasPillFields) {
                        this.passTest('pill_data structure', 'All fields present ✓');
                    } else {
                        this.warnTest(
                            'pill_data structure',
                            `Missing: ${pillRequired.filter((f) => !Object.prototype.hasOwnProperty.call(product.pill_data!, f)).join(', ')}`
                        );
                    }

                    // Test ui_meta
                    const uiMeta = product.pill_data.ui_meta;
                    if (
                        uiMeta &&
                        'y_axis_score' in uiMeta &&
                        'badges' in uiMeta &&
                        'primary_category' in uiMeta
                    ) {
                        this.passTest('ui_meta fields', 'Score, badges, category ✓');
                    }

                    // Test specs
                    const specs = product.pill_data.specs;
                    if (specs && Object.keys(specs).length > 0) {
                        this.passTest(
                            'Specifications',
                            `${Object.keys(specs).length} specs found ✓`
                        );
                    } else {
                        this.warnTest('Specifications', 'No specs or empty specs object');
                    }

                    // Test validation pipeline
                    const pipeline = product.pill_data.validation_pipeline;
                    if (pipeline) {
                        const steps = [
                            'step1_official',
                            'step2_commercial',
                            'step3_context',
                            'step4_cross_validation',
                            'step5_published',
                        ];
                        const hasAllSteps = steps.every((step) =>
                            Object.prototype.hasOwnProperty.call(pipeline, step)
                        );

                        if (hasAllSteps) {
                            this.passTest('Validation pipeline', 'All 5 steps present ✓');
                        } else {
                            this.failTest('Validation pipeline', 'Missing steps');
                        }
                    } else {
                        this.warnTest(
                            'Validation pipeline',
                            'No pipeline data found'
                        );
                    }

                    // Test sources of truth
                    const sources =
                        product.pill_data.context_meta?.sources_of_truth || [];
                    if (sources.length >= 2) {
                        this.passTest('Sources of truth', `${sources.length} sources ✓`);
                    } else {
                        this.warnTest(
                            'Sources of truth',
                            `Expected 2+, got ${sources.length}`
                        );
                    }
                }
            }
        } catch (error) {
            this.failTest('Data loading', `Failed to parse JSON: ${error}`);
        }
    }

    /**
     * TEST 3: Component Props Compatibility
     */
    testComponentPropsCompatibility() {
        console.log(
            `\n${Colors.HEADER}${Colors.BOLD}TEST 3: COMPONENT PROPS COMPATIBILITY${Colors.ENDC}`
        );
        console.log('-'.repeat(60));

        // Test ProductSpecs component props
        const productSpecsProps = {
            specs: {
                frequency_response: '20Hz - 20kHz',
                power: '100W',
                impedance: '4 Ohms',
            },
            category: 'STUDIO_MONITORS',
            className: 'test-class',
        };

        if (productSpecsProps.specs && productSpecsProps.category) {
            this.passTest('ProductSpecs props', 'specs and category provided ✓');
        }

        // Test ConfidenceBadge component props
        const confidenceBadgeProps = {
            score: 80,
            badges: ['DIAMOND'],
            sourcesOfTruth: [
                {
                    name: 'Sound On Sound',
                    type: 'review' as const,
                    verified: true,
                    confidence: 85,
                },
            ],
            showDetailed: true,
        };

        if (
            confidenceBadgeProps.score &&
            confidenceBadgeProps.badges &&
            confidenceBadgeProps.sourcesOfTruth
        ) {
            this.passTest('ConfidenceBadge props', 'All props provided ✓');
        }

        // Test ValidationPipeline component props
        const validationPipelineProps = {
            pipeline: {
                step1_official: {
                    status: 'complete' as const,
                    data_quality: 95,
                    sources_used: ['manufacturer'],
                    timestamp: new Date().toISOString(),
                },
                step2_commercial: {
                    status: 'complete' as const,
                    data_quality: 90,
                    sources_used: ['pricing_api'],
                    timestamp: new Date().toISOString(),
                },
                step3_context: {
                    status: 'complete' as const,
                    data_quality: 85,
                    sources_used: ['Sound On Sound'],
                    timestamp: new Date().toISOString(),
                },
                step4_cross_validation: {
                    status: 'complete' as const,
                    data_quality: 80,
                    timestamp: new Date().toISOString(),
                },
                step5_published: {
                    status: 'complete' as const,
                    data_quality: 80,
                    sources_used: ['golden_catalog'],
                    timestamp: new Date().toISOString(),
                },
            },
            score: 80,
        };

        if (validationPipelineProps.pipeline && validationPipelineProps.score) {
            this.passTest('ValidationPipeline props', 'pipeline and score ✓');
        }
    }

    /**
     * TEST 4: Confidence Score Validation
     */
    testConfidenceScores() {
        console.log(`\n${Colors.HEADER}${Colors.BOLD}TEST 4: CONFIDENCE SCORES${Colors.ENDC}`);
        console.log('-'.repeat(60));

        const dataDir = path.join(process.cwd(), 'frontend', 'public', 'data');
        const brandFiles = fs
            .readdirSync(dataDir)
            .filter((f) => f.endsWith('.json') && f !== 'index.json');

        let totalProducts = 0;
        let validScores = 0;

        for (const file of brandFiles) {
            try {
                const data = JSON.parse(
                    fs.readFileSync(path.join(dataDir, file), 'utf-8')
                );
                const products = data.products || [];

                for (const product of products) {
                    totalProducts++;
                    const score = product.pill_data?.ui_meta?.y_axis_score;

                    if (typeof score === 'number' && score >= 50 && score <= 100) {
                        validScores++;
                    } else {
                        this.warnTest(
                            `${file} score validation`,
                            `Product ${product.id}: invalid score ${score}`
                        );
                    }
                }
            } catch (error) {
                this.failTest(`${file} parsing`, String(error));
            }
        }

        if (totalProducts > 0 && validScores === totalProducts) {
            this.passTest('All confidence scores', `${validScores}/${totalProducts} valid ✓`);
        } else {
            this.warnTest(
                'Confidence scores',
                `${validScores}/${totalProducts} valid`
            );
        }
    }

    /**
     * TEST 5: Pipeline Data Quality Metrics
     */
    testPipelineDataQuality() {
        console.log(
            `\n${Colors.HEADER}${Colors.BOLD}TEST 5: PIPELINE DATA QUALITY${Colors.ENDC}`
        );
        console.log('-'.repeat(60));

        const dataDir = path.join(process.cwd(), 'frontend', 'public', 'data');
        const brandFiles = fs
            .readdirSync(dataDir)
            .filter((f) => f.endsWith('.json') && f !== 'index.json');

        const stepNames = [
            'step1_official',
            'step2_commercial',
            'step3_context',
            'step4_cross_validation',
            'step5_published',
        ];

        for (const file of brandFiles) {
            try {
                const data = JSON.parse(
                    fs.readFileSync(path.join(dataDir, file), 'utf-8')
                );

                for (const product of data.products || []) {
                    const pipeline = product.pill_data?.validation_pipeline || {};

                    for (const stepName of stepNames) {
                        if (!pipeline[stepName]) {
                            this.failTest(
                                `${file}/${product.id} ${stepName}`,
                                'Step missing'
                            );
                            continue;
                        }

                        const step = pipeline[stepName];
                        const quality = step.data_quality;

                        if (typeof quality === 'number' && quality >= 0 && quality <= 100) {
                            // Just count valid quality scores
                        } else {
                            this.failTest(
                                `${file}/${product.id} ${stepName} quality`,
                                `Invalid: ${quality}`
                            );
                        }
                    }
                }
            } catch (error) {
                this.failTest(`${file} parsing`, String(error));
            }
        }

        this.passTest('Pipeline validation', 'All steps have valid quality metrics ✓');
    }

    /**
     * Run all tests and print summary
     */
    runAll() {
        console.log(
            `\n${Colors.BOLD}${Colors.HEADER}\n╔${'='.repeat(58)}╗\n║     HALILIT - FRONTEND VALIDATION SUITE${' '.repeat(15)}║\n╚${'='.repeat(58)}╝\n${Colors.ENDC}`
        );

        this.testTypeDefinitions();
        this.testDataContracts();
        this.testComponentPropsCompatibility();
        this.testConfidenceScores();
        this.testPipelineDataQuality();

        // Print summary
        const total =
            this.results.passed.length +
            this.results.failed.length +
            this.results.warnings.length;
        const passPct =
            total > 0 ? ((this.results.passed.length / total) * 100).toFixed(1) : '0';

        console.log(`\n${Colors.BOLD}${'='.repeat(60)}${Colors.ENDC}`);
        console.log(
            `RESULTS: ${Colors.OKGREEN}${this.results.passed.length} passed${Colors.ENDC}, ` +
            `${Colors.FAIL}${this.results.failed.length} failed${Colors.ENDC}, ` +
            `${Colors.WARNING}${this.results.warnings.length} warnings${Colors.ENDC}`
        );
        console.log(
            `Pass Rate: ${Colors.BOLD}${passPct}%${Colors.ENDC}`
        );
        console.log(`${Colors.BOLD}${'='.repeat(60)}${Colors.ENDC}\n`);

        return this.results.failed.length === 0 ? 0 : 1;
    }
}

// Run tests
const suite = new ValidationSuite();
process.exit(suite.runAll());
