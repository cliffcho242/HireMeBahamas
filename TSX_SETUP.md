# TypeScript Execution with tsx

This project uses [tsx](https://tsx.is/) for running TypeScript files directly without compilation. tsx is a modern, fast TypeScript execution engine that replaces ts-node and fixes ESM issues.

## Features

- ✅ Fast TypeScript execution without pre-compilation
- ✅ Native ESM support (no more import/require issues)
- ✅ Watch mode for development
- ✅ Works with latest TypeScript features
- ✅ No additional configuration needed

## Installation

tsx is already installed as a dev dependency:

```bash
npm install
```

## Usage

### Run TypeScript files directly

```bash
# Run main.ts
npx tsx src/main.ts

# Run index.ts
npx tsx src/index.ts

# Run any TypeScript file
npx tsx path/to/your/file.ts
```

### Watch mode for development

Watch mode automatically re-runs your TypeScript file when it changes:

```bash
# Watch main.ts
npx tsx watch src/main.ts

# Watch index.ts
npx tsx watch src/index.ts
```

### Using npm scripts

The package.json includes convenient scripts:

```bash
# Run tsx with any file
npm run tsx src/main.ts

# Run in watch mode
npm run tsx:watch src/main.ts
```

## Why tsx instead of ts-node?

- **Faster**: tsx uses esbuild for near-instant execution
- **ESM Support**: Native support for ES modules, no configuration needed
- **Modern**: Built for modern TypeScript and Node.js
- **No Setup**: Works out of the box without tsconfig changes
- **Better Error Messages**: Clear, actionable error output

## Examples

### Running the database schema

```bash
npx tsx src/main.ts
```

This will load and validate the Drizzle ORM schema.

### Development with watch mode

```bash
npx tsx watch src/main.ts
```

The script will automatically reload when you make changes to TypeScript files.

## Troubleshooting

If you encounter any issues:

1. Ensure TypeScript is installed: `npm install`
2. Check tsx version: `npx tsx --version`
3. Verify TypeScript version: `npx tsc --version`

## Learn More

- [tsx Documentation](https://tsx.is/)
- [tsx GitHub Repository](https://github.com/privatenumber/tsx)
