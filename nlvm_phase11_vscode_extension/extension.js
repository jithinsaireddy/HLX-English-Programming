const vscode = require('vscode');
const cp = require('child_process');

function runCommand(cmd, cwd) {
  return new Promise((resolve) => {
    cp.exec(cmd, { cwd }, (err, stdout, stderr) => {
      resolve({ err, stdout, stderr });
    });
  });
}

async function activate(context) {
  const formatCmd = vscode.commands.registerCommand('english.format', async () => {
    const doc = vscode.window.activeTextEditor?.document;
    if (!doc) { return; }
    await doc.save();
    const res = await runCommand(`english-format "${doc.fileName}"`, vscode.workspace.rootPath || undefined);
    if (res.err) {
      vscode.window.showErrorMessage('Format failed');
    } else {
      await vscode.workspace.openTextDocument(doc.fileName).then(d => {
        vscode.window.showTextDocument(d);
      });
      vscode.window.showInformationMessage('Formatted');
    }
  });

  const lintCmd = vscode.commands.registerCommand('english.lint', async () => {
    const doc = vscode.window.activeTextEditor?.document;
    if (!doc) { return; }
    await doc.save();
    const res = await runCommand(`english-lint "${doc.fileName}"`, vscode.workspace.rootPath || undefined);
    if (res.err) {
      vscode.window.showErrorMessage('Lint failed');
    } else {
      if (res.stdout && res.stdout.trim().length > 0 && res.stdout.trim() !== 'No issues found.') {
        vscode.window.showWarningMessage(res.stdout);
      } else {
        vscode.window.showInformationMessage('No issues found.');
      }
    }
  });

  context.subscriptions.push(formatCmd, lintCmd);
}

function deactivate() {}

module.exports = { activate, deactivate };



