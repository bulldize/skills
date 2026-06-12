param(
  [switch]$SkipChecks
)

$ErrorActionPreference = "Stop"

function Write-Step($Message) {
  Write-Host "[repair-codex-plugins] $Message"
}

function Get-CodexHome {
  if ($env:CODEX_HOME -and $env:CODEX_HOME.Trim()) {
    return [System.IO.Path]::GetFullPath($env:CODEX_HOME)
  }
  return [System.IO.Path]::Combine($env:USERPROFILE, ".codex")
}

function Get-CodexPackage {
  $package = Get-AppxPackage -Name OpenAI.Codex | Sort-Object Version -Descending | Select-Object -First 1
  if (-not $package -or -not $package.InstallLocation) {
    throw "Could not find installed OpenAI.Codex package."
  }
  return $package
}

function Get-CodexCliPath($InstallLocation) {
  if ($env:CODEX_CLI_PATH -and (Test-Path -LiteralPath $env:CODEX_CLI_PATH)) {
    return $env:CODEX_CLI_PATH
  }

  $localRoot = Join-Path $env:LOCALAPPDATA "OpenAI\Codex\bin"
  if (Test-Path -LiteralPath $localRoot) {
    $localCandidate = Get-ChildItem -LiteralPath $localRoot -Recurse -Filter "codex.exe" -ErrorAction SilentlyContinue |
      Sort-Object LastWriteTime -Descending |
      Select-Object -First 1
    if ($localCandidate) {
      return $localCandidate.FullName
    }
  }

  $candidates = @(
    (Join-Path $InstallLocation "app\resources\codex.exe"),
    (Join-Path $InstallLocation "app\resources\codex")
  )
  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
      return $candidate
    }
  }

  return "codex"
}

function Copy-BundledMarketplace($SourceRoot, $CodexHome, $PackageVersion) {
  $source = Join-Path $SourceRoot "app\resources\plugins\openai-bundled"
  $manifest = Join-Path $source ".agents\plugins\marketplace.json"
  if (-not (Test-Path -LiteralPath $manifest)) {
    throw "Current Codex package does not contain a supported openai-bundled marketplace at $source"
  }

  $destParent = Join-Path $CodexHome ".tmp\bundled-marketplaces"
  $dest = Join-Path $destParent ("openai-bundled-" + $PackageVersion)
  New-Item -ItemType Directory -Force -Path $destParent | Out-Null

  $destManifest = Join-Path $dest ".agents\plugins\marketplace.json"
  if (Test-Path -LiteralPath $destManifest) {
    Write-Step "Using existing user-writable bundled marketplace: $dest"
    return $dest
  }

  if (Test-Path -LiteralPath $dest) {
    $backup = "$dest.bak-$(Get-Date -Format yyyyMMdd-HHmmss)"
    Move-Item -LiteralPath $dest -Destination $backup
    Write-Step "Backed up incomplete marketplace snapshot to $backup"
  }

  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  $robocopy = Start-Process -FilePath "robocopy.exe" -ArgumentList @(
    $source,
    $dest,
    "/E",
    "/NFL",
    "/NDL",
    "/NJH",
    "/NJS",
    "/NP",
    "/R:2",
    "/W:1"
  ) -Wait -PassThru -NoNewWindow
  if ($robocopy.ExitCode -ge 8) {
    throw "robocopy failed with exit code $($robocopy.ExitCode)"
  }
  if (-not (Test-Path -LiteralPath $destManifest)) {
    throw "Marketplace manifest was not copied to $destManifest"
  }

  Write-Step "Copied bundled marketplace to $dest"
  return $dest
}

function Update-ConfigToml($ConfigPath, $BundledPath) {
  if (-not (Test-Path -LiteralPath $ConfigPath)) {
    New-Item -ItemType File -Force -Path $ConfigPath | Out-Null
  }
  $content = Get-Content -LiteralPath $ConfigPath -Raw
  $source = "\\?\$BundledPath"
  $sourceLine = "source = '$source'"
  $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  $marketplaceBlock = @"
[marketplaces.openai-bundled]
last_updated = "$timestamp"
source_type = "local"
$sourceLine

"@

  if ($content -match '(?ms)^\[marketplaces\.openai-bundled\]\s*.*?(?=^\[|\z)') {
    $content = [regex]::Replace($content, '(?ms)^\[marketplaces\.openai-bundled\]\s*.*?(?=^\[|\z)', $marketplaceBlock)
  } else {
    $content = $content.TrimEnd() + "`r`n`r`n" + $marketplaceBlock
  }

  foreach ($plugin in @("browser", "chrome", "computer-use", "latex")) {
    $heading = "[plugins.""$plugin@openai-bundled""]"
    $block = "$heading`r`nenabled = true`r`n`r`n"
    $escaped = [regex]::Escape($heading)
    if ($content -match "(?ms)^$escaped\s*.*?(?=^\[|\z)") {
      $content = [regex]::Replace($content, "(?ms)^$escaped\s*.*?(?=^\[|\z)", $block)
    } else {
      $content = $content.TrimEnd() + "`r`n`r`n" + $block
    }
  }

  Set-Content -LiteralPath $ConfigPath -Value $content -Encoding UTF8
  Write-Step "Updated $ConfigPath"
}

function Patch-SkyExports($CodexHome) {
  $runtimeRoot = Join-Path $env:LOCALAPPDATA "OpenAI\Codex\runtimes\cua_node"
  $packages = @()
  if (Test-Path -LiteralPath $runtimeRoot) {
    $packages += Get-ChildItem -LiteralPath $runtimeRoot -Recurse -Filter "package.json" -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -like "*\node_modules\@oai\sky\package.json" }
  }

  $packages = $packages | Sort-Object FullName -Unique
  foreach ($package in $packages) {
    $packagePath = $package.FullName
    $basePath = Join-Path (Split-Path -Parent $packagePath) "dist\project\cua\sky_js\src\targets\windows\internal\computer_use_client_base.js"
    if (-not (Test-Path -LiteralPath $basePath)) {
      continue
    }

    $json = Get-Content -LiteralPath $packagePath -Raw | ConvertFrom-Json
    $exportKey = "./dist/project/cua/sky_js/src/targets/windows/internal/computer_use_client_base.js"
    if (-not $json.exports) {
      $json | Add-Member -MemberType NoteProperty -Name "exports" -Value ([pscustomobject]@{})
    }
    $existing = $json.exports.PSObject.Properties[$exportKey]
    if (-not $existing) {
      $backup = "$packagePath.bak-codex-$(Get-Date -Format yyyyMMdd-HHmmss)"
      Copy-Item -LiteralPath $packagePath -Destination $backup
      $json.exports | Add-Member -MemberType NoteProperty -Name $exportKey -Value "./dist/project/cua/sky_js/src/targets/windows/internal/computer_use_client_base.js"
      $json | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $packagePath -Encoding UTF8
      Write-Step "Patched @oai/sky export in $packagePath"
    }
  }
}

function Run-Checks($CodexCli, $BundledPath) {
  Write-Step "Plugin marketplaces:"
  & $CodexCli plugin marketplace list

  Write-Step "Bundled plugin status:"
  & $CodexCli plugin list | Select-String -Pattern 'Marketplace|openai-bundled|browser@openai-bundled|chrome@openai-bundled|computer-use@openai-bundled|latex@openai-bundled|sites@openai-bundled' -CaseSensitive:$false

  $chromeRoot = Join-Path $BundledPath "plugins\chrome"
  $extensionCheck = Join-Path $chromeRoot "scripts\check-extension-installed.js"
  $manifestCheck = Join-Path $chromeRoot "scripts\check-native-host-manifest.js"
  if (Test-Path -LiteralPath $extensionCheck) {
    Write-Step "Chrome extension installed check:"
    node $extensionCheck --json
  }
  if (Test-Path -LiteralPath $manifestCheck) {
    Write-Step "Chrome native host manifest check:"
    node $manifestCheck --json
  }
}

$codexHome = Get-CodexHome
$package = Get-CodexPackage
$installLocation = $package.InstallLocation
$version = [string]$package.Version
$codexCli = Get-CodexCliPath $installLocation

Write-Step "Detected Codex package $($package.PackageFullName)"
$bundledPath = Copy-BundledMarketplace -SourceRoot $installLocation -CodexHome $codexHome -PackageVersion $version
Update-ConfigToml -ConfigPath (Join-Path $codexHome "config.toml") -BundledPath $bundledPath
Patch-SkyExports -CodexHome $codexHome

if (-not $SkipChecks) {
  Run-Checks -CodexCli $codexCli -BundledPath $bundledPath
}

Write-Step "Done. Reopen Codex desktop if the plugin UI still shows stale state."
