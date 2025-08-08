function Update-JVModule {
    [CmdletBinding()]
    param (
        # This parameter set is now for updating from a git repository.
        [Parameter(ParameterSetName = 'Update')]
        [Switch]$Update,

        # The URL should point to the raw Invoke-Update.ps1 in your forked repository.
        # e.g., https://raw.githubusercontent.com/YOUR_USERNAME/Javinizer/master/src/Javinizer/Misc/Invoke-Update.ps1
        [Parameter(ParameterSetName = 'Update')]
        [String]$UpdateUrl = 'https://raw.githubusercontent.com/YOUR_USERNAME/Javinizer/master/src/Javinizer/Misc/Invoke-Update.ps1'
    )

    process {
        # The version check against PowerShell Gallery has been removed as it's not applicable for a fork.
        # The update process now assumes you are running from a git clone of your forked repository.

        if ($Update) {
            if ($UpdateUrl -like '*YOUR_USERNAME*') {
                Write-Error "Please update the -UpdateUrl parameter in Update-JVModule.ps1 to point to your own forked repository."
                return
            }

            Write-Warning "Starting update process from your git repository."
            Write-Warning "Please make sure to close all related Javinizer settings files before continuing."
            Pause

            try {
                Invoke-Expression ((New-Object System.Net.WebClient).DownloadString($UpdateUrl))
            }
            catch {
                Write-Error "Failed to download or execute the update script from $UpdateUrl. Please check the URL and your internet connection."
                Write-Error $_
            }
        }
        else {
            Write-Host "The -UpdateModule switch is now used to update from your git repository."
            Write-Host "Please use 'Javinizer -UpdateModule -Update' to start the update process."
        }
    }
}
