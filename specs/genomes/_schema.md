# Genome Spec Schema — v1.0 (Bio-Swarm Architecture)

A **Genome** is a framework-agnostic, machine-readable specification for a UI or backend cell.
It captures _what_ something must do (States, Traits) without prescribing _how_ (React, Vue, HTMX).

The Ribosome interpreter synthesizes the Genome into the current target framework.

---

## Required Fields

```yaml
id: string # Unique identifier, e.g. genome_product_explorer
version: semver # e.g. "1.0.0"
type: UI_Cell | Service_Cell | Data_Cell | Gate_Cell
fitness_goal: SCREAMING_CAPS_STRING # The north-star metric this cell optimises for
```

## Environment Block

```yaml
environment:
  - path/to/data_model.py # Files the Ribosome must read before synthesis
```

## States Block (FSM — Finite State Machine)

```yaml
States:
  STATE_NAME:
    description: Human-readable description.
    transitions: # Optional: what triggers transition to other states
      - trigger: "event description"
        next: NEXT_STATE
    visual_hint: "CSS class or description of visual feedback"
    required: true|false # If false, the Ribosome can omit this state if not relevant
```

## Traits Block (Chromosomes — heritable properties)

```yaml
Traits:
  TraitName:
    type: bool | string | enum
    value: ...
    inheritable: true|false # Can child genomes override this?
    description: ...
```

## Mutations_Allowed Block

```yaml
Mutations_Allowed:
  - PropertyName: Variable # Agent may adapt this to context
```

## Extends Block (Trait Inheritance)

```yaml
extends: genome_base_cell # Inherit all traits from parent genome
```

## Phenotype_Assertions Block (Post-synthesis verification)

```yaml
Phenotype_Assertions:
  - "Every State must map to a distinct React useState or conditional render"
  - "fitness_goal must be measurable in the rendered output"
```
