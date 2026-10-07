# Windows GitHub upload

Open PowerShell in this folder:

```powershell
cd D:\path\to\retail-inventory-agent
```

Then:

```powershell
git init
git add .
git status
git commit -m "Initial release: inventory decision agent"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/retail-inventory-agent.git
git push -u origin main
```

Before `git add .`, verify that private CSV files are ignored:

```powershell
git status
```

You should not see private operational files such as `sales.csv` or `current_inventory.csv`.
