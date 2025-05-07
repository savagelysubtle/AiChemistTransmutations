"use strict";
const asciiAlpha = regexCheck(/[A-Za-z]/);
const asciiAlphanumeric = regexCheck(/[\dA-Za-z]/);
const asciiAtext = regexCheck(/[#-'*+\--9=?A-Z^-~]/);
function asciiControl(code) {
  return (
    // Special whitespace codes (which have negative values), C0 and Control
    // character DEL
    code !== null && (code < 32 || code === 127)
  );
}
const asciiDigit = regexCheck(/\d/);
const asciiHexDigit = regexCheck(/[\dA-Fa-f]/);
const asciiPunctuation = regexCheck(/[!-/:-@[-`{-~]/);
function markdownLineEnding(code) {
  return code !== null && code < -2;
}
function markdownLineEndingOrSpace(code) {
  return code !== null && (code < 0 || code === 32);
}
function markdownSpace(code) {
  return code === -2 || code === -1 || code === 32;
}
const unicodePunctuation = regexCheck(new RegExp("\\p{P}|\\p{S}", "u"));
const unicodeWhitespace = regexCheck(/\s/);
function regexCheck(regex) {
  return check;
  function check(code) {
    return code !== null && code > -1 && regex.test(String.fromCharCode(code));
  }
}
exports.asciiAlpha = asciiAlpha;
exports.asciiAlphanumeric = asciiAlphanumeric;
exports.asciiAtext = asciiAtext;
exports.asciiControl = asciiControl;
exports.asciiDigit = asciiDigit;
exports.asciiHexDigit = asciiHexDigit;
exports.asciiPunctuation = asciiPunctuation;
exports.markdownLineEnding = markdownLineEnding;
exports.markdownLineEndingOrSpace = markdownLineEndingOrSpace;
exports.markdownSpace = markdownSpace;
exports.unicodePunctuation = unicodePunctuation;
exports.unicodeWhitespace = unicodeWhitespace;
