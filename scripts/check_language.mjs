// Evaluate only the inline language-selection script. No browser or network is used.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const examples = [
  [['zh-TW'], 'zh-hant'], [['zh-HK'], 'zh-hant'], [['zh-Hant'], 'zh-hant'],
  [['zh-Hant-CN'], 'zh-hant'], [['zh-Hans-TW'], 'zh-hant'], [['zh_HK'], 'zh-hant'],
  [['zh-CN'], 'zh-hans'], [['zh-SG'], 'zh-hans'], [['zh-MO'], 'zh-hans'],
  [['zh'], 'zh-hans'], [['ZH-cn'], 'zh-hans'], [['ja-JP'], 'ja'],
  [['ko-KR'], 'ko'], [['en-US'], 'en'], [['en-GB'], 'en'],
  [['fr-FR'], 'en'], [['fr-FR', 'ja-JP'], 'ja'], [['en-US', 'zh-TW'], 'en'],
  [['zh-Hant-HK', 'en'], 'zh-hant'], [[], 'ko'], [undefined, 'ko'],
];
const bases = [
  'https://example.test/',
  'https://example.test/whimsy-cam-site/',
  'https://example.test/whimsy-cam-site/index.html',
  new URL('../index.html', import.meta.url).href,
];
let checks = 0;
for (const base of bases) {
  for (const [languages, expected] of examples) {
    let destination;
    const context = {
      navigator: { languages, language: 'ko-KR' },
      window: { location: { href: base, replace(url) { destination = String(url); } } },
      URL,
    };
    vm.runInNewContext(script, context, { timeout: 500 });
    assert.equal(destination, new URL(`${expected}/index.html`, base).href);
    if (destination.startsWith('file:')) assert.ok(fileURLToPath(destination).endsWith(`${expected}/index.html`));
    checks++;
  }
}
console.log(`PASS: ${checks} language-selection cases, including project paths and file URLs.`);
