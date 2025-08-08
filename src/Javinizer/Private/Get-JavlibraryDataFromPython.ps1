function Get-JavlibraryDataFromPython {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Url
    )

    # Assuming the python script is in the parent directory of the 'Private' folder.
    $scriptPath = Resolve-Path (Join-Path $PSScriptRoot '..' 'get_javlibrary_data.py')

    try {
        # Execute the python script and capture its output.
        $jsonOutput = python3 $scriptPath $Url

        if ($jsonOutput) {
            # The output might be an array of strings, so join them.
            $jsonString = $jsonOutput -join "`n"
            $data = $jsonString | ConvertFrom-Json

            if ($data.PSObject.Properties.Name -contains 'error') {
                Write-Warning "Python script returned an error: $($data.error)"
                return $null
            }
            return $data
        } else {
            Write-Warning "Python script produced no output."
            return $null
        }
    }
    catch {
        Write-Error "Failed to execute python script or parse its output: $_"
        return $null
    }
}
