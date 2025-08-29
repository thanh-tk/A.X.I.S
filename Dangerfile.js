// SPDX-License-Identifier: MIT
const { danger, fail } = require('danger');

const prBody = danger.github.pr.body || '';

if (!/id:\s*[A-Z]+-\d+/i.test(prBody)) {
  fail('PR body must include `id: <TASK>`');
}

const jsonMatch = prBody.match(/```json\n([\s\S]*?)\n```/);
if (!jsonMatch) {
  fail('PR body must include Agent Output JSON block.');
} else {
  try {
    const agentOutput = JSON.parse(jsonMatch[1]);
    const declared = agentOutput.files_to_create_or_edit || [];
    const changed = [...danger.git.modified_files, ...danger.git.created_files];
    const undeclared = changed.filter(f => !declared.includes(f));
    if (undeclared.length > 0) {
      fail(`Undeclared file changes: ${undeclared.join(', ')}`);
    }
  } catch (e) {
    fail('Agent Output JSON block is not valid JSON.');
  }
}
