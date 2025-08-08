function Get-JavlibraryData {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true, Position = 0, ValueFromPipeline = $true, ValueFromPipelineByPropertyName = $true)]
        [String]$Url,

        [Parameter()]
        [String]$JavlibraryBaseUrl,

        [Parameter()]
        [PSObject]$Session
    )

    process {
        # The new python-based scraper handles the web request and parsing.
        $scrapedData = Get-JavlibraryDataFromPython -Url $Url

        if (-not $scrapedData) {
            Write-Warning "Failed to get data from Javlibrary using python scraper for URL: $Url"
            return $null
        }

        # The python script does not provide a release year, so we extract it from the release date.
        $releaseYear = if ($scrapedData.release_date) { ($scrapedData.release_date -split '-')[0] } else { $null }

        # The old scraper returned a custom object for rating. We replicate that structure.
        $ratingObject = if ($scrapedData.rating) {
            [PSCustomObject]@{
                Rating = $scrapedData.rating
                Votes  = $null # Votes are not available from the new scraper
            }
        } else {
            $null
        }

        # The old scraper returned a complex object for actresses. We simplify this to a list of names.
        # For compatibility, we create a list of objects with a 'Name' property.
        $actressObjects = @()
        if ($scrapedData.actresses) {
            foreach ($actressName in $scrapedData.actresses) {
                $actressObjects += [PSCustomObject]@{
                    Name = $actressName
                    # Other properties from the old scraper are not available.
                }
            }
        }

        $movieDataObject = [PSCustomObject]@{
            Source        = if ($Url -match '/ja/') { 'javlibraryja' } elseif ($Url -match '/cn/' -or $Url -match '/tw/') { 'javlibraryzh' } else { 'javlibrary' }
            Url           = $Url
            Id            = $scrapedData.id
            AjaxId        = $null # Not available from the new scraper
            Title         = $scrapedData.title
            ReleaseDate   = $scrapedData.release_date
            ReleaseYear   = $releaseYear
            Runtime       = $scrapedData.runtime
            Director      = $scrapedData.director
            Maker         = $scrapedData.maker
            Label         = $scrapedData.label
            Rating        = $ratingObject
            Actress       = if ($actressObjects.Count -gt 0) { $actressObjects } else { $null }
            Genre         = $scrapedData.genres
            CoverUrl      = $scrapedData.cover_url
            ScreenshotUrl = $null # Not available from the new scraper
        }

        Write-JVLog -Write:$script:JVLogWrite -LogPath $script:JVLogPath -WriteLevel $script:JVLogWriteLevel -Level Debug -Message "[$($MyInvocation.MyCommand.Name)] JAVLibrary data object (from Python): $($movieDataObject | ConvertTo-Json -Depth 5 -Compress)"
        Write-Output $movieDataObject
    }
}
