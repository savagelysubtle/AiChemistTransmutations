import {promises as fsPromises} from 'node:fs';
import {resolve, dirname, join} from 'node:path';
import {mdxToMd} from 'mdx-to-md'; // The library we installed

/**
 * Converts an MDX file to a Markdown file.
 *
 * MDX is a format that lets you write JSX in your Markdown documents.
 * This function takes an MDX file, processes it to standard Markdown,
 * and saves it.
 *
 * @param inputPath The absolute path to the input MDX file.
 * @param outputPath Optional. The absolute path where the output Markdown file should be saved.
 *                   If not provided, it will be saved in the same directory as the input file,
 *                   with the same name but a '.md' extension.
 * @returns A promise that resolves to the path of the created Markdown file.
 * @throws If the input file doesn't exist or if there's an error during conversion/writing.
 */
export async function convertMdxToMd(
  inputPath: string,
  outputPath?: string,
): Promise<string> {
  try {
    // 1. Validate the input path
    // We use fsPromises.access to check if the file exists and is readable.
    // If it doesn't exist or we don't have permission, it will throw an error.
    await fsPromises.access(inputPath, fsPromises.constants.R_OK);

    // 2. Determine the output path
    // If an outputPath isn't provided, we'll create one.
    // For example, if inputPath is /path/to/file.mdx,
    // outputPath will be /path/to/file.md.
    const finalOutputPath =
      outputPath || inputPath.replace(/\.mdx$/i, '.md');

    // Ensure the output directory exists.
    // `dirname(finalOutputPath)` gets the directory part of the path.
    // `fsPromises.mkdir` with `recursive: true` creates parent directories if they don't exist.
    await fsPromises.mkdir(dirname(finalOutputPath), {recursive: true});

    // 3. Read the MDX file content
    // ---------------------------------------------------------------------
    // mdx-bundler (a transitive dependency of `mdx-to-md`) relies on the
    // `esbuild` CLI binary being available at runtime. When we bundle our
    // Electron main process with Vite/rollup that package is marked as
    // external (see vite.config.ts) which means it will be resolved from
    // `node_modules` at runtime.  However, on Windows especially, the
    // `ESBUILD_BINARY_PATH` environment variable often needs to be set so
    // the JS API can locate its companion executable.  We set it here once
    // in a cross-platform way so the library can always find the binary
    // regardless of where the app is launched from.

    if (!process.env.ESBUILD_BINARY_PATH) {
      try {
        // Resolve the installed esbuild package location (works in both
        // ESM and CJS since this file is compiled for Node/Electron).
        // The path we get is something like
        //   <project>/node_modules/esbuild/lib/main.js
        // So we walk up a couple directories to the package root.
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const esbuildPkgPath = require.resolve('esbuild/package.json');
        const esbuildDir = dirname(esbuildPkgPath);

        const binary =
          process.platform === 'win32'
            ? join(esbuildDir, 'esbuild.exe')
            : join(esbuildDir, 'bin', 'esbuild');

        process.env.ESBUILD_BINARY_PATH = binary;
      } catch {
        // If resolution fails we'll just let mdx-to-md handle errors later.
      }
    }

    // 3. Read the MDX file content
    // The mdxToMd function from the library expects the path to the MDX file.
    // It internally reads the file.

    // 4. Convert MDX content to Markdown string
    // The `mdxToMd` function takes the path to the MDX file.
    const markdownContent = await mdxToMd(resolve(inputPath));

    // 5. Write the Markdown content to the output file
    // We write the generated markdown string to our target file.
    await fsPromises.writeFile(finalOutputPath, markdownContent, 'utf8');

    console.log(`Successfully converted ${inputPath} to ${finalOutputPath}`);
    return finalOutputPath;
  } catch (error) {
    console.error(`Error during MDX to MD conversion:`, error);
    // We re-throw the error so that the caller (e.g., the Electron main process)
    // can handle it and potentially inform the user.
    throw new Error(
      `Failed to convert MDX to MD: ${(error as Error).message}`,
    );
  }
}