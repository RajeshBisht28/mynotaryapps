# Define the full registry path
$chromePolicyPath = "HKLM:\SOFTWARE\Policies\Google\Chrome"

# Create parent keys if they don't exist
if (!(Test-Path "HKLM:\SOFTWARE\Policies\Google")) {
    New-Item -Path "HKLM:\SOFTWARE\Policies" -Name "Google" -Force
}

if (!(Test-Path $chromePolicyPath)) {
    New-Item -Path "HKLM:\SOFTWARE\Policies\Google" -Name "Chrome" -Force
}

# Set the registry values to disable password manager and leak detection
Set-ItemProperty -Path $chromePolicyPath -Name "PasswordManagerEnabled" -Value 0 -Type DWord
Set-ItemProperty -Path $chromePolicyPath -Name "PasswordLeakDetectionEnabled" -Value 0 -Type DWord

Write-Output "Chrome password manager and leak detection features are now disabled."
