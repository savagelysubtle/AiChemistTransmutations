// This file is being updated to use mdx-bundler directly for more control
// over MDX component handling, instead of the higher-level mdx-to-md library.
import {promises as fsPromises} from 'node:fs';
import {resolve, dirname, join} from 'node:path';
// Remove the old import:
// import {mdxToMd} from 'mdx-to-md'; // The library we installed

// Add new imports for direct mdx-bundler usage:
import {bundleMDX} from 'mdx-bundler';
import {getMDXComponent} from 'mdx-bundler/client';
import React from 'react'; // Required for getMDXComponent and createElement
import {renderToStaticMarkup} from 'react-dom/server'; // To render React to HTML string
import TurndownService from 'turndown'; // To convert HTML to Markdown

/**
 * Converts an MDX file to a Markdown file using mdx-bundler directly.
 *
 * MDX is a format that lets you write JSX in your Markdown documents.
 * This function takes an MDX file, processes it to standard Markdown,
 * and saves it. It handles custom components by allowing mappings.
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
    await fsPromises.access(inputPath, fsPromises.constants.R_OK);

    // 2. Determine the output path
    const finalOutputPath =
      outputPath || inputPath.replace(/\.mdx$/i, '.md');

    // Ensure the output directory exists.
    await fsPromises.mkdir(dirname(finalOutputPath), {recursive: true});

    // 3. Ensure ESBUILD_BINARY_PATH is set for mdx-bundler
    // This logic is preserved from the original file as it's important for esbuild.
    if (!process.env.ESBUILD_BINARY_PATH) {
      try {
        const esbuildPkgPath = require.resolve('esbuild/package.json');
        const esbuildDir = dirname(esbuildPkgPath);
        const binary =
          process.platform === 'win32'
            ? join(esbuildDir, 'esbuild.exe')
            : join(esbuildDir, 'bin', 'esbuild');
        process.env.ESBUILD_BINARY_PATH = binary;
      } catch {
        // If resolution fails, we'll let mdx-bundler handle errors later.
        console.warn('Could not resolve esbuild binary path. mdx-bundler might fail.');
      }
    }

    // 4. Bundle the MDX file content using mdx-bundler
    // The `bundleMDX` function from `mdx-bundler` compiles and bundles the MDX source.
    // It can take the file path directly.
    const {code /*, frontmatter */} = await bundleMDX({
      file: resolve(inputPath), // Use the resolved absolute path
      // mdxOptions can be used here to pass remark/rehype plugins if needed
      // mdxOptions: (options, frontmatter) => {
      //   options.remarkPlugins = [...(options.remarkPlugins ?? [])];
      //   options.rehypePlugins = [...(options.rehypePlugins ?? [])];
      //   return options;
      // },
    });

    // 5. Get a React component from the bundled code
    // `getMDXComponent` takes the bundled code and returns a renderable React component.
    const Component = getMDXComponent(code);

    // 6. Define mappings for custom components.
    // This is where we handle the 'Frame' component.
    // We'll make 'Frame' render its children directly, effectively stripping the Frame tags.
    const mdxComponents: Record<string, React.ComponentType<any>> = {
      Frame: (props: {children?: React.ReactNode}) =>
        React.createElement(React.Fragment, null, props.children),
      // Add other custom component mappings here if needed.
      // For standard HTML elements that Turndown will handle, explicit mapping isn't always necessary
      // unless you want to pre-process them with React or they are used as JSX components.
    };

    // 7. Render the MDX component to an HTML string
    // We pass our custom component mappings to the MDX component.
    const reactElement = React.createElement(Component, {components: mdxComponents});
    const htmlContent = renderToStaticMarkup(reactElement);

    // 8. Convert the HTML string to Markdown using Turndown
    const turndownService = new TurndownService({
      headingStyle: 'atx', // Use '#' for headings
      codeBlockStyle: 'fenced', // Use ``` for code blocks
    });
    const markdownContent = turndownService.turndown(htmlContent);

    // 9. Write the Markdown content to the output file
    await fsPromises.writeFile(finalOutputPath, markdownContent, 'utf8');

    console.log(`Successfully converted ${inputPath} to ${finalOutputPath}`);
    return finalOutputPath;
  } catch (error) {
    console.error(`Error during MDX to MD conversion:`, error);
    throw new Error(
      `Failed to convert MDX to MD: ${(error as Error).message}`,
    );
  }
}